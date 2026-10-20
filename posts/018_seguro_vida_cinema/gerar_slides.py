"""Post 018 — carrossel com foto PANORÂMICA contínua (a modelo "caminha" entre os slides).
foto_base.jpg traz texto e logo da campanha da Porto: eles são apagados (preenchimento por
vizinhança) e a foto é espelhada/estendida em um painel de 4 slides de largura."""
from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

AQUI = Path(__file__).parent
RAIZ = AQUI.parent.parent
W, H = 1080, 1350
BLUE = (36, 138, 255); NAVY = (11, 39, 72); WHITE = (255, 255, 255); LIGHT = (234, 243, 255); SKY = (130, 196, 255)
N = 4
FONTS = RAIZ / 'marca' / 'fonts'
def f(w, s): return ImageFont.truetype(str(FONTS / f'Poppins-{w}.ttf'), s)
logo = Image.open(RAIZ / 'marca' / 'logo_quadrata.png').convert('RGBA'); logo = logo.crop(logo.getbbox())
icon = logo.crop((0, 0, logo.width, int(logo.height * 0.70))); icon = icon.crop(icon.getbbox())
rng = np.random.default_rng(7)

# ---------- limpeza: apaga texto/logo/pílula da campanha por preenchimento de vizinhança ----------
def limpa(im):
    a = np.asarray(im, dtype=np.float32)
    mask = np.zeros(a.shape[:2], bool)
    for (x0, y0, x1, y1) in [(85, 255, 625, 372), (85, 440, 425, 540), (88, 570, 470, 835), (92, 868, 520, 1100), (505, 868, 580, 1100), (92, 1170, 380, 1230)]:
        r, g, b = a[y0:y1, x0:x1, 0], a[y0:y1, x0:x1, 1], a[y0:y1, x0:x1, 2]
        mn, mx = np.minimum(np.minimum(r, g), b), np.maximum(np.maximum(r, g), b)
        m = ((mn > 170) & (mx - mn < 30)) | ((b > r + 35) & (b > g + 5))
        mask[y0:y1, x0:x1] |= m
    mk = Image.fromarray((mask * 255).astype('uint8')).filter(ImageFilter.MaxFilter(7))
    mask = np.asarray(mk) > 0
    w = (~mask).astype(np.float32)
    out = a.copy()
    gb = lambda arr, sg: np.asarray(Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), 'L').filter(ImageFilter.GaussianBlur(sg)), dtype=np.float32)
    for sg in (6, 14, 30, 60):
        num = np.stack([gb(a[..., c] * w, sg) for c in range(3)], -1)
        den = gb(w * 255, sg)[..., None] / 255
        fill = num / np.maximum(den, 1e-3)
        sel = mask & (den[..., 0] > 0.06)
        out[sel] = fill[sel]
        mask = mask & ~sel
        w = np.where(sel, 1.0, w).astype(np.float32); a = np.where(sel[..., None], out, a)
    return Image.fromarray(np.clip(out, 0, 255).astype('uint8'))

orig = limpa(Image.open(AQUI / 'foto_base.jpg').convert('RGB').crop((0, 0, 1080, 1920)))

# ---------- painel panorâmico (4 slides de largura) ----------
S = 0.8; Y0 = 60
pw, ph = int(1080 * S), int(1920 * S)                    # 864 x 1536
pic = orig.resize((pw, ph), Image.LANCZOS).crop((0, Y0, pw, Y0 + H))     # 864 x 1350, modelo à direita
pic_f = ImageOps.mirror(pic)                              # modelo à esquerda
PW = W * N
pan = Image.new('RGB', (PW, H))
pan.paste(pic_f, (0, 0)); pan.paste(pic, (PW - pw, 0))
# miolo: tiras de grama (x 0..259 da foto) espelhadas lado a lado
strip = pic.crop((0, 0, 259, H))
baixo = strip.crop((0, 1040, 259, 1110)).resize((259, 310), Image.LANCZOS).filter(ImageFilter.GaussianBlur(6))
strip.paste(baixo, (0, 1040)); strip_m = ImageOps.mirror(strip)
x = pw; n = 10; mid = PW - pw - pw
for i in range(n):
    x0 = pw + round(mid * i / n); x1 = pw + round(mid * (i + 1) / n)
    t = (strip if i % 2 == 0 else strip_m).resize((x1 - x0, H), Image.LANCZOS)
    pan.paste(t, (x0, 0))
