"""
adaptar_sugestoes.py — transforma as artes de posts/SUGESTÃO em posts prontos.
Para cada arte: troca o telefone antigo pelo WhatsApp 24h, ajusta para 1080x1350,
aplica um leve realce de nitidez e cria um 2º slide de chamada do Fabrício.
Uso: python scripts/adaptar_sugestoes.py
"""
from pathlib import Path
import shutil, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

RAIZ = Path(__file__).resolve().parent.parent
SUG = RAIZ / 'posts' / 'SUGESTÃO'
W, H = 1080, 1350
BLUE = (36, 138, 255); NAVY = (11, 39, 72); WHITE = (255, 255, 255); CARD = (20, 55, 98)
FONE = '(11) 98678-0000'

FONTS = RAIZ / 'marca' / 'fonts'
FONTS.mkdir(parents=True, exist_ok=True)
for w in ('Bold', 'Medium', 'Regular'):
    p = FONTS / f'Poppins-{w}.ttf'
    if not p.exists():
        urllib.request.urlretrieve(f'https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-{w}.ttf', p)
def f(w, s): return ImageFont.truetype(str(FONTS / f'Poppins-{w}.ttf'), s)

logo = Image.open(RAIZ / 'marca' / 'logo_quadrata.png').convert('RGBA')
logo = logo.crop(logo.getbbox())
icon = logo.crop((0, 0, logo.width, int(logo.height * 0.70))); icon = icon.crop(icon.getbbox())


def patch(im, box):
    """Apaga um trecho pintando cada linha com a transição entre as cores das bordas."""
    x0, y0, x1, y1 = box
    px = im.load()
    for y in range(y0, y1):
        l = [px[x, y] for x in range(x0 - 4, x0)]
        r = [px[x, y] for x in range(x1, x1 + 4)]
        cl = [sum(c[i] for c in l) / 4 for i in range(3)]
        cr = [sum(c[i] for c in r) / 4 for i in range(3)]
        for x in range(x0, x1):
            t = (x - x0) / (x1 - x0)
            px[x, y] = tuple(int(cl[i] * (1 - t) + cr[i] * t) for i in range(3))
    reg = im.crop(box).filter(ImageFilter.GaussianBlur(2))
    im.paste(reg, box[:2])


def ctext(d, y, t, font, fill):
    w = d.textlength(t, font=font); d.text(((W - w) / 2, y), t, font=font, fill=fill)


