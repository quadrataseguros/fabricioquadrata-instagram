"""Gera a arte 4:5 (1080x1350) para grupos de WhatsApp. O clique vem do link wa.me na mensagem."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_reels as g

g.W, g.H = 1080, 1350
RAIZ = g.RAIZ
saida = RAIZ / 'divulgacao'
saida.mkdir(exist_ok=True)

bg = g.fundo(RAIZ / 'reels/fotos/perguntas.jpg', 0.38, 0.40, 0.85).convert('RGBA')
d = ImageDraw.Draw(bg)
lg = Image.open(g.LOGO).convert('RGBA')
lg = lg.resize((440, int(lg.height * 440 / lg.width)), Image.LANCZOS)
bg.alpha_composite(lg, (g.MARGEM, 60))
y = g.texto_linhas(d, g.quebra(d, 'Seguro sem complicação.', g.fonte(92), 900), g.fonte(92), g.MARGEM, 250)
g.texto_linhas(d, ['Cotação grátis, direto no WhatsApp.'], g.fonte(44, False), g.MARGEM, y + 10)

chips = ['Auto', 'Moto', 'Vida', 'Saúde', 'Residencial', 'Consórcio']
x, yy, f = g.MARGEM, 760, g.fonte(40)
for c in chips:
    w = int(d.textlength(c, font=f)) + 56
    if x + w > 1080 - g.MARGEM:
        x, yy = g.MARGEM, yy + 90
    d.rounded_rectangle((x, yy, x + w, yy + 72), radius=36, fill=g.AZUL)
    d.text((x + 28, yy + 9), c, font=f, fill=g.BRANCO)
    x += w + 16

d.rounded_rectangle((g.MARGEM, 970, 1080 - g.MARGEM, 1110), radius=70, fill=g.AZUL)
d.text((540, 1014), 'TOQUE NO LINK ABAIXO', font=g.fonte(50), fill=g.BRANCO, anchor='mm')
d.text((540, 1072), 'e fale agora com o Fabrício', font=g.fonte(36, False), fill=g.BRANCO, anchor='mm')
d.text((540, 1160), 'Atendimento 24 horas', font=g.fonte(38), fill=g.BRANCO, anchor='mm')
d.text((540, 1215), 'Valores e coberturas sujeitos a análise de perfil e condições da seguradora.',
       font=g.fonte(23, False), fill=g.BRANCO, anchor='mm')
bg.convert('RGB').save(saida / 'whatsapp_cotacao.jpg', quality=95)
