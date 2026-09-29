"""Testa se o token do @fabricioquadrata funciona (não publica nada)."""
import os, sys, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "credenciais.txt")
TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
VER = os.getenv("META_API_VERSION", "v21.0")

if not TOKEN or TOKEN == "COLE_O_TOKEN_AQUI":
    print("ERRO: cole o token no arquivo credenciais.txt primeiro.")
    sys.exit(1)

r = requests.get(f"https://graph.instagram.com/{VER}/me",
                 params={"fields": "user_id,username,account_type", "access_token": TOKEN},
                 timeout=20).json()
if "error" in r:
    print("ERRO:", r["error"].get("message"))
    sys.exit(1)

print("Conexao OK!")
print("Conta:   @" + r.get("username", "?"))
print("ID:      " + str(r.get("user_id", "?")))
print("Tipo:    " + str(r.get("account_type", "?")))
if r.get("username") != os.getenv("INSTAGRAM_USERNAME"):
    print("ATENCAO: esse token e de outra conta, confira o credenciais.txt")
