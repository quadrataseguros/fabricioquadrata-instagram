from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).parent
RAIZ = AQUI.parent.parent
W, H = 1080, 1350
BLUE = (36, 138, 255); NAVY = (11, 39, 72); WHITE = (255, 255, 255); LIGHT = (234, 243, 255)
CARD = (20, 55, 98)
N = 4  # total de slides

FONTS = RAIZ / 'marca' / 'fonts'
def f(w, s): return ImageFont.truetype(str(FONTS / f'Poppins-{w}.ttf'), s)

logo = Image.open(RAIZ / 'marca' / 'logo_quadrata.png').convert('RGBA')
logo = logo.crop(logo.getbbox())
icon = logo.crop((0, 0, logo.width, int(logo.height * 0.70)))
icon = icon.crop(icon.getbbox())

def paste(img, src, w, xy):
    s = src.resize((w, int(src.height * w / src.width)), Image.LANCZOS); img.paste(s, xy, s); return s.size
def ctext(d, y, t, font, fill):
    w = d.textlength(t, font=font); d.text(((W - w) / 2, y), t, font=font, fill=fill)
def rtext(d, xr, y, t, font, fill):
    w = d.textlength(t, font=font); d.text((xr - w, y), t, font=font, fill=fill)
def footer(d, fill, active):
    ctext(d, H - 95, '@fabricioquadrata', f('Medium', 30), fill)
    x0 = W / 2 - (N * 28) / 2
    for i in range(N):
        c = fill if i == active else (fill[0] // 2 + 60, fill[1] // 2 + 60, fill[2] // 2 + 60)
        d.ellipse((x0 + i * 28, H - 135, x0 + i * 28 + 12, H - 123), fill=c)
def save(im, n): im.save(AQUI / f'slide{n}.jpg', quality=92)
def brl(x): return 'R$ ' + f'{x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
def estrela(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)
def selo(d, cx, cy, r=17):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BLUE)
    estrela(d, cx, cy, r * 0.62, WHITE)

# Total mensal no débito em 12x (cotação de 20/10/2026). Cartão: 15% de desconto no total, em 11x.
FAIXAS = [  # rótulo, homem, mulher
    ('Até 30 anos', 85.95, 69.01),
    ('31 a 35', 95.46, 77.47),
    ('36 a 40', 119.62, 94.80),
    ('41 a 45', 161.11, 125.48),
    ('46 a 50', 298.92, 188.07),
]
def cartao(v): return round(v * 12 * 0.85 / 11, 2)

