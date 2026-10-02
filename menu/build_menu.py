"""Genera la carta de Divino Peccato (HTML + PDF) con precios tomados del Excel.

Precio = columna AC 'PVP final con IVA' de la hoja 'Mezcla de Ventas'.
Uso: python3 build_menu.py <ruta_excel> <ruta_logo_png>
"""
import base64
import html
import sys
from pathlib import Path

import openpyxl

XLSX, LOGO = sys.argv[1], sys.argv[2]
OUT = Path(__file__).parent

ws = openpyxl.load_workbook(XLSX, data_only=True)["Mezcla de Ventas"]
PRICES = {}
for r in range(5, ws.max_row + 1):
    name, ac = ws.cell(r, 1).value, ws.cell(r, 29).value
    if isinstance(name, str) and isinstance(ac, (int, float)):
        PRICES[name.strip().upper()] = int(round(ac))


def norm(s):
    return " ".join(s.replace("\xa0", " ").split()).upper()


PRICES = {norm(k): v for k, v in PRICES.items()}


def p(key):
    return PRICES[norm(key)]


# (nombre en carta, clave Excel, descripción, etiqueta)
ANTIPASTI = [
    ("Pane d'Aglio Gratinato", "PANE D’AGLIO GRATINATO", "Focaccia genovese, ajo, mozzarella y parmigiano gratinados, perejil", ""),
    ("Carpaccio di Salmone", "CARPACCIO DI SALMONE", "Salmón fresco laminado, limón, alcaparras, arúgula y lascas de parmigiano", ""),
    ("Carpaccio di Manzo", "CARPACCIO DI MANSO", "Filete de res laminado, arúgula, alcaparras, parmigiano y aceite de oliva extra virgen", ""),
    ("Funghi alla Siciliana", "FUNGHI SICILIANA", "Champiñones y setas salteados al ajo, vino blanco, mantequilla y parmigiano", ""),
    ("Caprese Classica", "CAPRESSE CLASSICA", "Jitomate, mozzarella fior di latte, albahaca y olio al basilico", "v"),
    ("Insalata Cesare", "INSALATA CESARE", "Lechuga romana, aderezo César de la casa, crutones de focaccia y parmigiano", ""),
    ("Insalata Peccato", "INSALATA DI PECATO", "Hojas mixtas, jitomate, huevo, mozzarella, chícharo y parmigiano", "casa"),
    ("Vellutata di Pomodoro", "VELLUTATA DI POMODORO", "Crema de jitomate asado con albahaca fresca", "v"),
]
PIZZE = [
    ("Peccato", "PIZZA PECCATO", "Pomodoro, mozzarella, salami italiano y espinaca", "casa"),
    ("Margherita", "PIZZA MARGUERITHA", "Pomodoro, mozzarella, albahaca y aceite de oliva", "v"),
    ("Quattro Formaggi", "PIZZA 4 QUESOS", "Mozzarella, gorgonzola, provolone y parmigiano", "v"),
    ("Prosciutto e Rucola", "PIZZA PROSCIUTTO E RUCOLA", "Prosciutto crudo, arúgula, parmigiano y aceite de oliva", ""),
    ("Bolognese", "PIZZA BOLOGNESA", "Pomodoro, mozzarella y ragù alla bolognese", ""),
    ("Parmigiana", "PIZZA PARMIGIANA", "Berenjena dorada, parmigiano, mozzarella y albahaca", "v"),
    ("Napoletana", "PIZZA NAPOLETANA", "Anchoas, alcaparras, aceitunas negras y orégano", ""),
    ("Regia", "PIZZA REGIA", "Chicharrón de La Rams, jalapeño y cebolla morada. Monterrey en Italia", ""),
    ("Pepperoni", "PIZZA PEPERONI", "Pomodoro, mozzarella y pepperoni", ""),
    ("Cotto e Funghi", "PIZZA JAMON Y CHAMPIÑONES", "Jamón de pierna y champiñones", ""),
]
PASTE = [
    ("Linguine Fra Diavolo", "LINGUINI FRA DIAVOLO", "Camarón, pomodoro picante, espinaca, nuez y queso feta", "picante"),
    ("Spaghetti alla Bolognese", "SPAGHETTI ALLA BOLOGNESE", "Ragù de res cocinado lentamente con vino tinto, parmigiano", ""),
    ("Spaghetti con Polpette", "SPAGHETTI CON POLPETTE", "Albóndigas de la casa en sugo al pomodoro y albahaca", ""),
    ("Spaghetti Puttanesca", "SPAGUETTI PUTANESCA", "Jitomate, aceitunas negras, anchoas, alcaparras y chile", "picante"),
    ("Penne alla Vodka", "PENNE ALLA VODKA", "Pomodoro, crema, vodka y un toque de chile", "casa"),
    ("Penne al Pesto", "PENNE AL PESTO", "Pesto genovese de albahaca y piñón, parmigiano", "v"),
    ("Fettuccine Alfredo", "FETTUCCINI ALFREDO", "Mantequilla, crema y parmigiano", "v"),
    ("Fettuccine alla Carbonara", "FETTUCCINI ALA CARBONARA", "Tocino, yema, parmigiano y pimienta negra", ""),
    ("Spaghetti Cremosi con Pollo", "SPAGHETTI CREMOSO CON POLLO Y VERDURAS", "Pollo, brócoli y zanahoria en salsa cremosa al vino blanco", ""),
    ("Lasagna alla Biancini", "LASAGNA ALLA BIANCINI", "Ragù alla bolognese, besciamella, mozzarella y parmigiano", ""),
    ("Lasagna al Pomodoro", "LASAGNA AL POMODORO", "Ragù, sugo al pomodoro, ricotta, mozzarella y albahaca", ""),
]
SECONDI = [
    ("Pollo alla Parmigiana", "POLLO ALLA PARMIGIANA", "Pechuga empanizada, pomodoro y mozzarella gratinada, con spaghetti", ""),
    ("Pollo Piccata", "POLLO PICATTA", "Pechuga en salsa de limón, alcaparras y vino blanco, con spaghetti", ""),
    ("Salmone in Salsa Rosa", "SALMONE SALSA ROSA", "Filete de salmón en salsa rosa al vino blanco, con fettuccine", ""),
    ("Filetto Rossini", "FILETTO ROSSINI", "Filete de res con salsa cremosa de setas al vino tinto, con linguine", ""),
]
DOLCI = [
    ("Tiramisù", "TIRAMISU", "Mascarpone, café espresso, soletas y cacao", "casa"),
    ("Crème Brûlée", "CRÈME BRULÈE", "Crema de vainilla con costra de azúcar quemada", ""),
    ("Flan Napolitano", "FLAN NAPOLITANO", "Clásico de la casa, cremoso y con caramelo", ""),
    ("Cheesecake ai Frutti Rossi", "CHEESECAKE", "Base de galleta y mermelada de frutos rojos", ""),
]
COCKTAILS = [
    ("Aperol Spritz", "APEROL SPRITZ", "Aperol, prosecco, soda y naranja"),
    ("Negroni Classico", "NEGRONI CLÁSICO", "Gin, Campari y vermut rosso"),
    ("Bellini di Venezia", "BELLINI DI VENEZIA", "Puré de durazno blanco y prosecco"),
    ("Garibaldi", "GARIBALDI DE LA BARRA", "Campari y jugo de naranja recién exprimido"),
    ("Carajillo Italiano", "CARAJILLO ITALIANO", "Licor 43 y espresso"),
    ("Margarita Italiana", "MARGARITA ITALIANA", "Tequila blanco, amaretto y limón"),
    ("Mojito Italiano", "MOJITO ITALIANO", "Ron blanco, limoncello, hierbabuena y limón"),
    ("Mezcal Mule", "MEZCAL MULE", "Mezcal joven, ginger beer, pepino y limón"),
    ("Paloma della Casa", "PALOMA DE LA CASA (CANTARITO STYLE)", "Tequila reposado, Fresca y limón, estilo cantarito"),
    ("Michelada della Casa", "CLAMATADA / MICHELADA DE LA CASA", "Carta Blanca, Clamato, limón y Tajín"),
]
ANALCOLICI = [
    ("Limonata al Rosmarino", "LIMONADA DE LIMÓN REAL CON ROMERO", "Limón amarillo, romero y soda"),
    ("Soda Italiana ai Frutti Rossi", "SODA ITALIANA DE FRUTOS ROJOS", "Frutos rojos, arándano y hierbabuena"),
    ("Conga San Pellegrino", "CONGA SAN PELLEGRINO", "Naranja, piña, limón y granadina"),
    ("Mule di Cetriolo", "MOCKTAIL MULE DE PEPINO & JENGIBRE", "Pepino, limón y ginger beer"),
    ("Mojito di Jamaica", "MOJITO DE JAMAICA Y ALBAHACA", "Flor de Jamaica, albahaca y soda"),
    ("Apple Ginger Sparkler", "APPLE GINGER SPARKLER", "Manzana, limón y ginger beer"),
    ("San Francisco Italiano", "SAN FRANCISCO ITALIANO", "Naranja, piña, durazno y granadina"),
    ("Clericot Virgin", "VIRGIN CLERICOT", "Uva, ginger ale y fruta fresca"),
    ("Piña Colada Virgin", "PIÑA COLADA VIRGEN", "Coco y piña natural"),
    ("Clamato Preparado", "CLAMATO PREPARADO VIRGIN", "Clamato, limón, Maggi y Tajín"),
]
VINI = [
    # (vino, región, nota, clave copa, clave botella)
    ("Bianchi", [
        ("Pinot Grigio · Fantinel Borgo Tesis", "Friuli", "Seco, cítrico, manzana verde", "COPA PINOT GRIGIO", "BOTELLA PINOT GRIGIO – FANTINEL BORGO TESIS"),
        ("Bianco Toscana · Banfi Centine", "Toscana", "Fresco, afrutado, equilibrado", None, "BOTELLA TREBBIANO / BIANCO TOSCANA – BANFI CENTINE BIANCO"),
        ("Moscato · Perla Rossa", "Piemonte", "Dulce, suave, ligeramente burbujeante", None, "BOTELLA MOSCATO – PERLA ROSSA / DECORDI MOSCATO"),
        ("Prosecco Brut · La Marca", "Veneto", "Burbuja fina, floral", None, "BOTELLA PROSECCO BRUT – LA MARCA"),
    ]),
    ("Rossi", [
        ("Chianti DOCG · Banfi Bell'Agio", "Toscana", "Sangiovese: cereza roja y especias", "COPA CHIANTI DOCG", "BOTELLA CHIANTI DOCG – BANFI BELL’AGIO / CASTELLO DI MELETO CHIANTI CLASSICO"),
        ("Lambrusco Frizzante · Riunite", "Emilia-Romagna", "Tinto burbujeante y fresco", "COPA LAMBRUSCO FRIZZANTE", "BOTELLA LAMBRUSCO FRIZZANTE – RIUNITE / DECORDI IGT"),
        ("Primitivo · Manieri", "Puglia", "Frutos negros maduros, especiado", None, "BOTELLA PRIMITIVO – MANIERI / QUOTA 29"),
        ("Nero d'Avola · Cusumano", "Sicilia", "Ciruela y mora, taninos suaves", None, "BOTELLA NERO D’AVOLA – PELLEGRINO / CUSUMANO"),
        ("Toscana Rosso · Banfi Centine", "Toscana", "Redondo y fácil de beber", None, "BOTELLA TOSCANA ROSSO – BANFI CENTINE ROSSO"),
        ("Barbera d'Asti · Fontanafredda", "Piemonte", "Fresco, frutal, buena acidez", None, "BOTELLA BARBERA D’ASTI – DEZZANI / FONTANAFREDDA"),
    ]),
]
BIRRE = [("Tecate", "CERVEZA TECATE"), ("Tecate Light", "CERVEZA TECATE LIGHT"), ("Carta Blanca", "CERVEZA CARTA BLANCA"),
         ("Indio", "CERVEZA INDIO"), ("Dos Equis Lager", "CERVEZA DOS EQUIS LAGER"), ("Dos Equis Ámbar", "CERVEZA DOS EQUIS ÁMBAR"),
         ("Bohemia Clásica", "CERVEZA BOHEMIA CLÁSICA"), ("Heineken", "CERVEZA HEINEKEN")]