soft = pan.filter(ImageFilter.GaussianBlur(14))           # esconde emendas só no miolo
m = Image.new('L', (PW, H), 0); ImageDraw.Draw(m).rectangle((pw + 30, 0, PW - pw - 30, H), fill=255)
pan = Image.composite(soft, pan, m.filter(ImageFilter.GaussianBlur(40)))

def cinema(im, vinheta=0.30, grao=3.5):
    a = np.asarray(im.convert('RGB'), dtype=np.float32) / 255
    lum = (a * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    a = lum + (a - lum) * 0.93
    a = a + np.array([0, 0.010, 0.035]) * (1 - lum) + np.array([0.025, 0.008, -0.015]) * lum
    a = np.clip(a, 0, 1); a = a * a * (3 - 2 * a) * 0.45 + a * 0.55
    hi = np.clip((a.mean(2, keepdims=True) - 0.62) / 0.38, 0, 1) * a
    bl = np.asarray(Image.fromarray((hi * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(22)), dtype=np.float32) / 255
    a = 1 - (1 - a) * (1 - bl * 0.35)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h * 0.45) / (h * 0.62)) ** 2)
    a = a * (1 - vinheta * np.clip(r - 0.45, 0, 1) ** 1.5)[..., None]
    a = a + rng.normal(0, grao / 255, (h, w, 1))
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype('uint8'))

def fatia(i, desfoque=0, escuro=0.0, ganho=1.0):
    im = pan.crop((i * W, 0, (i + 1) * W, H))
    if desfoque: im = im.filter(ImageFilter.GaussianBlur(desfoque))
    im = cinema(im).convert('RGBA')
    if escuro: im.alpha_composite(Image.new('RGBA', (W, H), NAVY + (int(escuro * 255),)))
    return im

# ---------- utilidades de desenho ----------
def ctext(d, y, t, font, fill): d.text(((W - d.textlength(t, font=font)) / 2, y), t, font=font, fill=fill)
def rtext(d, xr, y, t, font, fill): d.text((xr - d.textlength(t, font=font), y), t, font=font, fill=fill)
def sombra(im, box, raio, alfa=90, desf=18, dy=8):
    s = Image.new('RGBA', im.size, (0, 0, 0, 0)); x0, y0, x1, y1 = box
    ImageDraw.Draw(s).rounded_rectangle((x0, y0 + dy, x1, y1 + dy), radius=raio, fill=(0, 0, 0, alfa))
    im.alpha_composite(s.filter(ImageFilter.GaussianBlur(desf)))
def texto_sombra(im, xy, t, font, fill, anc='la'):
    s = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(s).text(xy, t, font=font, fill=(0, 0, 0, 150), anchor=anc)
    im.alpha_composite(s.filter(ImageFilter.GaussianBlur(7))); ImageDraw.Draw(im).text(xy, t, font=font, fill=fill, anchor=anc)
def footer(im, active, cor=WHITE):
    d = ImageDraw.Draw(im)
    texto_sombra(im, (W / 2, H - 70), '@fabricioquadrata', f('Medium', 30), cor, 'mm')
    x0 = W / 2 - (N * 28) / 2
    for i in range(N):
        c = cor if i == active else (200, 205, 210)
        d.ellipse((x0 + i * 28, H - 135, x0 + i * 28 + 12, H - 123), fill=c + ((255,) if i == active else (150,)))
def vidro(im, box, raio=26, alfa=0.60):
    x0, y0, x1, y1 = box
    reg = im.crop(box).filter(ImageFilter.GaussianBlur(10))
    mk = Image.new('L', reg.size, 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, reg.width - 1, reg.height - 1), radius=raio, fill=255)
    im.paste(reg, (x0, y0), mk); im.paste(Image.new('RGBA', reg.size, NAVY + (int(alfa * 255),)), (x0, y0), mk)
    ImageDraw.Draw(im).rounded_rectangle(box, radius=raio, outline=(255, 255, 255, 45), width=2)
def brl(x): return 'R$ ' + f'{x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
def estrela(d, cx, cy, r, fill):
    d.polygon([(cx + (r if i % 2 == 0 else r * .42) * math.cos(-math.pi / 2 + i * math.pi / 5),
                cy + (r if i % 2 == 0 else r * .42) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)], fill=fill)
