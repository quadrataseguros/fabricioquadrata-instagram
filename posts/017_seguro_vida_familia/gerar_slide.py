from pathlib import Path
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = Path(__file__).parent
RAIZ = AQUI.parent.parent
W, H = 1080, 1350
BLUE = (36, 138, 255); WHITE = (255, 255, 255)
DEEP = (7, 22, 44)
LIGHT_BLUE = (110, 182, 255)

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

def ctext(d, y, t, font, fill):
    w = d.textlength(t, font=font); d.text(((W - w) / 2, y), t, font=font, fill=fill)

def soft_lines(img, lines):
    """Cada linha: (baseline_y, [(texto, fonte, cor), ...]) centralizada, com sombra desfocada."""
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    for base, segs in lines:
        x = (W - sum(ld.textlength(t, font=fo) for t, fo, _ in segs)) / 2
        for t, fo, cor in segs:
            sd.text((x, base + 4), t, font=fo, fill=(0, 0, 0, 160), anchor='ls')
            ld.text((x, base), t, font=fo, fill=cor, anchor='ls')
            x += ld.textlength(t, font=fo)
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(10)))
    return Image.alpha_composite(img, layer)

# ---------- foto: mãe e filho com o retrato do pai ----------
foto = Image.open(AQUI / 'foto_base.jpg').convert('RGB')
foto = foto.resize((W, int(foto.height * W / foto.width)), Image.LANCZOS)  # 1080 x 1341
im = Image.new('RGBA', (W, H), DEEP + (255,))
im.paste(foto, (0, 0))

# a foto do Gemini tem uma emenda em y≈895: o marinho cobre tudo a partir dali
fade = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fade)
F0, F1 = 735, 892
for y in range(F0, H):
    t = min(1, (y - F0) / (F1 - F0))
    fd.line((0, y, W, y), fill=DEEP + (int(255 * (t ** 1.3)),))
for y in range(0, 190):
    fd.line((0, y, W, y), fill=DEEP + (int(120 * (1 - y / 190) ** 1.2),))
im = Image.alpha_composite(im, fade)

# ---------- selo ----------
tag = Image.new('RGBA', (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(tag)
tf = f('Bold', 26); tlabel = 'SEGURO DE VIDA'
tw = td.textlength(tlabel, font=tf) + 64
td.rounded_rectangle(((W - tw) / 2, 56, (W + tw) / 2, 108), radius=26, fill=(7, 22, 44, 150), outline=(255, 255, 255, 130), width=2)
td.text(((W - tw) / 2 + 32, 66), tlabel, font=tf, fill=(255, 255, 255, 245))
im = Image.alpha_composite(im, tag)

# ---------- frase em duas linhas, palavras-chave em destaque ----------
med, bold = f('Medium', 46), f('Bold', 70)
im = soft_lines(im, [
    (960, [('Não pode ser ', med, (255, 255, 255, 235)), ('ETERNO,', bold, WHITE)]),
    (1052, [('então seja ', med, (255, 255, 255, 235)), ('RESPONSÁVEL.', bold, LIGHT_BLUE + (255,))]),
])

# ---------- botão do telefone ----------
bw, bh = 560, 86
bx, by = (W - bw) // 2, 1094
glow_b = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gb = ImageDraw.Draw(glow_b)
gb.rounded_rectangle((bx, by + 8, bx + bw, by + bh + 8), radius=bh // 2, fill=(36, 138, 255, 120))
im = Image.alpha_composite(im, glow_b.filter(ImageFilter.GaussianBlur(20)))
btn = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(btn)
bd.rounded_rectangle((bx, by, bx + bw, by + bh), radius=bh // 2, fill=BLUE)
pf = f('Bold', 42); phone = '(11) 98678-0000'
bd.text((W / 2, by + bh / 2), phone, font=pf, fill=WHITE, anchor='mm')
im = Image.alpha_composite(im, btn)
d = ImageDraw.Draw(im)
ctext(d, by + bh + 16, 'Fale agora e proteja quem você ama', f('Regular', 26), (225, 232, 245))

# ---------- rodapé: logo + @fabricioquadrata na mesma linha ----------
hf = f('Medium', 30); handle = '@fabricioquadrata'
iw = 44; ih = int(icon.height * iw / icon.width)
total = iw + 14 + d.textlength(handle, font=hf)
x0 = int((W - total) / 2); fy = H - 62
im.alpha_composite(icon.resize((iw, ih), Image.LANCZOS), (x0, fy - ih // 2))
d = ImageDraw.Draw(im)
d.text((x0 + iw + 14, fy), handle, font=hf, fill=WHITE, anchor='lm')

im.convert('RGB').save(AQUI / 'slide1.jpg', quality=93)
print('OK: slide gerado em', AQUI)
