"""F&B prospecting pipeline: Outscraper (Google Maps) -> Claude scoring + draft -> approval queue CSV.

Nothing is sent from here. The output CSV has an `aprobado` column; only rows you mark
`si` are exported by `scripts/export_approved.py` for the sending tools.

Usage:
    OUTSCRAPER_API_KEY=... ANTHROPIC_API_KEY=... \
        python scripts/prospect_pipeline.py --categories cafetería panadería --cities "San Pedro Garza García" --limit 20

Costs: Outscraper bills per place, per review and per contact lookup; Claude bills per
token (~1 call per prospect). Start with --limit 10 and --max-prospects 10.
"""
import argparse
import csv
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import List, Literal

import anthropic
from outscraper import OutscraperClient
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parent.parent
PROSPECTING = ROOT / "prospecting"

DEFAULT_CITIES = [
    "Monterrey", "San Pedro Garza García", "San Nicolás de los Garza",
    "Guadalupe", "Apodaca", "Santa Catarina", "General Escobedo",
]
DEFAULT_CATEGORIES = ["restaurante", "cafetería", "panadería", "catering", "dark kitchen"]


class Draft(BaseModel):
    model_config = ConfigDict(extra="forbid")
    canal: Literal["email", "whatsapp", "instagram", "linkedin"]
    asunto: str = Field(description="Asunto de email; vacío si el canal no es email")
    mensaje: str


class Assessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    puntaje: int = Field(description="0-100, ajuste al perfil de cliente ideal")
    es_cadena: bool
    dolores: List[str] = Field(description="Problemas operativos concretos vistos en reseñas")
    evidencia: List[str] = Field(description="Frases textuales cortas de reseñas que soportan los dolores")
    angulo: str = Field(description="Qué servicio de la oferta resuelve el dolor principal")
    dato_especifico: str = Field(description="Un detalle real del negocio (menú, propuesta, reseña) usado en el mensaje")
    riesgos: str = Field(description="Por qué podría no ser buen prospecto o qué verificar antes de contactar")
    borrador: Draft


SYSTEM_TEMPLATE = """Eres un experto en ventas B2B para el sector de alimentos y bebidas en Monterrey, Nuevo León.
Trabajas para BOGUE, asesoría gastronómica. Evalúas prospectos con datos públicos de Google Maps
y redactas el primer mensaje de contacto. Un humano revisa y aprueba cada mensaje antes de enviarlo.

<perfil_cliente_ideal>
{icp}
</perfil_cliente_ideal>

<oferta>
{oferta}
</oferta>

Cómo puntuar (0-100):
- Ajuste al perfil, dolores operativos concretos y recientes en reseñas, negocio independiente,
  y capacidad aparente de pagar (opera, tiene volumen). Una cadena o franquicia con corporativo
  puntúa como máximo 20. Sin evidencia de dolor, no pases de 50.
- No inventes datos: si algo no está en la información recibida, no lo afirmes.

Cómo redactar el mensaje:
- Dirigido al dueño o encargado; tono directo y amigable, español de México, de tú.
- Máximo 90 palabras (WhatsApp/Instagram/LinkedIn) o 120 (email).
- Menciona exactamente un detalle específico y verificable del negocio (platillo, propuesta de valor
  o tema de reseñas), dicho con tacto: nunca cites una queja de forma que avergüence al dueño.
- Conecta ese detalle con un problema concreto que BOGUE resuelve y un entregable concreto.
- Sin promesas de resultados financieros garantizados. Cierra con el llamado a la acción de la oferta.
- Email: termina con una línea para darse de baja ("Si prefieres no recibir más mensajes, responde BAJA").
- Elige el canal según los datos disponibles: email si hay correo, si no WhatsApp si hay teléfono,
  si no Instagram/LinkedIn.
"""


def build_system() -> str:
    icp = (PROSPECTING / "icp.md").read_text(encoding="utf-8")
    oferta = (PROSPECTING / "oferta.md").read_text(encoding="utf-8")
    return SYSTEM_TEMPLATE.format(icp=icp, oferta=oferta)


def search_places(client, categories, cities, limit):
    queries = [f"{cat}, {city}, Nuevo León, México" for city in cities for cat in categories]
    results = client.google_maps_search(queries, limit=limit, language="es", region="MX", drop_duplicates=True)
    places = {}
    for batch in results:
        for place in batch:
            pid = place.get("place_id")
            if pid and pid not in places:
                places[pid] = place
    return list(places.values())


def prefilter(places, min_reviews, max_reviews, max_rating):
    kept = []
    for p in places:
        status = (p.get("business_status") or "").upper()
        if status and status != "OPERATIONAL":
            continue
        reviews = p.get("reviews") or 0
        rating = p.get("rating") or 0
        if min_reviews <= reviews <= max_reviews and rating <= max_rating:
            kept.append(p)
    kept.sort(key=lambda p: (p.get("rating") or 5, -(p.get("reviews") or 0)))
    return kept


def fetch_reviews(client, places, per_place):
    ids = [p["place_id"] for p in places]
    results = client.google_maps_reviews(ids, reviews_limit=per_place, sort="newest", language="es", ignore_empty=True)
    by_id = {r.get("place_id"): r.get("reviews_data") or [] for r in results}
    for p in places:
        p["_reviews"] = [
            {"nota": r.get("review_rating"), "fecha": r.get("review_datetime_utc"), "texto": r.get("review_text")}
            for r in by_id.get(p["place_id"], [])
            if r.get("review_text")
        ]