def selo(d, cx, cy, r=17):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BLUE); estrela(d, cx, cy, r * .62, WHITE)
def check(d, cx, cy, r=18):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=WHITE, width=3)
    d.line((cx - r * .45, cy + 1, cx - r * .1, cy + r * .4, cx + r * .5, cy - r * .35), fill=WHITE, width=4)
def salvar(im, n): im.convert('RGB').save(AQUI / f'slide{n}.jpg', quality=93)
def logo_card(im, x, y, h):
    lw = int(logo.width * h / logo.height)
    sombra(im, (x, y, x + lw + 40, y + h + 36), 26, 80)
    ImageDraw.Draw(im).rounded_rectangle((x, y, x + lw + 40, y + h + 36), radius=26, fill=WHITE)
    im.alpha_composite(logo.resize((lw, h), Image.LANCZOS), (x + 20, y + 18))

def base_escura(a0=170, altura=300):
    t = np.clip((np.arange(H, dtype=np.float32) - (H - altura)) / altura, 0, 1)
    arr = np.zeros((H, W, 4), 'uint8'); arr[..., 0], arr[..., 1], arr[..., 2] = NAVY
    arr[..., 3] = ((t * t * (3 - 2 * t)) * a0).astype('uint8')[:, None]
    return Image.fromarray(arr, 'RGBA')

def lateral(esq, a0=120):
    """degradê marinho lateral: esq=True escurece o lado direito (slide 1), False o esquerdo (slide 4)"""
    x = np.arange(W, dtype=np.float32)
    t = np.clip((x - 430) / 500, 0, 1) if esq else np.clip((620 - x) / 500, 0, 1)
    arr = np.zeros((H, W, 4), 'uint8'); arr[..., 0], arr[..., 1], arr[..., 2] = NAVY
    arr[..., 3] = (t ** 1.2 * a0).astype('uint8')[None, :]
    return Image.fromarray(arr, 'RGBA')

FAIXAS = [('Até 30 anos', 85.95, 69.01), ('31 a 35', 95.46, 77.47), ('36 a 40', 119.62, 94.80),
          ('41 a 45', 161.11, 125.48), ('46 a 50', 298.92, 188.07)]
def cartao(v): return round(v * 12 * 0.85 / 11, 2)

# Slide 1 — capa: modelo à esquerda, texto na grama à direita
im = fatia(0)
im.alpha_composite(lateral(True)); im.alpha_composite(base_escura())
d = ImageDraw.Draw(im)
logo_card(im, 640, 80, 120)
d.rounded_rectangle((620, 470, 930, 530), radius=30, fill=BLUE)
d.text((650, 481), 'SEGURO DE VIDA', font=f('Bold', 26), fill=WHITE)
texto_sombra(im, (620, 560), 'Viva hoje.', f('Bold', 84), WHITE)
texto_sombra(im, (620, 665), 'Proteja', f('Bold', 66), SKY)
texto_sombra(im, (620, 740), 'o amanhã.', f('Bold', 66), SKY)
sombra(im, (620, 860, 1040, 1010), 30, 80)
d = ImageDraw.Draw(im)
d.rounded_rectangle((620, 860, 1040, 1010), radius=30, fill=WHITE)
d.text((650, 878), 'a partir de', font=f('Medium', 26), fill=NAVY)
d.text((650, 912), brl(FAIXAS[0][2]), font=f('Bold', 50), fill=BLUE)
d.text((650, 970), 'por mês', font=f('Medium', 22), fill=NAVY)
d.line((830, 1180, 990, 1180), fill=WHITE, width=4); d.line((960, 1160, 992, 1180, 960, 1200), fill=WHITE, width=4, joint='curve')
footer(im, 0); salvar(im, 1)

# Slide 3 — tabela
im = fatia(2, desfoque=10, escuro=0.20); d = ImageDraw.Draw(im)
texto_sombra(im, (W / 2, 120), 'Valores por idade', f('Bold', 66), WHITE, 'mm')
texto_sombra(im, (W / 2, 180), 'por mês, no débito em conta (12x)', f('Medium', 32), WHITE, 'mm')
XL, XH, XM, CW = 70, 330, 705, 305
y = 232
for x, t in ((XH, 'HOMEM'), (XM, 'MULHER')):
    texto_sombra(im, (x + CW / 2, y + 16), t, f('Bold', 30), SKY, 'mm')