BIBITE = [("Coca-Cola", "COCA-COLA"), ("Coca-Cola Sin Azúcar", "COCA-COLA SIN AZÚCAR"), ("Coca-Cola Light", "COCA-COLA LIGHT"),
          ("Sprite", "SPRITE"), ("Fanta Naranja", "FANTA NARANJA"), ("Fresca Toronja", "FRESCA TORONJA"),
          ("Sidral Mundet", "SIDRAL MUNDET"), ("Topo Chico", "TOPO CHICO")]
DISTILLATI = [("Tequila 100% agave", "TEQUILLAS"), ("Whisky", "WHSIKYS"), ("Caffè", "CAFES")]

TAGS = {
    "casa": '<span class="tag tag-casa">della casa</span>',
    "v": '<span class="tag tag-v" title="Vegetariano">v</span>',
    "picante": '<span class="tag tag-hot" title="Picante">piccante</span>',
}

e = html.escape


def dish(name, key, desc, tag=""):
    return (f'<div class="dish"><div class="dn"><span class="name">{e(name)}</span>{TAGS.get(tag, "")}'
            f'<span class="price nw">{p(key)}</span></div><div class="desc">{e(desc)}</div></div>')


def section(it, es, items, cls=""):
    body = "".join(dish(*i) for i in items)
    return f'<section class="sec {cls}"><h2>{it}</h2><div class="sub">{es}</div>{body}</section>'