# Slide 1 — capa
im = Image.new('RGB', (W, H), WHITE); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 18), fill=BLUE)
sw, sh = paste(im, logo, 300, ((W - 300) // 2, 100))
y = 100 + sh + 70
ctext(d, y, 'Quanto custa um', f('Bold', 72), NAVY)
ctext(d, y + 95, 'seguro de vida?', f('Bold', 84), BLUE)
ctext(d, y + 235, 'Veja os valores por idade,', f('Medium', 38), NAVY)
ctext(d, y + 285, 'para homens e mulheres', f('Medium', 38), NAVY)
d.rounded_rectangle((W / 2 - 330, y + 400, W / 2 + 330, y + 490), radius=45, fill=BLUE)
ctext(d, y + 418, 'a partir de ' + brl(FAIXAS[0][2]) + ' por mês', f('Bold', 38), WHITE)
footer(d, NAVY, 0); save(im, 1)

# Slide 2 — tabela de valores
im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
ctext(d, 75, 'Valores por idade', f('Bold', 66), WHITE)
ctext(d, 160, 'por mês, no débito em conta (12x)', f('Medium', 32), LIGHT)
X0, XL, XH, XM = 70, 70, 330, 705   # margem, início das colunas
CW = 305
y = 235
for x, t in ((XH, 'HOMEM'), (XM, 'MULHER')):
    tw = d.textlength(t, font=f('Bold', 30)); d.text((x + (CW - tw) / 2, y), t, font=f('Bold', 30), fill=BLUE)
y += 62
RH = 128
for rot, h, m in FAIXAS:
    d.rounded_rectangle((XL, y, W - 70, y + RH - 14), radius=24, fill=CARD)
    d.text((XL + 28, y + 36), rot, font=f('Bold', 32), fill=WHITE)
    for x, v in ((XH, h), (XM, m)):
        tw = d.textlength(brl(v), font=f('Bold', 40)); d.text((x + (CW - tw) / 2, y + 12), brl(v), font=f('Bold', 40), fill=WHITE)
        sub = f'ou 11x {brl(cartao(v))}'
        tw = d.textlength(sub, font=f('Regular', 24)); d.text((x + (CW - tw) / 2, y + 66), sub, font=f('Regular', 24), fill=LIGHT)
        if v > 100: selo(d, x + CW - 24, y + 28)
    y += RH
y += 6
selo(d, 100, y + 18, 15)
d.text((130, y + 3), 'Câncer (R$ 50 mil) sem custo só em outubro,', font=f('Regular', 25), fill=WHITE)
d.text((130, y + 33), 'nas parcelas acima de R$ 100.', font=f('Regular', 25), fill=WHITE)
d.text((70, y + 83), 'No cartão: 11x com 15% de desconto no total.', font=f('Regular', 25), fill=LIGHT)
d.text((70, y + 118), 'Simulação de 20/10/2026, válida até 26/10. Sujeita à análise de risco.', font=f('Regular', 22), fill=LIGHT)
footer(d, WHITE, 1); save(im, 2)

# Slide 3 — coberturas
im = Image.new('RGB', (W, H), WHITE); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 18), fill=BLUE)
ctext(d, 85, 'O que está incluso', f('Bold', 68), NAVY)
ctext(d, 175, 'as mesmas coberturas em todas as idades', f('Medium', 30), BLUE)
ITENS = [('Morte', 'R$ 150.000'), ('Invalidez por acidente', 'R$ 150.000'),
         ('Antecipação por doença grave', 'R$ 150.000'), ('Doenças graves', 'R$ 50.000'),
         ('Assistência funeral', 'R$ 7.000'), ('Diária por incapacidade', 'R$ 100/dia')]
y = 255
for nome, val in ITENS:
    d.rounded_rectangle((70, y, W - 70, y + 100), radius=24, fill=LIGHT)
    d.ellipse((100, y + 34, 132, y + 66), fill=BLUE)
    d.text((158, y + 26), nome, font=f('Medium', 33), fill=NAVY)
    rtext(d, W - 100, y + 26, val, f('Bold', 33), BLUE)
    y += 120
d.rounded_rectangle((70, y, W - 70, y + 120), radius=24, fill=NAVY)
d.text((100, y + 16), 'Diagnóstico de câncer', font=f('Bold', 33), fill=WHITE)
d.text((100, y + 64), 'sem custo em outubro, parcela acima de R$ 100', font=f('Regular', 24), fill=LIGHT)
rtext(d, W - 100, y + 30, 'R$ 50.000', f('Bold', 36), WHITE)
footer(d, NAVY, 2); save(im, 3)

# Slide 4 — chamada
im = Image.new('RGB', (W, H), BLUE); d = ImageDraw.Draw(im)
card = Image.new('RGBA', (360, 360), (0, 0, 0, 0)); cd = ImageDraw.Draw(card); cd.rounded_rectangle((0, 0, 359, 359), radius=60, fill=WHITE)
im.paste(card, ((W - 360) // 2, 170), card); paste(im, icon, 250, ((W - 250) // 2, 225))
ctext(d, 590, 'Peça a sua simulação', f('Bold', 70), WHITE)
ctext(d, 685, 'é só dizer sua idade', f('Bold', 70), NAVY)
ctext(d, 835, 'WhatsApp', f('Medium', 38), WHITE)
d.rounded_rectangle((150, 895, W - 150, 1015), radius=60, fill=NAVY)
ctext(d, 915, '(11) 98678-0000', f('Bold', 56), WHITE)
ctext(d, 1050, 'ou chama no direct', f('Medium', 36), WHITE)
footer(d, WHITE, 3); save(im, 4)
