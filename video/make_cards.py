import sys
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont, ImageOps
IMG,M,OUT=sys.argv[1:4]
F='/usr/share/fonts/opentype/inter/InterDisplay-'
GREEN=(90,158,50); DARK=(22,38,24); YEL=(232,214,64)
def enhance(im):
    im=ImageOps.autocontrast(im,cutoff=1)
    im=ImageEnhance.Color(im).enhance(1.25)
    im=ImageEnhance.Contrast(im).enhance(1.08)
    return im.filter(ImageFilter.UnsharpMask(radius=2,percent=120,threshold=2))
def cover(im,w,h):
    r=max(w/im.width,h/im.height); im=im.resize((int(im.width*r+.5),int(im.height*r+.5)),Image.LANCZOS)
    l=(im.width-w)//2; t=(im.height-h)//2; return im.crop((l,t,l+w,t+h))
def card(photo,kicker,title,sub,name):
    W,H=1920,1080; c=Image.new('RGB',(W,H),DARK)
    pw=1140; c.paste(cover(enhance(photo),pw,H),(0,0))
    d=ImageDraw.Draw(c); d.rectangle([pw,0,W,H],fill=GREEN)
    x=pw+70; y=300
    d.text((x,y),kicker.upper(),font=ImageFont.truetype(F+'SemiBold.otf',34),fill=YEL); y+=70
    ft=ImageFont.truetype(F+'Black.otf',78)
    for line in title.split('\n'): d.text((x,y),line,font=ft,fill='white'); y+=92
    y+=20; d.rectangle([x,y,x+90,y+8],fill=YEL); y+=40
    fs=ImageFont.truetype(F+'Medium.otf',36)
    for line in sub.split('\n'): d.text((x,y),line,font=fs,fill=(235,245,230)); y+=50
    d.text((x,H-110),'DISTRITO TAQUERO',font=ImageFont.truetype(F+'Black.otf',30),fill='white')
    c.save(f'{OUT}/{name}.png')
# historias IG: recorte sin stickers ni interfaz (coordenadas sobre 750x1334)
st=[(1,(100,470,650,1160),'La gaonera','Rib eye','Corte a la plancha\nsobre costra de queso'),
    (2,(100,380,650,960),'La gaonera','Pechuga de pollo','Al romero y ajo'),
    (3,(100,390,650,975),'Vegetariana','Rajas con elote','Poblano, elote y crema'),
    (4,(100,575,650,1160),'Vegetariana','Portobello','Estofado con hierbas'),
    (5,(100,595,650,1160),'Especialidad','Chamorro','8 horas en salsa\nde chile ancho')]
for i,box,k,t,s in st: card(Image.open(f'{IMG}/{i}.jpg').convert('RGB').crop(box),k,t,s,f'ig{i}')
card(Image.open(M+'image-3-1.jpg').convert('RGB'),'Tacos de corte','11 tacos,\n4 salsas','Papa galeana a la sal\ny cebolla a la mexicana','flat')
card(Image.open(M+'image-3-2.jpg').convert('RGB'),'Del mar','Camarón\nal ajillo','Sobre costra de queso\ny aguacate','costra')
card(Image.open(M+'image-2-1.jpg').convert('RGB'),'Combos de 4','Para compartir','Con papa galeana\ny salsas de la casa','combo')
