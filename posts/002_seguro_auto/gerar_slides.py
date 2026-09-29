from pathlib import Path
import urllib.request
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).parent
RAIZ = AQUI.parent.parent
W, H = 1080, 1350
BLUE = (36, 138, 255); NAVY = (11, 39, 72); WHITE = (255, 255, 255); LIGHT = (234, 243, 255)
CARD = (20, 55, 98)
N = 5  # total de slides

# Poppins: baixa do Google Fonts na primeira vez
FONTS = RAIZ / 'marca' / 'fonts'
FONTS.mkdir(parents=True, exist_ok=True)
for w in ('Bold', 'Medium', 'Regular'):
    p = FONTS / f'Poppins-{w}.ttf'
    if not p.exists():
        urllib.request.urlretrieve(f'https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-{w}.ttf', p)
def f(w, s): return ImageFont.truetype(str(FONTS / f'Poppins-{w}.ttf'), s)

logo = Image.open(RAIZ / 'marca' / 'logo_quadrata.png').convert('RGBA')
logo = logo.crop(logo.getbbox())
icon = logo.crop((0, 0, logo.width, int(logo.height * 0.70)))  # só o símbolo
icon = icon.crop(icon.getbbox())

def paste(img, src, w, xy):
    s = src.resize((w, int(src.height * w / src.width)), Image.LANCZOS); img.paste(s, xy, s); return s.size
def ctext(d, y, t, font, fill):
    w = d.textlength(t, font=font); d.text(((W - w) / 2, y), t, font=font, fill=fill)
def footer(d, fill, active):
    ctext(d, H - 95, '@fabricioquadrata', f('Medium', 30), fill)
    x0 = W / 2 - (N * 28) / 2
    for i in range(N):
        c = fill if i == active else (fill[0] // 2 + 60, fill[1] // 2 + 60, fill[2] // 2 + 60)
        d.ellipse((x0 + i * 28, H - 135, x0 + i * 28 + 12, H - 123), fill=c)
def save(im, n): im.save(AQUI / f'slide{n}.jpg', quality=92)

# Slide 1 — capa
im = Image.new('RGB', (W, H), WHITE); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 18), fill=BLUE)
paste(im, icon, 200, ((W - 200) // 2, 170))
d.rounded_rectangle((W / 2 - 170, 470, W / 2 + 170, 540), radius=35, fill=LIGHT)
ctext(d, 480, 'SEGURO AUTO', f('Bold', 36), BLUE)
ctext(d, 610, 'Seu carro está', f('Bold', 80), NAVY)
ctext(d, 710, 'protegido', f('Bold', 80), NAVY)
ctext(d, 810, 'de verdade?', f('Bold', 80), BLUE)
ctext(d, 960, 'Arrasta pro lado que o Fabrício explica', f('Medium', 34), NAVY)
footer(d, NAVY, 0); save(im, 1)

# Slide 2 — coberturas
im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
paste(im, icon, 110, (90, 100))
d.text((90, 260), 'O que o seguro', font=f('Bold', 70), fill=WHITE)
d.text((90, 350), 'auto pode cobrir', font=f('Bold', 70), fill=BLUE)
items = ['Batida e colisão', 'Roubo e furto', 'Danos a outros carros', 'Incêndio e alagamento', 'Guincho e chaveiro 24h']
y = 500
for it in items:
    d.rounded_rectangle((90, y, W - 90, y + 100), radius=24, fill=CARD)
    d.ellipse((125, y + 34, 157, y + 66), fill=BLUE)
    d.text((190, y + 22), it, font=f('Medium', 38), fill=WHITE)
    y += 122
d.text((90, y + 12), 'As coberturas mudam de apólice pra apólice.', font=f('Regular', 30), fill=(170, 195, 225))
footer(d, WHITE, 1); save(im, 2)

# Slide 3 — bateu o carro?
im = Image.new('RGB', (W, H), LIGHT); d = ImageDraw.Draw(im)
d.text((90, 150), 'Bateu o carro?', font=f('Bold', 76), fill=NAVY)
d.text((90, 245), 'Faça assim:', font=f('Bold', 76), fill=BLUE)
steps = [('Respira e sinaliza', 'Pisca-alerta e triângulo na via.'),
         ('Fotografa tudo', 'Carros, placas e o local.'),
         ('Anota os dados', 'Nome, CNH e telefone do outro.'),
         ('Chama o Fabrício', 'Ele orienta o próximo passo.')]
y = 420
for i, (t, s) in enumerate(steps, 1):
    d.rounded_rectangle((90, y, W - 90, y + 150), radius=28, fill=WHITE)
    d.ellipse((125, y + 40, 195, y + 110), fill=BLUE if i < 4 else NAVY)
    ctn = str(i); fw = d.textlength(ctn, font=f('Bold', 40))
    d.text((160 - fw / 2, y + 47), ctn, font=f('Bold', 40), fill=WHITE)
    d.text((230, y + 25), t, font=f('Bold', 40), fill=NAVY)
    d.text((230, y + 82), s, font=f('Regular', 32), fill=(70, 90, 115))
    y += 172
footer(d, NAVY, 2); save(im, 3)

# Slide 4 — renovação
im = Image.new('RGB', (W, H), WHITE); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 18), fill=BLUE)
ctext(d, 220, 'Atenção', f('Bold', 44), BLUE)
ctext(d, 300, 'Seguro vencido', f('Bold', 84), NAVY)
ctext(d, 400, '= carro sem', f('Bold', 84), NAVY)
ctext(d, 500, 'proteção', f('Bold', 84), BLUE)
d.rounded_rectangle((90, 700, W - 90, 980), radius=36, fill=LIGHT)
ctext(d, 745, 'O Fabrício confere a data', f('Medium', 40), NAVY)
ctext(d, 805, 'da sua renovação e busca', f('Medium', 40), NAVY)
ctext(d, 865, 'a melhor condição pra você.', f('Medium', 40), NAVY)
footer(d, NAVY, 3); save(im, 4)

# Slide 5 — CTA
im = Image.new('RGB', (W, H), BLUE); d = ImageDraw.Draw(im)
card = Image.new('RGBA', (360, 360), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
cd.rounded_rectangle((0, 0, 359, 359), radius=60, fill=WHITE)
im.paste(card, ((W - 360) // 2, 170), card); paste(im, icon, 250, ((W - 250) // 2, 225))
ctext(d, 590, 'Cota seu seguro', f('Bold', 76), WHITE)
ctext(d, 685, 'auto agora', f('Bold', 76), NAVY)
ctext(d, 835, 'WhatsApp 24 horas', f('Medium', 38), WHITE)
d.rounded_rectangle((150, 895, W - 150, 1015), radius=60, fill=NAVY)
ctext(d, 915, '(11) 98678-0000', f('Bold', 56), WHITE)
ctext(d, 1050, 'ou chama no direct', f('Medium', 36), WHITE)
footer(d, WHITE, 4); save(im, 5)

print('OK: 5 slides gerados em', AQUI)
