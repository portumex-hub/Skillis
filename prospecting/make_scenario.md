# Escenarios de Make — prospección F&B con aprobación humana

Dos escenarios. El primero solo genera borradores; el segundo solo envía lo aprobado.
Ningún mensaje sale sin que la columna `aprobado` diga `si`.

## Hoja de Google Sheets "Cola de aprobación"
Columnas (mismo orden que `scripts/prospect_pipeline.py`):
`aprobado, puntaje, negocio, categoria, zona, calificacion, num_resenas, canal, asunto, mensaje,
dato_especifico, dolores, evidencia, angulo, riesgos, email, telefono, instagram, web, place_id,
google_maps, estado_envio, fecha_envio`

## Escenario 1 — Buscar y redactar (programado: lunes 7:00)
1. **Outscraper → Google Maps Search** — consulta `"{categoría}, {municipio}, Nuevo León, México"`,
   idioma `es`, región `MX`, límite 20.
2. **Filter** — `reviews` entre 30 y 3000, `rating` ≤ 4.6, `business_status` = OPERATIONAL.
3. **Google Sheets → Search Rows** por `place_id`; **Filter**: continuar solo si no existe
   (no volver a contactar al mismo negocio).
4. **Outscraper → Google Maps Reviews** — `place_id`, 15 reseñas, orden `newest`.
5. **Anthropic Claude → Create a Message** — modelo `claude-opus-5-5`, system = contenido de
   `prospecting/icp.md` + `prospecting/oferta.md` + reglas de `SYSTEM_TEMPLATE` del script;
   pedir respuesta JSON con los campos de `Assessment`.
6. **JSON → Parse JSON**.
7. **Filter** — `puntaje` ≥ 60 y `es_cadena` = false.
8. **Google Sheets → Add a Row** con `aprobado` vacío.
9. **Gmail → Send an Email a ti mismo**: "N prospectos nuevos para aprobar" + enlace a la hoja.

## Escenario 2 — Enviar lo aprobado (cada hora, 9:00–18:00 L-V)
1. **Google Sheets → Search Rows** — `aprobado` = si y `estado_envio` vacío.
2. **Router** por `canal`:
   - **email** → Instantly (*Add Lead to Campaign*) o Lemlist (*Add Lead*), con `asunto` y
     `mensaje` como variables personalizadas. La campaña controla límites diarios y calentamiento.
   - **whatsapp / instagram / linkedin** → **Gmail a ti mismo** con el mensaje listo para copiar
     (envío manual, ver abajo por qué).
3. **Google Sheets → Update a Row** — `estado_envio` = enviado/manual, `fecha_envio` = now.

## Límites que no se pueden saltar
- Instagram/Facebook: la API de mensajería de Meta solo permite responder a quien te escribió
  primero (ventana de 24 h). Mandar mensajes en frío desde Make vía API no es posible por la vía
  oficial; las herramientas que lo hacen operan contra los términos de Meta y arriesgan la cuenta.
- LinkedIn: no hay API oficial de prospección; Waalaxy/PhantomBuster violan sus términos.
  Usarlas con la cuenta personal de André arriesga restricción del perfil.
- Email: usar un dominio secundario (no el principal de BOGUE), calentarlo 2–3 semanas,
  máximo ~30–50 envíos/día por buzón, y siempre incluir opción de baja.