y += 60; RH = 128
for rot, h, m in FAIXAS:
    vidro(im, (XL, y, W - 70, y + RH - 14), raio=24, alfa=0.66); d = ImageDraw.Draw(im)
    d.text((XL + 28, y + 36), rot, font=f('Bold', 32), fill=WHITE)
    for x, v in ((XH, h), (XM, m)):
        p = brl(v); d.text((x + (CW - d.textlength(p, font=f('Bold', 40))) / 2, y + 12), p, font=f('Bold', 40), fill=WHITE)
        s = f'ou 11x {brl(cartao(v))}'; d.text((x + (CW - d.textlength(s, font=f('Regular', 24))) / 2, y + 66), s, font=f('Regular', 24), fill=LIGHT)
        if v > 100: selo(d, x + CW - 24, y + 28)
    y += RH
y += 6
vidro(im, (60, y, W - 60, y + 160), raio=24, alfa=0.66); d = ImageDraw.Draw(im)
selo(d, 100, y + 30, 15)
d.text((130, y + 14), 'Câncer (R$ 50 mil) sem custo só em outubro,', font=f('Regular', 25), fill=WHITE)
d.text((130, y + 44), 'nas parcelas acima de R$ 100.', font=f('Regular', 25), fill=WHITE)
d.text((84, y + 94), 'No cartão: 11x com 15% de desconto no total.', font=f('Regular', 24), fill=LIGHT)
d.text((84, y + 126), 'Simulação de 20/10/2026, válida até 26/10. Sujeita à análise de risco.', font=f('Regular', 20), fill=LIGHT)
footer(im, 2); salvar(im, 3)

# Slide 2 — coberturas em pílulas azuis (como na referência)
im = fatia(1, desfoque=6, escuro=0.10); d = ImageDraw.Draw(im)
texto_sombra(im, (80, 100), 'Coberturas', f('Bold', 70), WHITE)
texto_sombra(im, (80, 190), 'iguais em todas as idades:', f('Medium', 40), WHITE)
ITENS = [('Morte', 'R$ 150.000'), ('Invalidez por acidente', 'R$ 150.000'), ('Antecipação por doença grave', 'R$ 150.000'),
         ('Doenças graves', 'R$ 50.000'), ('Assistência funeral', 'R$ 7.000'), ('Diária por incapacidade', 'R$ 100/dia')]
y = 270
for nome, val in ITENS:
    sombra(im, (70, y, W - 70, y + 96), 48, 70, 12, 6); d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, y, W - 70, y + 96), radius=48, fill=(0, 150, 255))
    check(d, 128, y + 48)
    d.text((170, y + 24), nome, font=f('Bold', 31), fill=WHITE)
    rtext(d, W - 110, y + 24, val, f('Bold', 31), WHITE)
    y += 114
sombra(im, (70, y + 6, W - 70, y + 140), 48, 70, 12, 6); d = ImageDraw.Draw(im)
d.rounded_rectangle((70, y + 6, W - 70, y + 140), radius=48, fill=WHITE)
d.text((120, y + 24), 'Diagnóstico de câncer', font=f('Bold', 33), fill=NAVY)
d.text((120, y + 76), 'sem custo em outubro, parcela acima de R$ 100', font=f('Medium', 24), fill=BLUE)
rtext(d, W - 110, y + 36, 'R$ 50.000', f('Bold', 36), NAVY)
footer(im, 1); salvar(im, 2)

# Slide 4 — chamada: modelo à direita, texto na grama à esquerda
im = fatia(3)
im.alpha_composite(lateral(False)); im.alpha_composite(base_escura())
d = ImageDraw.Draw(im)
logo_card(im, 60, 80, 120)
texto_sombra(im, (60, 400), 'Peça a sua', f('Bold', 62), WHITE)
texto_sombra(im, (60, 475), 'simulação', f('Bold', 62), SKY)
texto_sombra(im, (60, 570), 'é só dizer a sua idade', f('Medium', 30), WHITE)
sombra(im, (60, 650, 560, 800), 36, 80); d = ImageDraw.Draw(im)
d.rounded_rectangle((60, 650, 560, 800), radius=36, fill=WHITE)
d.text((90, 668), 'WhatsApp', font=f('Medium', 28), fill=BLUE)
d.text((90, 708), '(11) 98678-0000', font=f('Bold', 44), fill=NAVY)
texto_sombra(im, (60, 840), 'ou chama no direct', f('Medium', 30), WHITE)
footer(im, 3); salvar(im, 4)
