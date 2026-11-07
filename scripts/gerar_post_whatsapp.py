"""Gera a arte vertical (1080x1920) para enviar em grupos de WhatsApp.
A imagem não carrega link: o clique vem do link wa.me na mensagem que acompanha a imagem."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_reels as g

RAIZ = g.RAIZ
saida = RAIZ / 'divulgacao'
saida.mkdir(exist_ok=True)

bg = g.fundo(RAIZ / 'reels/fotos/perguntas.jpg', 0.30, 0.45, 0.80).convert('RGBA')
d = ImageDraw.Draw(bg)

# logotipo grande no topo
lg = Image.open(g.LOGO).convert('RGBA')
lg = lg.resize((560, int(lg.height * 560 / lg.width)), Image.LANCZOS)
bg.alpha_composite(lg, (g.MARGEM, 150))

# título
y = g.texto_linhas(d, g.quebra(d, 'Seguro sem complicação.', g.fonte(118), 900), g.fonte(118), g.MARGEM, 390)
y = g.texto_linhas(d, g.quebra(d, 'Cotação grátis, direto no WhatsApp.', g.fonte(60, False), 900), g.fonte(60, False), g.MARGEM, y + 20)

# produtos em pílulas
chips = ['Auto', 'Moto', 'Vida', 'Saúde', 'Residencial', 'Consórcio']
x, yy = g.MARGEM, 1090
f = g.fonte(46)
for c in chips:
    w = int(d.textlength(c, font=f)) + 64
    if x + w > 1080 - g.MARGEM:
        x, yy = g.MARGEM, yy + 100
    d.rounded_rectangle((x, yy, x + w, yy + 80), radius=40, fill=g.AZUL)
    d.text((x + 32, yy + 12), c, font=f, fill=g.BRANCO)
    x += w + 18

# botão de chamada
d.rounded_rectangle((g.MARGEM, 1380, 1080 - g.MARGEM, 1530), radius=75, fill=g.AZUL)
d.text((540, 1432), 'TOQUE NO LINK ABAIXO', font=g.fonte(54), fill=g.BRANCO, anchor='mm')
d.text((540, 1495), 'e fale agora com o Fabrício', font=g.fonte(40, False), fill=g.BRANCO, anchor='mm')
d.text((540, 1600), 'Atendimento 24 horas  |  ' + g.TELEFONE, font=g.fonte(38), fill=g.BRANCO, anchor='mm')
g.texto_linhas(d, g.quebra(d, 'Valores e coberturas sujeitos a análise de perfil e condições da seguradora.', g.fonte(26, False), 900),
               g.fonte(26, False), g.MARGEM, 1665)

bg.convert('RGB').save(saida / 'whatsapp_cotacao.jpg', quality=95)
print('OK', saida / 'whatsapp_cotacao.jpg')