def para_feed(im, y0, y1):
    """Encaixa arte 9:16 em 1080x1350: fundo desfocado + faixa de contato no rodapé."""
    area_h = 1240
    arte = im.crop((0, y0, im.width, y1))
    s = area_h / arte.height
    arte = arte.resize((int(arte.width * s), area_h), Image.LANCZOS)
    fundo = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)
    top = (fundo.height - area_h) // 2
    fundo = fundo.crop((0, top, W, top + area_h)).filter(ImageFilter.GaussianBlur(40))
    fundo = ImageEnhance.Brightness(fundo).enhance(0.75)
    out = Image.new('RGB', (W, H), NAVY)
    out.paste(fundo, (0, 0))
    sombra = Image.new('RGBA', (arte.width + 40, area_h), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rectangle((20, 0, arte.width + 20, area_h), fill=(0, 0, 0, 110))
    sombra = sombra.filter(ImageFilter.GaussianBlur(14))
    x = (W - arte.width) // 2
    out.paste(sombra, (x - 20, 0), sombra)
    out.paste(arte, (x, 0))
    d = ImageDraw.Draw(out)
    d.rectangle((0, area_h, W, H), fill=NAVY)
    d.rectangle((0, area_h, W, area_h + 5), fill=BLUE)
    ctext(d, area_h + 16, f'WhatsApp 24h  {FONE}', f('Bold', 40), WHITE)
    ctext(d, area_h + 68, '@fabricioquadrata', f('Medium', 26), (150, 195, 255))
    return out


def slide_cta(t1, t2, itens):
    im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
    card = Image.new('RGBA', (170, 170), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, 169, 169), radius=36, fill=WHITE)
    im.paste(card, ((W - 170) // 2, 100), card)
    s = icon.resize((120, int(icon.height * 120 / icon.width)), Image.LANCZOS)
    im.paste(s, ((W - 120) // 2, 100 + (170 - s.height) // 2), s)
    ctext(d, 315, t1, f('Bold', 66), WHITE)
    ctext(d, 400, t2, f('Bold', 66), BLUE)
    y = 555
    for it in itens:
        d.rounded_rectangle((110, y, W - 110, y + 100), radius=24, fill=CARD)
        d.ellipse((145, y + 34, 177, y + 66), fill=BLUE)
        d.text((205, y + 24), it, font=f('Medium', 34), fill=WHITE)
        y += 120
    ctext(d, 940, 'Fale com o Fabrício pelo WhatsApp', f('Medium', 34), WHITE)
    d.rounded_rectangle((170, 1000, W - 170, 1110), radius=55, fill=BLUE)
    ctext(d, 1020, FONE, f('Bold', 54), WHITE)
    ctext(d, 1130, 'Atendimento 24h · ou chama no direct', f('Medium', 30), (150, 195, 255))
    x0 = W / 2 - 28
    for i in range(2):
        d.ellipse((x0 + i * 28, H - 135, x0 + i * 28 + 12, H - 123), fill=WHITE if i == 1 else (65, 80, 100))
    ctext(d, H - 95, '@fabricioquadrata', f('Medium', 30), WHITE)
    return im


# ---------- Ajustes de cada arte ----------
def arte1(im):   # Assistência familiar
    patch(im, (212, 1478, 525, 1592)); d = ImageDraw.Draw(im)
    d.text((225, 1486), 'Fale com a gente 24h', font=f('Regular', 23), fill=WHITE)
    d.text((225, 1514), 'pelo WhatsApp', font=f('Regular', 23), fill=WHITE)
    d.text((225, 1540), FONE, font=f('Bold', 36), fill=(245, 180, 40))
    return para_feed(im, 60, 1720)

def arte2(im):   # Seguro de vida (já é 1080x1350)
    patch(im, (512, 1238, 800, 1296)); d = ImageDraw.Draw(im)
    d.text((518, 1242), FONE, font=f('Bold', 34), fill=(15, 20, 30))
    return im

def arte2b(im):  # Seguro auto — corrige a estatística (70% NÃO têm seguro)
    patch(im, (785, 206, 1020, 240)); d = ImageDraw.Draw(im)
    d.text((788, 207), '70% DOS VEÍCULOS', font=f('Regular', 23), fill=WHITE)
    return para_feed(im, 100, 1900)

def arte3(im):   # Planos de saúde
    patch(im, (160, 1730, 460, 1782)); d = ImageDraw.Draw(im)
    d.text((170, 1733), FONE, font=f('Regular', 34), fill=WHITE)
    return para_feed(im, 240, 1920)

def arte4(im):   # Residencial
    patch(im, (195, 1524, 525, 1572)); d = ImageDraw.Draw(im)
    d.text((202, 1526), FONE, font=f('Regular', 32), fill=WHITE)
    return para_feed(im, 40, 1700)

def arte5(im): return para_feed(im, 0, 1920)     # Por que a Quadrata
def arte6(im): return para_feed(im, 200, 1920)   # Moto


POSTS = [
    ('1.png', '003_assistencia_familiar', arte1, 'Proteja quem', 'você ama',
     ['Titular e família inclusos', 'Traslado nacional e internacional', 'Atendimento telefônico 24h']),
    ('2.png', '004_seguro_de_vida', arte2, 'Seguro de vida', 'que cabe no bolso',
     ['A partir de R$ 29,90 por mês', 'Cotação rápida pelo WhatsApp', 'Sem burocracia']),
    ('2 (2).png', '005_seguro_auto_proteja_se', arte2b, 'Faça parte dos 30%', 'que se protegem',
     ['Colisão, roubo e terceiros', 'Guincho e assistência 24h', 'Cotação rápida pelo WhatsApp']),
    ('3.png', '006_planos_de_saude', arte3, 'O plano de saúde', 'ideal pra família',
     ['Várias operadoras numa conversa só', 'Comparação de preço e rede', 'Atendimento 24h']),
    ('4.png', '007_seguro_residencial', arte4, 'Sua casa protegida', 'por pouco',
     ['Incêndio, roubo e danos elétricos', 'Chaveiro, encanador e eletricista', 'Cotação rápida pelo WhatsApp']),
    ('5.png', '008_por_que_quadrata', arte5, 'Você avisa.', 'A gente resolve.',
     ['Acionamento imediato', 'Acompanhamento do início ao fim', 'Atendimento 24h pelo WhatsApp']),
    ('6.png', '009_seguro_moto', arte6, 'Seguro moto', 'pra trabalho e lazer',
     ['Roubo e furto', 'Assistência 24h e guincho', 'Cotação rápida pelo WhatsApp']),
]

bat = RAIZ / 'posts' / '001_apresentacao_fabricio' / 'PUBLICAR.bat'
for arq, pasta, ajuste, t1, t2, itens in POSTS:
    dest = RAIZ / 'posts' / pasta
    if (dest / 'PUBLICADO.txt').exists():
        print('Pulando (já publicado):', pasta); continue
    dest.mkdir(exist_ok=True)
    im = Image.open(SUG / arq).convert('RGB')
    im = ajuste(im).filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    im.save(dest / 'slide1.jpg', quality=93)
    slide_cta(t1, t2, itens).save(dest / 'slide2.jpg', quality=93)
    shutil.copy(bat, dest / 'PUBLICAR.bat')
    print('OK:', pasta)
