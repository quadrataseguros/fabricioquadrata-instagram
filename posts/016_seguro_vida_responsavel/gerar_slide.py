from pathlib import Path
import math
import random
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = Path(__file__).parent
RAIZ = AQUI.parent.parent
W, H = 1080, 1350
BLUE = (36, 138, 255); NAVY = (11, 39, 72); WHITE = (255, 255, 255)

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
def lerp(c1, c2, t): return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ---------- fundo: entardecer suave sobre o mar ----------
HORIZON = 740
base = Image.new('RGB', (W, H), NAVY)
px = base.load()
sky_stops = [(0, (8, 16, 38)), (300, (17, 36, 74)), (540, (86, 66, 96)), (660, (198, 112, 92)), (HORIZON, (255, 196, 148))]
for y in range(HORIZON):
    for i in range(len(sky_stops) - 1):
        y0, c0 = sky_stops[i]; y1, c1 = sky_stops[i + 1]
        if y0 <= y <= y1:
            t = (y - y0) / max(1, (y1 - y0)); c = lerp(c0, c1, t); break
    for x in range(W): px[x, y] = c
water_stops = [(HORIZON, (160, 100, 88)), (980, (36, 30, 54)), (H, (5, 9, 22))]
for y in range(HORIZON, H):
    for i in range(len(water_stops) - 1):
        y0, c0 = water_stops[i]; y1, c1 = water_stops[i + 1]
        if y0 <= y <= y1:
            t = (y - y0) / max(1, (y1 - y0)); c = lerp(c0, c1, t); break
    for x in range(W): px[x, y] = c
im = base.convert('RGBA')

# sol tocando o horizonte
cx, cy = W // 2, HORIZON - 8
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
for rr, a in [(300, 6), (250, 10), (210, 14), (175, 20), (145, 30), (115, 46), (90, 66), (68, 95)]:
    gd.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(255, 220, 172, a))
glow = glow.filter(ImageFilter.GaussianBlur(24))
im = Image.alpha_composite(im, glow)

# raios suaves, pra dar sensação de movimento saindo do sol
rays = Image.new('RGBA', (W, H), (0, 0, 0, 0)); rdw = ImageDraw.Draw(rays)
random.seed(3)
for i in range(14):
    ang = math.radians(200 + i * (140 / 13) + random.uniform(-3, 3))
    length = random.uniform(260, 430)
    width = random.uniform(2, 5)
    x2 = cx + length * math.cos(ang); y2 = cy + length * math.sin(ang)
    alpha = random.randint(14, 30)
    rdw.line((cx, cy, x2, y2), fill=(255, 224, 182, alpha), width=int(width))
rays = rays.filter(ImageFilter.GaussianBlur(6))
im = Image.alpha_composite(im, rays)

# reflexo tremulando na água (listras com leve variação orgânica)
refl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(refl)
random.seed(11)
for y in range(HORIZON + 6, H, 8):
    t = (y - HORIZON) / (H - HORIZON)
    width = int(130 * (1 - t) + 18)
    alpha = int(70 * (1 - t))
    jitter = int(10 * math.sin(y * 0.09) + random.randint(-7, 7))
    rd.rectangle((cx - width // 2 + jitter, y, cx + width // 2 + jitter, y + 4), fill=(255, 214, 170, alpha))
refl = refl.filter(ImageFilter.GaussianBlur(9))
im = Image.alpha_composite(im, refl)

# ---------- texto com sombra desfocada (acabamento suave) ----------
def soft_text(img, items):
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
    for y, t, font, _ in items:
        w = sd.textlength(t, font=font); sd.text(((W - w) / 2, y + 4), t, font=font, fill=(0, 0, 0, 150))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(10)))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    for y, t, font, fill in items:
        w = ld.textlength(t, font=font); ld.text(((W - w) / 2, y), t, font=font, fill=fill)
    return Image.alpha_composite(img, layer)

# selo de contexto
tag = Image.new('RGBA', (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(tag)
tf = f('Bold', 26); tlabel = 'SEGURO DE VIDA'
tw = td.textlength(tlabel, font=tf) + 64
td.rounded_rectangle(((W - tw) / 2, 168, (W + tw) / 2, 220), radius=26, fill=(255, 255, 255, 34), outline=(255, 255, 255, 110), width=2)
td.text(((W - tw) / 2 + 32, 178), tlabel, font=tf, fill=(255, 255, 255, 240))
im = Image.alpha_composite(im, tag)

im = soft_text(im, [
    (262, 'Não pode ser', f('Medium', 46), (255, 255, 255, 235)),
    (322, 'ETERNO,', f('Bold', 112), WHITE),
    (472, 'então seja', f('Medium', 46), (255, 255, 255, 235)),
    (534, 'RESPONSÁVEL.', f('Bold', 78), (110, 182, 255, 255)),
])

# chamada de venda
im = soft_text(im, [
    (800, 'Fale agora com nossa equipe', f('Medium', 36), WHITE),
    (848, 'e proteja você e sua família.', f('Medium', 36), WHITE),
])

# botão do telefone (azul sólido da marca, com brilho suave)
bw, bh = 600, 104
bx, by = (W - bw) // 2, 930
glow_b = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gb = ImageDraw.Draw(glow_b)
gb.rounded_rectangle((bx, by + 8, bx + bw, by + bh + 8), radius=bh // 2, fill=(36, 138, 255, 140))
im = Image.alpha_composite(im, glow_b.filter(ImageFilter.GaussianBlur(22)))
btn = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(btn)
bd.rounded_rectangle((bx, by, bx + bw, by + bh), radius=bh // 2, fill=BLUE)
pf = f('Bold', 46); phone = '(11) 98678-0000'
pw = bd.textlength(phone, font=pf)
bd.text(((W - pw) / 2, by + 22), phone, font=pf, fill=WHITE)
im = Image.alpha_composite(im, btn)
d = ImageDraw.Draw(im)
ctext(d, by + bh + 22, 'Atendimento 24h pelo WhatsApp', f('Regular', 26), (225, 232, 245))

# ---------- rodapé: logo + @fabricioquadrata ----------
scrim = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(scrim)
for y in range(H - 190, H):
    a = int(140 * (y - (H - 190)) / 190)
    sd.line((0, y, W, y), fill=(4, 10, 24, a))
im = Image.alpha_composite(im, scrim)

icon_w = 70
paste(im, icon, icon_w, ((W - icon_w) // 2, H - 158))
d = ImageDraw.Draw(im)
ctext(d, H - 64, '@fabricioquadrata', f('Medium', 30), WHITE)

im.convert('RGB').save(AQUI / 'slide1.jpg', quality=93)
print('OK: slide gerado em', AQUI)
