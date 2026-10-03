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
def ctext_shadow(d, y, t, font, fill, shadow=(0, 0, 0, 120), off=3):
    w = d.textlength(t, font=font); x = (W - w) / 2
    d.text((x, y + off), t, font=font, fill=shadow)
    d.text((x, y), t, font=font, fill=fill)
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

d = ImageDraw.Draw(im)

# ---------- texto: frase solta sobre o fundo, leve e com respiro ----------
ctext_shadow(d, 255, 'Se não pode ser', f('Medium', 44), (255, 255, 255, 235))
ctext_shadow(d, 318, 'ETERNO,', f('Bold', 104), WHITE)
ctext_shadow(d, 462, 'seja', f('Medium', 44), (255, 255, 255, 235))
ctext_shadow(d, 525, 'RESPONSÁVEL.', f('Bold', 74), (96, 174, 255, 255))

# ---------- botão do telefone: elemento próprio, separado da frase ----------
pill_w, pill_h = 560, 108
px0, py0 = (W - pill_w) // 2, 760
pill = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(pill)
pd.rounded_rectangle((px0, py0, px0 + pill_w, py0 + pill_h), radius=pill_h // 2, fill=(8, 20, 42, 150))
pd.rounded_rectangle((px0, py0, px0 + pill_w, py0 + pill_h), radius=pill_h // 2, outline=(255, 255, 255, 90), width=2)
im = Image.alpha_composite(im, pill)
d = ImageDraw.Draw(im)
dot_r = 7
d.ellipse((px0 + 46, py0 + pill_h // 2 - dot_r, px0 + 46 + dot_r * 2, py0 + pill_h // 2 + dot_r), fill=BLUE)
phone = '(11) 98678-0000'
pf = f('Bold', 42)
tw = d.textlength(phone, font=pf)
d.text((px0 + 46 + dot_r * 2 + 24, py0 + (pill_h - 50) // 2), phone, font=pf, fill=WHITE)

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
