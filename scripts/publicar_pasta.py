"""
publicar_pasta.py — publica um post a partir de uma pasta em posts/.
A pasta precisa ter: slide1.jpg, slide2.jpg... (2 a 10) e legenda.txt
Uso: python scripts/publicar_pasta.py posts/001_nome_do_post
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import publish_instagram as ig

pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if not pasta or not pasta.is_dir():
    print("ERRO: informe a pasta do post. Ex: posts/001_apresentacao_fabricio")
    sys.exit(1)

marcador = pasta / "PUBLICADO.txt"
if marcador.exists():
    print("Este post ja foi publicado:", marcador.read_text(encoding="utf-8").strip())
    sys.exit(0)

slides = sorted(pasta.glob("slide*.jpg"), key=lambda p: int("".join(c for c in p.stem if c.isdigit()) or 0))
legenda = (pasta / "legenda.txt").read_text(encoding="utf-8").strip()
print(f"Post: {pasta.name}")
print(f"Slides: {len(slides)}  |  Legenda: {len(legenda)} caracteres")

if input("\nPublicar AGORA no Instagram? Digite S e Enter para confirmar: ").strip().upper() != "S":
    print("Cancelado. Nada foi publicado.")
    sys.exit(0)

ig.run([str(s) for s in slides], legenda)

from datetime import datetime
marcador.write_text(f"Publicado em {datetime.now():%d/%m/%Y %H:%M}\n", encoding="utf-8")