def fetch_contacts(client, places):
    sites = [p["site"] for p in places if p.get("site")]
    if not sites:
        return
    by_domain = {}
    for r in client.emails_and_contacts(sites):
        by_domain[r.get("query")] = r
    for p in places:
        info = by_domain.get(p.get("site")) or {}
        emails = [e.get("value") for e in info.get("emails") or [] if e.get("value")]
        socials = info.get("socials") or {}
        p["_email"] = emails[0] if emails else ""
        p["_instagram"] = socials.get("instagram") or ""
        p["_linkedin"] = socials.get("linkedin") or ""


def assess(claude, system, place, model, effort):
    facts = {
        "nombre": place.get("name"),
        "categoria": place.get("category") or place.get("type"),
        "direccion": place.get("full_address"),
        "calificacion": place.get("rating"),
        "num_resenas": place.get("reviews"),
        "rango_precio": place.get("range"),
        "web": place.get("site"),
        "telefono": place.get("phone"),
        "email": place.get("_email", ""),
        "instagram": place.get("_instagram", ""),
        "descripcion": place.get("description"),
        "resenas_recientes": place.get("_reviews", []),
    }
    response = claude.beta.messages.parse(
        model=model,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": effort},
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=[{
            "role": "user",
            "content": "Evalúa este prospecto y redacta el borrador.\n\n<prospecto>\n"
            + json.dumps(facts, ensure_ascii=False, indent=1)
            + "\n</prospecto>",
        }],
        output_format=Assessment,
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"refusal: {response.stop_details}")
    return response.parsed_output


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--categories", nargs="+", default=DEFAULT_CATEGORIES)
    parser.add_argument("--cities", nargs="+", default=DEFAULT_CITIES)
    parser.add_argument("--limit", type=int, default=20, help="Places per category+city query")
    parser.add_argument("--min-reviews", type=int, default=30)
    parser.add_argument("--max-reviews", type=int, default=3000)
    parser.add_argument("--max-rating", type=float, default=4.6)
    parser.add_argument("--max-prospects", type=int, default=25, help="Cap on places sent to reviews + Claude")
    parser.add_argument("--reviews-per-place", type=int, default=15)
    parser.add_argument("--contacts", action="store_true", help="Look up emails/socials from websites (extra cost)")
    parser.add_argument("--model", default="claude-opus-5-5")
    parser.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--min-score", type=int, default=60, help="Only queue prospects at or above this score")
    parser.add_argument("--out", default=f"output/cola_aprobacion_{date.today():%Y%m%d}.csv")
    args = parser.parse_args()

    for var in ("OUTSCRAPER_API_KEY",):
        if not os.environ.get(var):
            sys.exit(f"{var} is not set (see .env.example)")

    outscraper = OutscraperClient(api_key=os.environ["OUTSCRAPER_API_KEY"])
    claude = anthropic.Anthropic()
    system = build_system()

    places = search_places(outscraper, args.categories, args.cities, args.limit)
    print(f"{len(places)} places found")
    places = prefilter(places, args.min_reviews, args.max_reviews, args.max_rating)[: args.max_prospects]
    print(f"{len(places)} places after filter")
    if not places:
        return

    fetch_reviews(outscraper, places, args.reviews_per_place)
    if args.contacts:
        fetch_contacts(outscraper, places)

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = out.with_suffix(".jsonl")
    fields = [
        "aprobado", "puntaje", "negocio", "categoria", "zona", "calificacion", "num_resenas",
        "canal", "asunto", "mensaje", "dato_especifico", "dolores", "evidencia", "angulo", "riesgos",
        "email", "telefono", "instagram", "web", "place_id", "google_maps",
    ]
    queued = 0
    with out.open("w", newline="", encoding="utf-8") as f, raw.open("w", encoding="utf-8") as rawf:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for p in places:
            try:
                a = assess(claude, system, p, args.model, args.effort)
            except (anthropic.APIError, RuntimeError) as e:
                print(f"skip {p.get('name')}: {e}", file=sys.stderr)
                continue
            rawf.write(json.dumps({"place": p, "assessment": a.model_dump()}, ensure_ascii=False, default=str) + "\n")
            if a.es_cadena or a.puntaje < args.min_score:
                continue
            writer.writerow({
                "aprobado": "",
                "puntaje": a.puntaje,
                "negocio": p.get("name"),
                "categoria": p.get("category") or p.get("type"),
                "zona": p.get("city") or p.get("borough"),
                "calificacion": p.get("rating"),
                "num_resenas": p.get("reviews"),
                "canal": a.borrador.canal,
                "asunto": a.borrador.asunto,
                "mensaje": a.borrador.mensaje,
                "dato_especifico": a.dato_especifico,
                "dolores": " | ".join(a.dolores),
                "evidencia": " | ".join(a.evidencia),
                "angulo": a.angulo,
                "riesgos": a.riesgos,
                "email": p.get("_email", ""),
                "telefono": p.get("phone"),
                "instagram": p.get("_instagram", ""),
                "web": p.get("site"),
                "place_id": p.get("place_id"),
                "google_maps": p.get("location_link"),
            })
            queued += 1
    print(f"{queued} prospects queued for approval -> {out}")
    print("Mark 'aprobado' = si on the rows to send, then run scripts/export_approved.py")


if __name__ == "__main__":
    main()
