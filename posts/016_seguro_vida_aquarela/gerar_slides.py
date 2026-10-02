from pathlib import Path
import urllib.request
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).parent
RAIZ = AQUI.parent.parent
W, H = 1080, 1350
BLUE = (36, 138, 255); NAVY = (11, 39, 72); WHITE = (255, 255, 255); LIGHT = (234, 243, 255)
CARD = (20, 55, 98)
N = 6  # total de slides

FONTS = RAIZ / 'marca' / 'fonts'
FONTS.mkdir(parents=True, exist_ok=True)
for w in ('Bold', 'Medium', 'Regular'):
    p = FONTS / f'Poppins-{w}.ttf'
    if not p.exists():
        urllib.request.urlretrieve(f'https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-{w}.ttf', p)
def f(w, s): return ImageFont.truetype(str(FONTS / f'Poppins-{w}.ttf'), s)

logo = Image.open(RAIZ / 'marca' / 'logo_quadrata.png').convert('RGBA')
logo = logo.crop(logo.getbbox())
icon = logo.crop((0, 0, logo.width, int(logo.height * 0.70)))
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
paste(im, icon, 200, ((W - 200) // 2, 150))
d.rounded_rectangle((W / 2 - 190, 440, W / 2 + 190, 510), radius=35, fill=LIGHT)
ctext(d, 450, 'SEGURO DE VIDA', f('Bold', 34), BLUE)
ctext(d, 590, 'Ninguém recebe', f('Bold', 74), NAVY)
ctext(d, 685, 'o manual do', f('Bold', 74), NAVY)
ctext(d, 780, 'futuro.', f('Bold', 74), BLUE)
ctext(d, 970, 'Arrasta pro lado que o Fabrício explica', f('Medium', 32), NAVY)
footer(d, NAVY, 0); save(im, 1)

# Slide 2 — o tempo não espera
im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
paste(im, icon, 110, (90, 100))
d.text((90, 290), 'O tempo não', font=f('Bold', 70), fill=WHITE)
d.text((90, 380), 'pede licença', font=f('Bold', 70), fill=BLUE)
d.rounded_rectangle((90, 560, W - 90, 840), radius=36, fill=CARD)
ctext(d, 610, 'Ele não espera a gente', f('Medium', 38), WHITE)
ctext(d, 670, 'terminar de se organizar,', f('Medium', 38), WHITE)
ctext(d, 730, 'juntar dinheiro ou', f('Medium', 38), WHITE)
ctext(d, 790, 'sentir que "chegou a hora".', f('Medium', 38), WHITE)
footer(d, WHITE, 1); save(im, 2)

# Slide 3 — rir ou chorar
im = Image.new('RGB', (W, H), LIGHT); d = ImageDraw.Draw(im)
d.text((90, 160), 'Tem dia que a vida', font=f('Bold', 62), fill=NAVY)
d.text((90, 245), 'faz a gente rir.', font=f('Bold', 62), fill=BLUE)
d.text((90, 420), 'Tem dia que ela', font=f('Bold', 62), fill=NAVY)
d.text((90, 505), 'pede coragem.', font=f('Bold', 62), fill=BLUE)
d.rounded_rectangle((90, 720, W - 90, 980), radius=36, fill=WHITE)
ctext(d, 770, 'Imprevisto não avisa.', f('Bold', 42), NAVY)
ctext(d, 840, 'E quem a gente ama', f('Medium', 36), (70, 90, 115))
ctext(d, 895, 'não pode ficar desprotegido', f('Medium', 36), (70, 90, 115))
ctext(d, 950, 'nesse meio tempo.', f('Medium', 36), (70, 90, 115))
footer(d, NAVY, 2); save(im, 3)

# Slide 4 — a estrada incerta
im = Image.new('RGB', (W, H), WHITE); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 18), fill=BLUE)
ctext(d, 170, 'Ninguém sabe onde', f('Bold', 56), NAVY)
ctext(d, 245, 'essa estrada vai dar', f('Bold', 56), BLUE)
items = ['Um diagnóstico inesperado', 'Um acidente no caminho', 'Uma fase sem renda', 'Uma despesa que não cabia no mês']
y = 420
for it in items:
    d.rounded_rectangle((90, y, W - 90, y + 100), radius=24, fill=LIGHT)
    d.ellipse((125, y + 34, 157, y + 66), fill=BLUE)
    d.text((190, y + 22), it, font=f('Medium', 34), fill=NAVY)
    y += 122
footer(d, NAVY, 3); save(im, 4)

# Slide 5 — o que dá pra decidir agora
im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
paste(im, icon, 110, (90, 100))
d.text((90, 280), 'Mas tem uma coisa', font=f('Bold', 58), fill=WHITE)
d.text((90, 360), 'que você decide hoje', font=f('Bold', 58), fill=BLUE)
items = ['Renda pra família seguir em pé', 'Dívidas e contas quitadas', 'Educação dos filhos garantida', 'Tranquilidade a partir de agora']
y = 540
for it in items:
    d.rounded_rectangle((90, y, W - 90, y + 100), radius=24, fill=CARD)
    d.ellipse((125, y + 34, 157, y + 66), fill=BLUE)
    d.text((190, y + 22), it, font=f('Medium', 32), fill=WHITE)
    y += 122
footer(d, WHITE, 4); save(im, 5)

# Slide 6 — CTA
im = Image.new('RGB', (W, H), BLUE); d = ImageDraw.Draw(im)
card = Image.new('RGBA', (360, 360), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
cd.rounded_rectangle((0, 0, 359, 359), radius=60, fill=WHITE)
im.paste(card, ((W - 360) // 2, 140), card); paste(im, icon, 250, ((W - 250) // 2, 195))
ctext(d, 540, 'O futuro a gente', f('Bold', 62), WHITE)
ctext(d, 615, 'não controla.', f('Bold', 62), NAVY)
ctext(d, 710, 'Mas quem a gente ama,', f('Medium', 38), WHITE)
ctext(d, 760, 'a gente protege.', f('Medium', 38), WHITE)
d.rounded_rectangle((150, 900, W - 150, 1020), radius=60, fill=NAVY)
ctext(d, 920, '(11) 98678-0000', f('Bold', 56), WHITE)
ctext(d, 1055, 'WhatsApp 24h ou chama no direct', f('Medium', 32), WHITE)
footer(d, WHITE, 5); save(im, 6)

print('OK: 6 slides gerados em', AQUI)
