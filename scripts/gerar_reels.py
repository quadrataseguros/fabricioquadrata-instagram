"""
gerar_reels.py — monta Reels 1080x1920 (MP4) no padrão visual da Quadrata:
foto de fundo com zoom lento, degradê azul-marinho, texto grande, logotipo
horizontal em letras brancas e CTA do WhatsApp. Precisa de ffmpeg e pillow.

Uso:  python scripts/gerar_reels.py alagou
Saída: reels/saida/<nome>.mp4  (sem áudio de música: escolha um áudio em alta no Instagram ao postar)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
FONTE_B = str(RAIZ / 'marca/fonts/Poppins-Bold.ttf')
FONTE_M = str(RAIZ / 'marca/fonts/Poppins-Medium.ttf')
LOGO = RAIZ / 'marca/logo_horizontal_branco.png'
W, H = 1080, 1920
MARINHO, AZUL, BRANCO = (9, 38, 73), (36, 138, 255), (255, 255, 255)
MARGEM, LARGURA = 90, 820  # área segura (botões do Instagram)
TELEFONE = '(11) 98678-0000'


def fonte(tam, negrito=True):
    return ImageFont.truetype(FONTE_B if negrito else FONTE_M, tam)


def quebra(draw, texto, f, largura):
    linhas, atual = [], ''
    for palavra in texto.split():
        teste = (atual + ' ' + palavra).strip()
        if draw.textlength(teste, font=f) <= largura:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def fundo(foto, escuridao, topo=0.55, base=0.75):
    """Foto cobrindo a tela, escurecida de forma contínua (sem faixas)."""
    im = Image.open(foto).convert('RGB')
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    a = np.asarray(im).astype(np.float32)
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    alpha = escuridao + (topo * np.clip(1 - y / 0.35, 0, 1) ** 1.5) + (base * np.clip((y - 0.55) / 0.45, 0, 1) ** 1.2)
    alpha = np.clip(alpha, 0, 0.93)[:, :, None]
    azul = np.array(MARINHO, dtype=np.float32)[None, None, :]
    return Image.fromarray((a * (1 - alpha) + azul * alpha).astype(np.uint8))


def logo_pequeno(tela, largura=300, x=MARGEM, y=250):
    lg = Image.open(LOGO).convert('RGBA')
    lg = lg.resize((largura, int(lg.height * largura / lg.width)), Image.LANCZOS)
    tela.alpha_composite(lg, (x, y))


def texto_linhas(d, linhas, f, x, y, cor=BRANCO, espaco=1.12):
    for ln in linhas:
        d.text((x, y), ln, font=f, fill=cor)
        y += int(f.size * espaco)
    return y


def pilula(d, texto, f, x, y, cor=AZUL, cor_texto=BRANCO, pad=(34, 16)):
    w = int(d.textlength(texto, font=f)) + pad[0] * 2
    h = f.size + pad[1] * 2
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=cor)
    d.text((x + pad[0], y + pad[1] - 4), texto, font=f, fill=cor_texto)
    return y + h


def cena_gancho(titulo, destaque):
    t = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    logo_pequeno(t)
    y = texto_linhas(d, quebra(d, titulo, fonte(112), LARGURA), fonte(112), MARGEM, 430)
    if len(destaque) <= 24:
        pilula(d, destaque, fonte(64), MARGEM, y + 30)
    else:
        linhas = quebra(d, destaque, fonte(54, False), LARGURA - 40)
        alt = int(54 * 1.2) * len(linhas)
        d.rounded_rectangle((MARGEM, y + 40, MARGEM + 10, y + 40 + alt), radius=5, fill=AZUL)
        texto_linhas(d, linhas, fonte(54, False), MARGEM + 36, y + 40, espaco=1.2)
    return t


def cena_passo(n, titulo, sub=None):
    t = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    logo_pequeno(t)
    y = 1170
    d.ellipse((MARGEM, y, MARGEM + 150, y + 150), fill=AZUL)
    fn = fonte(96)
    d.text((MARGEM + 75, y + 70), str(n), font=fn, fill=BRANCO, anchor='mm')
    y += 190
    y = texto_linhas(d, quebra(d, titulo, fonte(80), LARGURA), fonte(80), MARGEM, y)
    if sub:
        texto_linhas(d, quebra(d, sub, fonte(46, False), LARGURA), fonte(46, False), MARGEM, y + 14)
    return t


def cena_nota(frase, pergunta, aviso):
    t = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    logo_pequeno(t)
    y = texto_linhas(d, quebra(d, frase, fonte(70), LARGURA), fonte(70), MARGEM, 700)
    pilula(d, pergunta, fonte(64), MARGEM, y + 40)
    texto_linhas(d, quebra(d, aviso, fonte(30, False), LARGURA), fonte(30, False), MARGEM, 1560)
    return t


def cena_frase(frase, sub=None, aviso=None):
    t = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    logo_pequeno(t)
    y = texto_linhas(d, quebra(d, frase, fonte(78), LARGURA), fonte(78), MARGEM, 720)
    if sub:
        d.rounded_rectangle((MARGEM, y + 40, MARGEM + 10, y + 40 + int(52 * 1.25) * len(quebra(d, sub, fonte(52, False), LARGURA - 40))), radius=5, fill=AZUL)
        texto_linhas(d, quebra(d, sub, fonte(52, False), LARGURA - 40), fonte(52, False), MARGEM + 36, y + 40, espaco=1.25)
    if aviso:
        texto_linhas(d, quebra(d, aviso, fonte(30, False), LARGURA), fonte(30, False), MARGEM, 1540)
    return t


def cena_cta(palavra):
    t = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    lg = Image.open(LOGO).convert('RGBA')
    lg = lg.resize((820, int(lg.height * 820 / lg.width)), Image.LANCZOS)
    t.alpha_composite(lg, ((W - 820) // 2, 480))
    f = fonte(66)
    d.text((W // 2, 880), f'Comenta {palavra}', font=f, fill=BRANCO, anchor='mm')
    d.text((W // 2, 990), 'Cotação grátis no WhatsApp:', font=fonte(44), fill=BRANCO, anchor='mm')
    d.text((W // 2, 1085), TELEFONE, font=fonte(84), fill=AZUL, anchor='mm')
    d.text((W // 2, 1235), '@fabricioquadrata', font=fonte(40, False), fill=BRANCO, anchor='mm')
    return t


def rodar(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-1500:])


def video_cena(bg, texto, dur, saida, zoom='in', fps=30):
    """Foto com zoom lento + texto que entra com fade."""
    frames = int(dur * fps)
    z = ("min(zoom+0.0006,1.14)" if zoom == 'in' else "if(eq(on,0),1.14,max(zoom-0.0006,1.0))")
    filtro = (
        f"[0:v]scale=1620:2880,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={fps}[b];"
        f"[1:v]format=rgba,fade=t=in:st=0.15:d=0.45:alpha=1,fade=t=out:st={dur - 0.3}:d=0.3:alpha=1[t];"
        f"[b][t]overlay=format=auto,format=yuv420p[v]"
    )
    rodar(['ffmpeg', '-y', '-loop', '1', '-i', str(bg), '-loop', '1', '-i', str(texto), '-filter_complex', filtro,
           '-map', '[v]', '-t', str(dur), '-r', str(fps), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
           '-pix_fmt', 'yuv420p', str(saida)])


REELS = {
    'alagou': {
        'foto': 'reels/fotos/alagou.jpg',
        'cenas': [
            ('gancho', dict(titulo='Seu carro alagou?', destaque='NÃO ligue o motor.'), 3.4),
            ('passo', dict(n=1, titulo='Não gire a chave', sub='O motor pode ser danificado.'), 3.0),
            ('passo', dict(n=2, titulo='Fotografe tudo', sub='Nível da água, painel e placa.'), 3.0),
            ('passo', dict(n=3, titulo='Chame o guincho'), 2.8),
            ('passo', dict(n=4, titulo='Avise a seguradora ou a corretora'), 3.0),
            ('nota', dict(frase='Alagamento costuma estar na cobertura compreensiva, mas depende da apólice.',
                          pergunta='Quer saber o seu?',
                          aviso='Coberturas variam conforme a apólice contratada.'), 4.0),
            ('cta', dict(palavra='COTAR'), 4.2),
        ],
    },
}


REELS['renda'] = {
    'foto': 'reels/fotos/familia.jpg',
    'cenas': [
        ('gancho', dict(titulo='Se a sua renda parasse amanhã...', destaque='Quanto tempo a sua família pagaria as contas?'), 3.8),
        ('frase', dict(frase='Aluguel. Escola. Mercado.', sub='As contas não param quando a renda para.'), 3.6),
        ('frase', dict(frase='O seguro de vida ajuda a manter a rotina de quem você ama de pé.'), 3.8),
        ('frase', dict(frase='Quer saber quanto custa proteger a sua família?',
                       aviso='Valores sujeitos a análise de perfil e condições da seguradora. Coberturas variam conforme a apólice.'), 4.0),
        ('cta', dict(palavra='COTAR'), 4.2),
    ],
}
REELS['3perguntas'] = {
    'foto': 'reels/fotos/perguntas.jpg',
    'cenas': [
        ('gancho', dict(titulo='Antes de cotar o seu seguro,', destaque='responda 3 coisas.'), 3.4),
        ('passo', dict(n=1, titulo='Quem dirige o carro e onde ele dorme?'), 3.4),
        ('passo', dict(n=2, titulo='Qual franquia cabe no seu bolso?'), 3.2),
        ('passo', dict(n=3, titulo='Quais coberturas você não abre mão?'), 3.2),
        ('frase', dict(frase='Com isso, a cotação sai certeira e sem surpresa.'), 3.4),
        ('cta', dict(palavra='COTAR'), 4.2),
    ],
}
REELS['moto'] = {
    'foto': 'reels/fotos/moto.jpg',
    'cenas': [
        ('gancho', dict(titulo='Tem moto?', destaque='Evite estes 3 erros.'), 3.2),
        ('passo', dict(n=1, titulo='Deixar a moto sem proteção contra furto e roubo'), 3.6),
        ('passo', dict(n=2, titulo='Contratar sem ler o que a apólice cobre'), 3.4),
        ('passo', dict(n=3, titulo='Esquecer de atualizar o perfil de uso', sub='Trabalho ou lazer?'), 3.4),
        ('frase', dict(frase='Moto é ferramenta de trabalho para muita gente.', sub='Proteja.'), 3.6),
        ('cta', dict(palavra='COTAR'), 4.2),
    ],
}


def montar(nome):
    cfg = REELS[nome]
    saida = RAIZ / 'reels/saida'
    saida.mkdir(parents=True, exist_ok=True)
    foto = RAIZ / cfg['foto']
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        partes = []
        for i, (tipo, args, dur) in enumerate(cfg['cenas']):
            if tipo == 'cta':
                bg = fundo(foto, 0.80, 0.0, 0.1)
            elif tipo in ('nota', 'frase'):
                bg = fundo(foto, 0.55, 0.3, 0.4)
            elif tipo == 'gancho':
                bg = fundo(foto, 0.12, 0.65, 0.55)
            else:
                bg = fundo(foto, 0.18, 0.40, 0.80)
            bg.save(tmp / f'bg{i}.png')
            txt = {'gancho': cena_gancho, 'passo': cena_passo, 'nota': cena_nota, 'frase': cena_frase, 'cta': cena_cta}[tipo](**args)
            txt.save(tmp / f't{i}.png')
            video_cena(tmp / f'bg{i}.png', tmp / f't{i}.png', dur, tmp / f'c{i}.mp4', 'in' if i % 2 == 0 else 'out')
            partes.append(tmp / f'c{i}.mp4')
        lista = tmp / 'lista.txt'
        lista.write_text(''.join(f"file '{p}'\n" for p in partes))
        sem_audio = tmp / 'junto.mp4'
        rodar(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(lista), '-c', 'copy', str(sem_audio)])
        final = saida / f'{nome}.mp4'
        # faixa de áudio silenciosa (o Instagram aceita; troque por um áudio em alta ao postar)
        rodar(['ffmpeg', '-y', '-i', str(sem_audio), '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
               '-c:v', 'copy', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(final)])
    print('OK:', final)


if __name__ == '__main__':
    montar(sys.argv[1] if len(sys.argv) > 1 else 'alagou')
