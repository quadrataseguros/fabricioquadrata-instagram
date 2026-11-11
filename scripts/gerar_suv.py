"""
gerar_suv.py — clipe vertical 9:16 do SUV da Quadrata (movimento de câmera, feixe de luz, tela final com CTA).
Uso: python scripts/gerar_suv.py     Saída: videos/suv_quadrata.mp4
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_reels as g

RAIZ = g.RAIZ
W, H = 1080, 1920
D1, D2 = 7.0, 4.0


def rodar(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-1500:])


def fundo_azul():
    suv = Image.open(RAIZ / 'marca/suv_quadrata.jpg').convert('RGB').crop((0, 0, 1080, 418))
    bg = suv.resize((int(W * 1.6), int(H * 1.0)), Image.LANCZOS).crop((300, 0, 300 + W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(40))
    a = np.asarray(bg).astype(np.float32)
    azul = np.array(g.MARINHO, dtype=np.float32)
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    alpha = 0.80 + 0.12 * np.abs(y - 0.5) * 2
    return Image.fromarray((a * (1 - alpha) + azul * alpha).astype(np.uint8))


def carro_suave():
    suv = Image.open(RAIZ / 'marca/suv_quadrata.jpg').convert('RGB').crop((0, 0, 1080, 418))
    suv = suv.resize((1700, int(418 * 1700 / 1080)), Image.LANCZOS)
    w, h = suv.size
    m = np.ones((h, w), dtype=np.float32)
    f = 90
    for i in range(f):  # borda suave
        k = (i / f) ** 1.5
        m[i, :] = np.minimum(m[i, :], k)
        m[h - 1 - i, :] = np.minimum(m[h - 1 - i, :], k)
        m[:, i] = np.minimum(m[:, i], k)
        m[:, w - 1 - i] = np.minimum(m[:, w - 1 - i], k)
    rgba = suv.convert('RGBA')
    rgba.putalpha(Image.fromarray((m * 255).astype(np.uint8)))
    return rgba


def feixe():
    img = Image.new('RGBA', (420, 800), (0, 0, 0, 0))
    px = np.zeros((800, 420, 4), dtype=np.float32)
    xx = np.arange(420)[None, :]
    yy = np.arange(800)[:, None]
    centro = 210 - (yy - 400) * 0.45  # diagonal
    dist = np.abs(xx - centro)
    a = np.clip(1 - dist / 110, 0, 1) ** 2
    a = a * np.sin(np.clip(yy / 800, 0, 1) * np.pi) ** 1.5
    px[..., 0], px[..., 1], px[..., 2] = 215, 235, 255
    px[..., 3] = a * 190
    return Image.fromarray(px.astype(np.uint8))


def texto_cena1():
    t = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    y = g.texto_linhas(d, g.quebra(d, 'Proteção 24h, onde você estiver.', g.fonte(100), 900), g.fonte(100), 90, 250)
    g.pilula(d, 'Atendimento digital', g.fonte(54), 90, y + 30)
    d.text((W // 2, 1560), 'Quadrata Seguros', font=g.fonte(56), fill=g.BRANCO, anchor='mm')
    d.text((W // 2, 1630), '@fabricioquadrata', font=g.fonte(38, False), fill=g.BRANCO, anchor='mm')
    return t


def cena2():
    bg = Image.new('RGB', (W, H), g.MARINHO)
    lg = Image.open(RAIZ / 'marca/logo_digital.jpg').convert('RGB').resize((900, 900), Image.LANCZOS)
    bg.paste(lg, ((W - 900) // 2, 250))
    d = ImageDraw.Draw(bg)
    d.text((W // 2, 1290), 'Cotação grátis no WhatsApp:', font=g.fonte(50), fill=g.BRANCO, anchor='mm')
    d.text((W // 2, 1395), g.TELEFONE, font=g.fonte(90), fill=g.AZUL, anchor='mm')
    d.text((W // 2, 1520), '@fabricioquadrata', font=g.fonte(42, False), fill=g.BRANCO, anchor='mm')
    return bg


def montar():
    out = RAIZ / 'videos'
    out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        fundo_azul().save(tmp / 'bg.png')
        carro_suave().save(tmp / 'car.png')
        feixe().save(tmp / 'feixe.png')
        texto_cena1().save(tmp / 'txt.png')
        cena2().save(tmp / 'c2.png')
        filtro = (
            "[0:v][1:v]overlay=x='-300-(t/%s)*520':y=760[a];"
            "[a][3:v]overlay=x='-420+(t-2.0)*820':y=640:enable='between(t,2.0,4.8)'[b];"
            "[2:v]format=rgba,fade=t=in:st=0.2:d=0.6:alpha=1[t];"
            "[b][t]overlay,fade=t=in:st=0:d=0.5,fade=t=out:st=%s:d=0.5,format=yuv420p[v]"
        ) % (D1, D1 - 0.5)
        rodar(['ffmpeg', '-y', '-loop', '1', '-i', str(tmp / 'bg.png'), '-loop', '1', '-i', str(tmp / 'car.png'),
               '-loop', '1', '-i', str(tmp / 'txt.png'), '-loop', '1', '-i', str(tmp / 'feixe.png'),
               '-filter_complex', filtro, '-map', '[v]', '-t', str(D1), '-r', '30', '-c:v', 'libx264',
               '-crf', '18', '-pix_fmt', 'yuv420p', str(tmp / 's1.mp4')])
        rodar(['ffmpeg', '-y', '-loop', '1', '-i', str(tmp / 'c2.png'), '-vf',
               f"fade=t=in:st=0:d=0.5,fade=t=out:st={D2 - 0.4}:d=0.4,format=yuv420p", '-t', str(D2), '-r', '30',
               '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(tmp / 's2.mp4')])
        (tmp / 'l.txt').write_text(f"file '{tmp / 's1.mp4'}'\nfile '{tmp / 's2.mp4'}'\n")
        rodar(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(tmp / 'l.txt'), '-c', 'copy', str(tmp / 'j.mp4')])
        final = out / 'suv_quadrata.mp4'
        rodar(['ffmpeg', '-y', '-i', str(tmp / 'j.mp4'), '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
               '-c:v', 'copy', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(final)])
    print('OK', final)


if __name__ == '__main__':
    montar()