def simple_list(it, es, items):
    rows = "".join(f'<div class="row"><span>{e(n)}</span><span class="price">{p(k)}</span></div>' for n, k in items)
    return f'<section class="sec"><h2>{it}</h2><div class="sub">{es}</div><div class="rows">{rows}</div></section>'


def drinks(it, es, items):
    body = "".join(
        f'<div class="dish sm"><div class="dn"><span class="name">{e(n)}</span><span class="price">{p(k)}</span></div>'
        f'<div class="desc">{e(d)}</div></div>' for n, k, d in items)
    return f'<section class="sec"><h2>{it}</h2><div class="sub">{es}</div>{body}</section>'


def wines():
    out = ['<section class="sec wine"><h2>Vini</h2><div class="sub">Etiquetas italianas</div>',
           '<div class="wine-head"><span></span><span>copa</span><span>botella</span></div>']
    for grp, items in VINI:
        out.append(f'<h4>{grp}</h4>')
        for name, reg, note, copa, bot in items:
            c = str(p(copa)) if copa else "&nbsp;"
            name, prod = name.split(" · ")
            reg = f"{reg}</span> <span class=\"prod\">{prod}"
            out.append(f'<div class="wrow"><div><span class="name">{e(name)}</span>'
                       f'<div class="meta"><span class="reg">{reg}</span></div><div class="desc">{e(note)}</div></div><span class="price">{c}</span><span class="price">{p(bot)}</span></div>')
    out.append('</section>')
    return "".join(out)


