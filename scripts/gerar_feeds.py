"""
gerar_feeds.py — monta posts de feed 1080x1350 (carrossel ou imagem única) no padrão da Quadrata.
Uso:  python scripts/gerar_feeds.py coberturas
Saída: posts/<pasta>/slide1.jpg, slide2.jpg ...  (a legenda.txt é escrita à mão)
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_reels as g

g.W, g.H = 1080, 1350
W, H = 1080, 1350
RAIZ = g.RAIZ
M = 90
AVISO_PADRAO = 'Coberturas variam conforme a apólice contratada. Valores sujeitos a análise de perfil e condições da seguradora.'


def logo(tela, largura, x, y):
    lg = Image.open(g.LOGO).convert('RGBA')
    lg = lg.resize((largura, int(lg.height * largura / lg.width)), Image.LANCZOS)
    tela.alpha_composite(lg, (x, y))
    return lg.height


def fundo_liso():
    im = Image.new('RGB', (W, H), g.MARINHO)
    d = ImageDraw.Draw(im)
    for i in range(H):  # degradê vertical suave
        t = i / H
        cor = tuple(int(a + (b - a) * t) for a, b in zip((12, 48, 92), (7, 30, 60)))
        d.line((0, i, W, i), fill=cor)
    return im.convert('RGBA')


def rodape(tela, n=None, total=None):
    d = ImageDraw.Draw(tela)
    d.text((M, H - 70), '@fabricioquadrata', font=g.fonte(30, False), fill=g.BRANCO)
    if n:
        d.text((W - M, H - 70), f'{n}/{total}', font=g.fonte(30, False), fill=g.BRANCO, anchor='ra')


def capa(foto, titulo, chip, n, total, escuridao=0.40):
    bg = g.fundo(RAIZ / foto, escuridao, 0.35, 0.80).convert('RGBA')
    d = ImageDraw.Draw(bg)
    logo(bg, 400, M, 70)
    y = g.texto_linhas(d, g.quebra(d, titulo, g.fonte(96), 900), g.fonte(96), M, 300)
    if chip:
        g.pilula(d, chip, g.fonte(48), M, y + 30)
    if total > 1:
        d.text((W - M - 70, H - 190), 'Arraste', font=g.fonte(44), fill=g.BRANCO, anchor='ra')
        d.polygon([(W - M - 50, H - 190), (W - M - 50, H - 140), (W - M, H - 165)], fill=g.AZUL)
    rodape(bg, n, total)
    return bg


def item(numero, titulo, corpo, n, total):
    t = fundo_liso()
    d = ImageDraw.Draw(t)
    logo(t, 300, M, 70)
    y = 400
    if numero:
        d.ellipse((M, y, M + 150, y + 150), fill=g.AZUL)
        d.text((M + 75, y + 72), str(numero), font=g.fonte(96), fill=g.BRANCO, anchor='mm')
        y += 200
    y = g.texto_linhas(d, g.quebra(d, titulo, g.fonte(78), 900), g.fonte(78), M, y)
    if corpo:
        d.rounded_rectangle((M, y + 30, M + 10, y + 30 + int(46 * 1.3) * len(g.quebra(d, corpo, g.fonte(46, False), 860))), radius=5, fill=g.AZUL)
        g.texto_linhas(d, g.quebra(d, corpo, g.fonte(46, False), 860), g.fonte(46, False), M + 36, y + 30, espaco=1.3)
    rodape(t, n, total)
    return t


def cta(pergunta, palavra, n, total, aviso=AVISO_PADRAO):
    t = fundo_liso()
    d = ImageDraw.Draw(t)
    logo(t, 700, (W - 700) // 2, 150)
    y = g.texto_linhas(d, g.quebra(d, pergunta, g.fonte(72), 900), g.fonte(72), M, 500)
    d.rounded_rectangle((M, y + 40, W - M, y + 190), radius=75, fill=g.AZUL)
    d.text((W // 2, y + 115), f'Comenta {palavra}', font=g.fonte(64), fill=g.BRANCO, anchor='mm')
    d.text((W // 2, y + 290), 'Cotação grátis no WhatsApp:', font=g.fonte(40), fill=g.BRANCO, anchor='mm')
    d.text((W // 2, y + 380), g.TELEFONE, font=g.fonte(80), fill=g.AZUL, anchor='mm')
    g.texto_linhas(d, g.quebra(d, aviso, g.fonte(26, False), 900), g.fonte(26, False), M, y + 450)
    rodape(t, n, total)
    return t


def post_foto(foto, titulo, sub, chips, aviso=None, desloca=0, tam_titulo=84, chips_y=800, tam_chip=38):
    """Imagem única: foto de fundo, título no alto, chips e faixa de contato embaixo."""
    bg = g.fundo(RAIZ / foto, 0.30, 0.50, 0.85).convert('RGBA')
    if desloca:
        base = fundo_liso()
        base.paste(bg.crop((0, 0, W, H - desloca)), (0, desloca))
        for i in range(260):  # degradê para fundir a foto com o fundo azul no alto
            a = int(255 * (1 - i / 260))
            faixa = Image.new('RGBA', (W, 1), (*g.MARINHO, a))
            base.alpha_composite(faixa, (0, desloca + i))
        bg = base
    d = ImageDraw.Draw(bg)
    logo(bg, 380, M, 60)
    y = g.texto_linhas(d, g.quebra(d, titulo, g.fonte(tam_titulo), 900), g.fonte(tam_titulo), M, 240)
    if sub:
        g.texto_linhas(d, g.quebra(d, sub, g.fonte(42, False), 900), g.fonte(42, False), M, y + 10)
    x, yy, f = M, chips_y, g.fonte(tam_chip)
    for c in chips:
        w = int(d.textlength(c, font=f)) + 56
        if x + w > W - M:
            x, yy = M, yy + 88
        d.rounded_rectangle((x, yy, x + w, yy + 70), radius=35, fill=g.AZUL)
        d.text((x + 28, yy + 9), c, font=f, fill=g.BRANCO)
        x += w + 16
    d.rectangle((0, 1110, W, H), fill=g.MARINHO)
    logo(bg, 300, M, 1135)
    d.text((440, 1140), 'Cotação grátis no WhatsApp:', font=g.fonte(36), fill=g.BRANCO)
    d.text((440, 1190), g.TELEFONE, font=g.fonte(72), fill=g.AZUL)
    g.texto_linhas(d, g.quebra(d, aviso or AVISO_PADRAO, g.fonte(21, False), 960), g.fonte(21, False), M, 1295, espaco=1.15)
    return bg


def salvar(pasta, imgs):
    out = RAIZ / 'posts' / pasta
    out.mkdir(parents=True, exist_ok=True)
    for i, im in enumerate(imgs, 1):
        im.convert('RGB').save(out / f'slide{i}.jpg', quality=95)
    bat = RAIZ / 'posts/018_seguro_vida_cinema/PUBLICAR.bat'
    if bat.exists() and not (out / 'PUBLICAR.bat').exists():
        (out / 'PUBLICAR.bat').write_bytes(bat.read_bytes())
    print('OK', out, len(imgs), 'slide(s)')


def coberturas():
    itens = [
        ('Carro reserva', 'Costuma depender do plano e do prazo em dias. Confira o que a sua apólice prevê.'),
        ('Vidros e faróis', 'Nem toda apólice inclui. Veja se está na sua e qual é o limite.'),
        ('Alagamento', 'Costuma estar na cobertura compreensiva, mas não em todas as apólices.'),
        ('Danos a terceiros', 'Danos materiais e corporais a terceiros costumam ser coberturas à parte.'),
        ('Assistência 24h', 'Guincho e socorro costumam ter limite de quilômetros e de acionamentos.'),
    ]
    total = len(itens) + 2
    imgs = [capa('reels/fotos/perguntas.jpg', '5 coberturas que muita gente acha que tem', 'Você sabe se a sua tem?', 1, total)]
    imgs += [item(i + 1, t, b, i + 2, total) for i, (t, b) in enumerate(itens)]
    imgs.append(cta('Quer conferir a sua apólice?', 'COTAR', total, total))
    salvar('024_5_coberturas_carrossel', imgs)


def alagamento():
    passos = [
        ('Não gire a chave', 'Ligar o motor com água dentro pode danificá-lo.'),
        ('Fotografe tudo', 'Nível da água, painel e placa. Isso ajuda no atendimento.'),
        ('Chame o guincho', 'Remova o carro com cuidado, sem forçar o motor.'),
        ('Avise a seguradora ou a corretora', 'Quanto antes, melhor para abrir o atendimento.'),
    ]
    total = len(passos) + 2
    imgs = [capa('reels/fotos/alagou.jpg', 'Seu carro alagou? Faça isto primeiro.', None, 1, total, 0.30)]
    imgs += [item(i + 1, t, b, i + 2, total) for i, (t, b) in enumerate(passos)]
    imgs.append(cta('O seu seguro cobre alagamento?', 'COTAR', total, total,
                    'Alagamento costuma estar na cobertura compreensiva, mas depende da apólice. Valores sujeitos a análise de perfil e condições da seguradora.'))
    salvar('026_alagamento_4_passos', imgs)


def novembro_azul(foto='reels/fotos/novembro_azul.jpg'):
    salvar('025_novembro_azul', [post_foto(
        foto, 'Novembro Azul: cuidar de você também protege quem ama.', 'Marque um homem importante.',
        ['Consulta em dia', 'Exames de rotina', 'Prevenção'],
        'Conteúdo informativo. Não substitui orientação médica. Coberturas variam conforme a apólice. Valores sujeitos a análise de perfil e condições da seguradora.', desloca=230, tam_titulo=74, chips_y=930)])


def consorcio(foto='reels/fotos/perguntas.jpg'):
    salvar('027_consorcio', [post_foto(
        foto, 'Consórcio: planejamento estratégico.', 'Conquiste mais, com inteligência.',
        ['Parcelas reduzidas até a contemplação*', 'Várias contemplações por mês', 'Planejamento estratégico'],
        '*Nos planos com parcela reduzida, conforme a administradora. Condições conforme o plano e o contrato.',
        desloca=230, tam_titulo=84, chips_y=850, tam_chip=36)])


if __name__ == '__main__':
    globals()[sys.argv[1]]()
