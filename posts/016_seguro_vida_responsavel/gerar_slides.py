from pathlib import Path
import random
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = Path(__file__).parent
RAIZ = AQUI.parent.parent
W, H = 1080, 1350
BLUE = (36, 138, 255); NAVY = (11, 39, 72); WHITE = (255, 255, 255); LIGHT = (234, 243, 255)

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
def lerp(c1, c2, t): return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ---------- fundo: entardecer sobre o mar, com reflexo na água (reflexão sobre a vida) ----------
HORIZON = 700
im = Image.new('RGB', (W, H), NAVY)
px = im.load()

sky_stops = [(0, (8, 18, 42)), (320, (16, 38, 78)), (560, (96, 70, 102)), (660, (214, 118, 92)), (HORIZON, (255, 188, 132))]
for y in range(HORIZON):
    for i in range(len(sky_stops) - 1):
        y0, c0 = sky_stops[i]; y1, c1 = sky_stops[i + 1]
        if y0 <= y <= y1:
            t = (y - y0) / max(1, (y1 - y0)); c = lerp(c0, c1, t); break
    for x in range(W): px[x, y] = c

water_stops = [(HORIZON, (150, 90, 80)), (900, (40, 30, 55)), (H, (6, 10, 26))]
for y in range(HORIZON, H):
    for i in range(len(water_stops) - 1):
        y0, c0 = water_stops[i]; y1, c1 = water_stops[i + 1]
        if y0 <= y <= y1:
            t = (y - y0) / max(1, (y1 - y0)); c = lerp(c0, c1, t); break
    for x in range(W): px[x, y] = c

# sol tocando o horizonte, com glow suave (blur remove o efeito de "alvo")
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
cx, cy = W // 2, HORIZON - 10
for rr, a in [(260, 8), (230, 12), (200, 16), (170, 22), (140, 32), (110, 48), (90, 68), (70, 95)]:
    gd.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(255, 214, 160, a))
glow = glow.filter(ImageFilter.GaussianBlur(22))
im = Image.alpha_composite(im.convert('RGBA'), glow).convert('RGB')

# reflexo do sol tremulando na água
refl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(refl)
random.seed(7)
for y in range(HORIZON + 6, H, 9):
    t = (y - HORIZON) / (H - HORIZON)
    width = int(170 * (1 - t) + 30)
    alpha = int(120 * (1 - t))
    jitter = random.randint(-18, 18)
    rd.rectangle((cx - width // 2 + jitter, y, cx + width // 2 + jitter, y + 5), fill=(255, 210, 160, alpha))
refl = refl.filter(ImageFilter.GaussianBlur(4))
im = Image.alpha_composite(im.convert('RGBA'), refl).convert('RGB')
d = ImageDraw.Draw(im)

# ---------- painel escuro translúcido com a frase (centro da atenção) ----------
panel = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(panel)
pd.rounded_rectangle((70, 235, W - 70, 735), radius=40, fill=(8, 20, 45, 215))
im = Image.alpha_composite(im.convert('RGBA'), panel).convert('RGB')
d = ImageDraw.Draw(im)

ctext(d, 290, 'Se não pode ser', f('Medium', 46), WHITE)
ctext(d, 355, 'ETERNO,', f('Bold', 108), WHITE)
ctext(d, 500, 'seja', f('Medium', 46), WHITE)
ctext(d, 565, 'RESPONSÁVEL.', f('Bold', 76), BLUE)

# ---------- card de venda: seguro de vida / proteção financeira familiar ----------
card = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
cd.rounded_rectangle((70, 955, W - 70, 1280), radius=40, fill=(255, 255, 255, 248))
im = Image.alpha_composite(im.convert('RGBA'), card).convert('RGB')
d = ImageDraw.Draw(im)

paste(im, icon, 85, (95, 980))
d.rounded_rectangle((205, 995, 205 + 390, 1058), radius=31, fill=LIGHT)
tw = d.textlength('SEGURO DE VIDA', font=f('Bold', 28))
d.text((205 + (390 - tw) / 2, 1012), 'SEGURO DE VIDA', font=f('Bold', 28), fill=BLUE)

ctext(d, 1082, 'Proteção financeira pra quem', f('Medium', 32), NAVY)
ctext(d, 1124, 'você mais ama, a partir de hoje.', f('Medium', 32), NAVY)

d.rounded_rectangle((170, 1176, W - 170, 1270), radius=36, fill=NAVY)
ctext(d, 1186, '(11) 98678-0000', f('Bold', 38), WHITE)
ctext(d, 1230, 'WhatsApp 24h ou chama no direct', f('Medium', 24), WHITE)

ctext(d, 1298, '@fabricioquadrata', f('Medium', 28), WHITE)

im.save(AQUI / 'slide1.jpg', quality=93)
print('OK: slide único gerado em', AQUI)