logo64 = base64.b64encode(Path(LOGO).read_bytes()).decode()

ribe = (f'<div class="dish feature"><div class="dn"><span class="name">Rib Eye alla Griglia</span></div>'
        f'<div class="desc">Rib eye Choice a la parrilla con sal de grano y romero. Elige tu pasta:</div>'
        f'<div class="opts"><span>Burro e parmigiano <b>{p("RIB EYE AL GRILL CON PASTA A LA MANTEQUILLA")}</b></span>'
        f'<span>Alfredo <b>{p("RIB EYE AL GRILL CON PASTA ALFREDO")}</b></span>'
        f'<span>Carbonara <b>{p("RIB EYE AL GRILL CON PASTA CARBONARA")}</b></span></div></div>')

secondi = section("Secondi", "Platos fuertes", SECONDI).replace("</section>", ribe + "</section>")

FOOT = ('<footer><span>Todos nuestros platos se acompañan de focaccia al romero hecha en casa.</span>'
        '<span>Precios en pesos mexicanos · IVA incluido</span></footer>')
LEGEND = ('<div class="legend">' + TAGS["casa"] + ' recomendación de la casa &nbsp;·&nbsp; ' + TAGS["v"]
          + ' vegetariano &nbsp;·&nbsp; ' + TAGS["picante"] + ' picante</div>')


