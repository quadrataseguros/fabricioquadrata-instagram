"""
publish_instagram.py — Publicação automática no Instagram via Meta Graph API
Gerado pelo setup-instagram skill do Claude Code
API: graph.instagram.com (Instagram Business API v21.0)
"""
import argparse, os, sys, time, requests
from pathlib import Path
from dotenv import load_dotenv

# Encontra o .env (sobe até 3 níveis)
script_dir = Path(__file__).parent
for candidate in [script_dir.parent / "credenciais.txt", script_dir.parent / ".env", script_dir / ".env"]:
    if candidate.exists():
        load_dotenv(candidate)
        break

IG_ID      = os.getenv("INSTAGRAM_BUSINESS_ID")
TOKEN      = os.getenv("INSTAGRAM_ACCESS_TOKEN")
API_VER    = os.getenv("META_API_VERSION", "v21.0")
BASE_URL   = f"https://graph.instagram.com/{API_VER}"


UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}


def _up_uguu(path, name):
    with open(path, "rb") as f:
        r = requests.post("https://uguu.se/upload", files={"files[]": (name, f, "image/jpeg")}, headers=UA, timeout=60)
    return r.json()["files"][0]["url"]


def _up_tmpfiles(path, name):
    with open(path, "rb") as f:
        r = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": (name, f, "image/jpeg")}, headers=UA, timeout=60)
    url = r.json()["data"]["url"]
    return url.replace("://tmpfiles.org/", "://tmpfiles.org/dl/").replace("http://", "https://")


def _up_litterbox(path, name):
    with open(path, "rb") as f:
        r = requests.post("https://litterbox.catbox.moe/resources/internals/api.php",
                          data={"reqtype": "fileupload", "time": "24h"},
                          files={"fileToUpload": (name, f, "image/jpeg")}, headers=UA, timeout=60)
    return r.text.strip()


def _up_catbox(path, name):
    with open(path, "rb") as f:
        r = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"},
                          files={"fileToUpload": (name, f, "image/jpeg")}, headers=UA, timeout=60)
    return r.text.strip()


HOSTS = [("uguu.se", _up_uguu), ("tmpfiles.org", _up_tmpfiles),
         ("litterbox", _up_litterbox), ("catbox", _up_catbox)]


def _is_image(url: str) -> bool:
    try:
        r = requests.get(url, headers=UA, timeout=30, stream=True)
        ok = r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image/")
        r.close()
        return ok
    except Exception:
        return False


def host_image(image_path: str) -> str:
    """Hospeda a imagem num link publico. Tenta varios sites ate um funcionar."""
    name = Path(image_path).name
    for host, fn in HOSTS:
        try:
            url = fn(image_path, name)
        except Exception as e:
            print(f"  {host}: falhou ({type(e).__name__})")
            continue
        if isinstance(url, str) and url.startswith("https://") and _is_image(url):
            print(f"  Hospedada ({host}): {url}")
            return url
        print(f"  {host}: resposta invalida, tentando o proximo...")
    raise RuntimeError("Nenhum site de hospedagem aceitou a imagem. Nada foi publicado.")


def create_media_container(image_url: str) -> str:
    resp = requests.post(f"{BASE_URL}/{IG_ID}/media", data={
        "access_token": TOKEN,
        "image_url": image_url,
        "is_carousel_item": "true",
    }, timeout=60)
    result = resp.json()
    if "id" not in result:
        raise RuntimeError(f"Erro ao criar container: {result}")
    print(f"  Container criado: {result['id']}")
    return result["id"]


def create_single(image_url: str, caption: str) -> str:
    resp = requests.post(f"{BASE_URL}/{IG_ID}/media", data={
        "access_token": TOKEN,
        "image_url": image_url,
        "caption": caption,
    }, timeout=60)
    result = resp.json()
    if "id" not in result:
        raise RuntimeError(f"Erro ao criar post: {result}")
    print(f"  Post criado: {result['id']}")
    return result["id"]


def create_carousel(media_ids: list, caption: str) -> str:
    resp = requests.post(f"{BASE_URL}/{IG_ID}/media", data={
        "access_token": TOKEN,
        "media_type": "CAROUSEL",
        "children": ",".join(media_ids),
        "caption": caption,
    }, timeout=30)
    result = resp.json()
    if "id" not in result:
        raise RuntimeError(f"Erro ao criar carrossel: {result}")
    print(f"  Carrossel criado: {result['id']}")
    return result["id"]


def wait_ready(container_id: str) -> bool:
    for i in range(12):
        resp = requests.get(f"{BASE_URL}/{container_id}",
            params={"fields": "status_code", "access_token": TOKEN}, timeout=15)
        status = resp.json().get("status_code", "")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            raise RuntimeError(f"Erro no processamento: {resp.json()}")
        print(f"  Processando... {i*5}s")
        time.sleep(5)
    return False


def publish(container_id: str) -> str:
    resp = requests.post(f"{BASE_URL}/{IG_ID}/media_publish", data={
        "access_token": TOKEN,
        "creation_id": container_id,
    }, timeout=30)
    result = resp.json()
    if "id" not in result:
        raise RuntimeError(f"Erro ao publicar: {result}")
    return result["id"]


def run(images: list, caption: str, dry_run: bool = False):
    if not IG_ID or not TOKEN:
        print("ERRO: Credenciais não encontradas. Verifique o arquivo .env")
        sys.exit(1)
    if len(images) < 1:
        print("ERRO: Nenhuma imagem encontrada.")
        sys.exit(1)
    if len(images) > 10:
        print("ERRO: Máximo 10 imagens.")
        sys.exit(1)

    print(f"\nPublicando {len(images)} slides no Instagram (@{os.getenv('INSTAGRAM_USERNAME', '?')})...")
    if dry_run:
        print("[DRY RUN] Configuração OK. Remova --dry-run para publicar de verdade.")
        return

    print("\nPasso 1/3 — Hospedando imagens...")
    urls = [host_image(img) for img in images]

    if len(urls) == 1:
        print("\nPasso 2/3 — Criando post de imagem única...")
        container_id = create_single(urls[0], caption)
    else:
        print("\nPasso 2/3 — Criando containers...")
        ids = [create_media_container(url) for url in urls]
        print("\nPasso 3/3 — Montando e publicando carrossel...")
        container_id = create_carousel(ids, caption)

    if not wait_ready(container_id):
        print("ERRO: Timeout no processamento. Tente novamente.")
        sys.exit(1)

    post_id = publish(container_id)
    print(f"\nPublicado com sucesso!")
    print(f"Post ID: {post_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publica imagem única ou carrossel no Instagram")
    parser.add_argument("--images", nargs="+", required=True, help="Caminhos das imagens")
    parser.add_argument("--caption", required=True, help="Legenda do post")
    parser.add_argument("--dry-run", action="store_true", help="Testa sem publicar")
    args = parser.parse_args()
    run(args.images, args.caption, args.dry_run)
