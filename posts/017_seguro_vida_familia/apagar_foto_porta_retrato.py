"""Troca a foto do pai (virada para quem vê o post) pelo verso do porta-retrato.
Gera foto_editada.jpg a partir de foto_base.jpg, preservando os dedos da mãe."""
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

AQUI = Path(__file__).parent
im = Image.open(AQUI / 'foto_base.jpg').convert('RGB')
W, H = im.size

# miolo do porta-retrato (onde aparece a foto), em coordenadas da foto original
TL, TR, BR, BL = (1182, 919), (1339, 918), (1226, 1132), (1102, 1132)
area = Image.new('L', (W, H), 0)
ImageDraw.Draw(area).polygon([TL, TR, BR, BL], fill=255)

# dedos por cima da foto: tom de pele na parte de baixo/direita do miolo
# (o rosto do homem na foto fica acima/à esquerda e não entra nessa zona)
px = im.load()
dedos = Image.new('L', (W, H), 0); dp = dedos.load()
for y in range(915, 1140):
    for x in range(1100, 1330):
        r, g, b = px[x, y]
        pele = r > (158 if x < 1200 else 115) and r - g > 14 and r - b > 32
        if pele and (y > 1060 or (x > 1258 and y > 1030)):
            dp[x, y] = 255
dedos = dedos.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(3))

mask = ImageChops.subtract(area, dedos).filter(ImageFilter.GaussianBlur(1.2))

# verso: papelão kraft, com luz vindo da esquerda/alto, textura leve e pezinho de apoio
verso = Image.new('RGB', (W, H))
vd = ImageDraw.Draw(verso)
x0, x1, y0, y1 = 1100, 1330, 915, 1140
for y in range(y0, y1):
    for x in range(x0, x1):
        t = ((x - x0) / (x1 - x0)) * 0.55 + ((y - y0) / (y1 - y0)) * 0.45
        base = (150 - 38 * t, 110 - 30 * t, 74 - 22 * t)
        n = random.uniform(-5, 5)
        verso.putpixel((x, y), tuple(int(c + n) for c in base))
verso = verso.filter(ImageFilter.GaussianBlur(1.6))
vd = ImageDraw.Draw(verso, 'RGBA')

# sombra interna da moldura (topo e lado esquerdo)
sombra = Image.new('L', (W, H), 0); sd = ImageDraw.Draw(sombra)
sd.line([TL, TR], fill=150, width=9); sd.line([TL, BL], fill=150, width=9)
sombra = sombra.filter(ImageFilter.GaussianBlur(5))
verso = Image.composite(Image.new('RGB', (W, H), (60, 40, 25)), verso, sombra)

# pezinho de apoio: faixa afunilada, pouco contraste, com sombra suave à direita
cx = (TL[0] + TR[0] + BL[0] + BR[0]) / 4 + 4
top_y, bot_y = 975, 1128
skew = (BL[0] - TL[0]) / (BL[1] - TL[1])
def px_at(y, dx): return (cx + (y - 1025) * skew + dx, y)
pe = [px_at(top_y, -9), px_at(top_y, 9), px_at(bot_y, 15), px_at(bot_y, -15)]
sh = Image.new('L', (W, H), 0)
ImageDraw.Draw(sh).polygon([(x + 7, y + 3) for x, y in pe], fill=110)
verso = Image.composite(Image.new('RGB', (W, H), (70, 48, 30)), verso, sh.filter(ImageFilter.GaussianBlur(5)))
vd = ImageDraw.Draw(verso, 'RGBA')
vd.polygon(pe, fill=(128, 92, 60, 255))
vd.line([pe[0], pe[1]], fill=(110, 78, 50, 255), width=3)
verso = verso.filter(ImageFilter.GaussianBlur(0.8))

saida = Image.composite(verso, im, mask)
saida.save(AQUI / 'foto_editada.jpg', quality=95)
print('OK: foto_editada.jpg gerada')