def page(inner, num, mark=True):
    m = f'<img class="mark" src="data:image/png;base64,{logo64}" alt="">' if mark else ""
    return (f'<div class="page inner"><div class="awning"></div><header>{m}<span>Divino Peccato</span>'
            f'<span class="dot">·</span><span>Cucina mediterranea contemporanea</span></header>{inner}{FOOT}'
            f'<div class="pnum">{num}</div></div>')


cover = f'''<div class="page cover">
  <div class="cover-awning"></div>
  <img class="logo" src="data:image/png;base64,{logo64}" alt="Divino Peccato">
  <div class="tagline">Cucina mediterranea contemporanea</div>
  <div class="rule"><span></span><i>✦</i><span></span></div>
  <p class="motto">Mangia bene, ridi spesso, ama molto.</p>
  <div class="cover-foot">Antipasti · Pizze · Paste · Secondi · Dolci · Vini</div>
</div>'''

p2 = page(f'''<div class="cols">
  <div>{section("Antipasti", "Entradas y ensaladas", ANTIPASTI)}</div>
  <div>{section("Pizze", "Masa delgada estilo romano · 30 cm", PIZZE)}</div>
</div>{LEGEND}''', 2)

p3 = page(f'''<div class="cols">
  <div>{section("Paste", "Pasta al dente, salsas de la casa", PASTE)}</div>
  <div>{secondi}{section("Dolci", "Postres", DOLCI, "dolci")}</div>
</div>''', 3)

p4 = page(f'''<div class="cols wide">
  <div>{wines()}</div>
  <div>{drinks("Cocktails", "De la barra", COCKTAILS)}</div>
</div>''', 4)

p5 = page(f'''<div class="cols">
  <div>{drinks("Analcolici", "Sin alcohol, hechos al momento", ANALCOLICI)}</div>
  <div>{simple_list("Birre", "Cervezas", BIRRE)}{simple_list("Bibite", "Refrescos", BIBITE)}{simple_list("Distillati e Caffè", "Destilados y café", DISTILLATI)}</div>
</div>''', 5)

back = f'''<div class="page cover back">
  <div class="cover-awning"></div>
  <img class="logo sm" src="data:image/png;base64,{logo64}" alt="Divino Peccato">
  <div class="tagline">Grazie e buon appetito</div>
  <div class="rule"><span></span><i>✦</i><span></span></div>
  <p class="motto">Pregunta a tu mesero por el maridaje ideal para tu platillo.</p>
</div>'''

CSS = Path(OUT / "menu.css").read_text()
FONTS = Path(OUT / "fonts" / "fonts.css").read_text()
for fn in sorted((OUT / "fonts").glob("*.woff2")):
    b64 = base64.b64encode(fn.read_bytes()).decode()
    FONTS = FONTS.replace(f"url(fonts/{fn.name})", f"url(data:font/woff2;base64,{b64})")
CSS = FONTS + CSS
doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Divino Peccato · Menú</title>
<style>{CSS}</style></head><body>{cover}{p2}{p3}{p4}{p5}{back}</body></html>'''
(OUT / "divino_peccato_menu.html").write_text(doc)
print("ok", len(PRICES), "precios leídos")
