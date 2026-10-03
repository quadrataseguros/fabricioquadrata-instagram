from pathlib import Path
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

AQUI = Path(__file__).parent
RAIZ = AQUI.parent.parent
W, H = 1080, 1350
BLUE = (36, 138, 255); NAVY = (11, 39, 72); WHITE = (255, 255, 255)
DEEP = (7, 22, 44)

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
    s = src.resize((w, int(src.height * w / src.width)), Image.LANCZOS)
    img.alpha_composite(s, xy)
def ctext(d, y, t, font, fill):
    w = d.textlength(t, font=font); d.text(((W - w) / 2, y), t, font=font, fill=fill)
def soft_text(img, items):
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
    for y, t, font, _ in items:
        w = sd.textlength(t, font=font); sd.text(((W - w) / 2, y + 4), t, font=font, fill=(0, 0, 0, 150))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(10)))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    for y, t, font, fill in items:
        w = ld.textlength(t, font=font); ld.text(((W - w) / 2, y), t, font=font, fill=fill)
    return Image.alpha_composite(img, layer)

# ---------- foto: só a parte sem o texto antigo (faixa lateral e frases cortadas) ----------
foto = Image.open(AQUI / 'foto_base.webp').convert('RGB').crop((170, 0, 1080, 670))
foto = foto.resize((W, int(foto.height * W / foto.width)), Image.LANCZOS)
foto = ImageEnhance.Color(foto).enhance(0.85)
FH = foto.height

im = Image.new('RGBA', (W, H), DEEP + (255,))
im.paste(foto, (0, 0))

# fusão suave da foto com o marinho
fade = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fade)
F0 = 470
for y in range(F0, FH):
    t = (y - F0) / (FH - F0)
    fd.line((0, y, W, y), fill=DEEP + (int(255 * (t ** 1.4)),))
for y in range(0, 170):
    fd.line((0, y, W, y), fill=DEEP + (int(110 * (1 - y / 170)),))
im = Image.alpha_composite(im, fade)

# ---------- selo ----------
tag = Image.new('RGBA', (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(tag)
tf = f('Bold', 26); tlabel = 'SEGURO DE VIDA'
tw = td.textlength(tlabel, font=tf) + 64
td.rounded_rectangle(((W - tw) / 2, 60, (W + tw) / 2, 112), radius=26, fill=(7, 22, 44, 120), outline=(255, 255, 255, 120), width=2)
td.text(((W - tw) / 2 + 32, 70), tlabel, font=tf, fill=(255, 255, 255, 245))
im = Image.alpha_composite(im, tag)

# ---------- frase ----------
im = soft_text(im, [
    (640, 'Não pode ser', f('Medium', 44), (255, 255, 255, 235)),
    (696, 'ETERNO,', f('Bold', 108), WHITE),
    (836, 'então seja', f('Medium', 44), (255, 255, 255, 235)),
    (892, 'RESPONSÁVEL.', f('Bold', 76), (110, 182, 255, 255)),
])

# ---------- botão do telefone ----------
bw, bh = 580, 96
bx, by = (W - bw) // 2, 1030
glow_b = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gb = ImageDraw.Draw(glow_b)
gb.rounded_rectangle((bx, by + 8, bx + bw, by + bh + 8), radius=bh // 2, fill=(36, 138, 255, 120))
im = Image.alpha_composite(im, glow_b.filter(ImageFilter.GaussianBlur(20)))
btn = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(btn)
bd.rounded_rectangle((bx, by, bx + bw, by + bh), radius=bh // 2, fill=BLUE)
pf = f('Bold', 44); phone = '(11) 98678-0000'
bd.text(((W - bd.textlength(phone, font=pf)) / 2, by + 19), phone, font=pf, fill=WHITE)
im = Image.alpha_composite(im, btn)
d = ImageDraw.Draw(im)
ctext(d, by + bh + 18, 'Fale agora e proteja quem você ama', f('Regular', 26), (225, 232, 245))

# ---------- rodapé: logo + @fabricioquadrata ----------
icon_w = 60
paste(im, icon, icon_w, ((W - icon_w) // 2, H - 150))
d = ImageDraw.Draw(im)
ctext(d, H - 66, '@fabricioquadrata', f('Medium', 30), WHITE)

im.convert('RGB').save(AQUI / 'slide1.jpg', quality=93)
print('OK: slide gerado em', AQUI)
