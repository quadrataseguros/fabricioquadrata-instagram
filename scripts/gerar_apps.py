"""
gerar_apps.py — campanha para motoristas de aplicativo (pôster e carrossel de terceiros).
Uso: python scripts/gerar_apps.py     Saída: posts/029_app_poster, posts/030_app_terceiros_carrossel
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_feeds as f
import gerar_reels as g

W, H, M = f.W, f.H, f.M
AMARELO = (255, 200, 40)
AVISO = 'Coberturas variam conforme a apólice. Regras para motorista de aplicativo variam por seguradora. Valores sujeitos a análise de perfil e condições da seguradora.'


def fundo_estrada():
    im = f.fundo_liso()
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k in range(-2, 8):  # faixas diagonais de "estrada"
        x = k * 220
        d.polygon([(x, H), (x + 70, H), (x + 70 + 520, 0), (x + 520, 0)], fill=(36, 138, 255, 30))
    return Image.alpha_composite(im, ov)


def faixa_contato(im):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 1110, W, H), fill=g.MARINHO)
    f.logo(im, 300, M, 1135)
    d.text((440, 1140), 'Cotação grátis no WhatsApp:', font=g.fonte(36), fill=g.BRANCO)
    d.text((440, 1190), g.TELEFONE, font=g.fonte(72), fill=g.AZUL)
    g.texto_linhas(d, g.quebra(d, AVISO, g.fonte(21, False), 960), g.fonte(21, False), M, 1295, espaco=1.15)


def poster():
    im = fundo_estrada()
    d = ImageDraw.Draw(im)
    f.logo(im, 380, M, 60)
    g.pilula(d, 'Uber · 99 · iFood · inDrive', g.fonte(40), M, 215, cor=AMARELO, cor_texto=g.MARINHO)
    d.text((M - 6, 320), 'RODOU?', font=g.fonte(205), fill=g.BRANCO)
    d.text((M - 6, 530), 'PROTEJA.', font=g.fonte(175), fill=AMARELO)
    y = 810
    d.rounded_rectangle((M, y, M + 10, y + 190), radius=5, fill=AMARELO)
    g.texto_linhas(d, g.quebra(d, 'Cobertura de danos a terceiros para quem vive de rodar por aplicativo.', g.fonte(46, False), 860),
                   g.fonte(46, False), M + 36, y, espaco=1.3)
    d.rounded_rectangle((M, 1000, M + 560, 1080), radius=40, fill=AMARELO)
    d.text((M + 280, 1040), 'Peça a sua cotação', font=g.fonte(40), fill=g.MARINHO, anchor='mm')
    faixa_contato(im)
    return im


def carrossel():
    itens = [
        ('Você roda o dia todo', 'Mais horas na rua, mais chance de um imprevisto no trânsito.'),
        ('O prejuízo do outro pode sobrar para você', 'Em uma batida com culpa, o conserto do outro veículo pode pesar no seu bolso.'),
        ('Cobertura de danos a terceiros', 'Costuma cobrir danos materiais e corporais causados a outras pessoas, conforme a apólice.'),
        ('Vale para quem roda por app?', 'Cada seguradora tem a sua regra. O Fabrício confere antes de você contratar.'),
    ]
    total = len(itens) + 2
    capa = fundo_estrada()
    d = ImageDraw.Draw(capa)
    f.logo(capa, 400, M, 70)
    g.pilula(d, 'Motorista de app, é com você', g.fonte(40), M, 250, cor=AMARELO, cor_texto=g.MARINHO)
    y = g.texto_linhas(d, g.quebra(d, 'E SE VOCÊ BATER NO CARRO DE ALGUÉM?', g.fonte(110), 900), g.fonte(110), M, 360)
    d.text((W - M - 70, H - 190), 'Arraste', font=g.fonte(44), fill=g.BRANCO, anchor='ra')
    d.polygon([(W - M - 50, H - 190), (W - M - 50, H - 140), (W - M, H - 165)], fill=g.AZUL)
    f.rodape(capa, 1, total)
    imgs = [capa] + [f.item(i + 1, t, b, i + 2, total) for i, (t, b) in enumerate(itens)]
    imgs.append(f.cta('Rodou? Proteja. Quer a sua cotação?', 'APP', total, total, AVISO))
    return imgs


if __name__ == '__main__':
    f.salvar('029_app_poster', [poster()])
    f.salvar('030_app_terceiros_carrossel', carrossel())
