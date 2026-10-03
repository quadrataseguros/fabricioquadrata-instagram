from pathlib import Path
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = Path(__file__).parent
RAIZ = AQUI.parent.parent
W, H = 1080, 1350
WHITE = (255, 255, 255)

FONTS = RAIZ / 'marca' / 'fonts'
FONTS.mkdir(parents=True, exist_ok=True)
for w in ('Bold', 'Medium', 'Regular'):
    p = FONTS / f'Poppins-{w}.ttf'
    if not p.exists():
        urllib.request.urlretrieve(f'https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-{w}.ttf', p)
def f(w, s): return ImageFont.truetype(str(FONTS / f'Poppins-{w}.ttf'), s)

im = Image.open(AQUI / 'slide1_base.jpg').convert('RGBA')

logo = Image.open(RAIZ / 'marca' / 'logo_quadrata.png').convert('RGBA')
logo = logo.crop(logo.getbbox())
icon = logo.crop((0, 0, logo.width, int(logo.height * 0.70)))
icon = icon.crop(icon.getbbox())

def paste(img, src, w, xy):
    s = src.resize((w, int(src.height * w / src.width)), Image.LANCZOS)
    img.alpha_composite(s, xy)

def ctext(d, y, t, font, fill):
    w = d.textlength(t, font=font)
    d.text(((W - w) / 2, y), t, font=font, fill=fill)

# tarja escura sutil embaixo, pra garantir contraste da logo + @ sobre a foto
scrim = Image.new('RGBA', (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(scrim)
for y in range(H - 170, H):
    a = int(130 * (y - (H - 170)) / 170)
    sd.line((0, y, W, y), fill=(4, 10, 24, a))
im = Image.alpha_composite(im, scrim)

icon_w = 72
paste(im, icon, icon_w, ((W - icon_w) // 2, H - 150))

d = ImageDraw.Draw(im)
ctext(d, H - 62, '@fabricioquadrata', f('Medium', 30), WHITE)

im.convert('RGB').save(AQUI / 'slide1.jpg', quality=93)
print('OK: logo + @fabricioquadrata adicionados')
