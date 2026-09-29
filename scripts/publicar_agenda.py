"""
publicar_agenda.py — publica sozinho os posts da agenda.txt no horário marcado.
Roda como Cron Job no Render a cada 15 minutos (ou no Agendador do Windows).

Regras de segurança:
- Só publica entre 10:00 e 21:30 (horário de Brasília).
- No máximo 1 post por dia.
- Antes de publicar, consulta o próprio Instagram: se a legenda já está no
  perfil, não publica de novo. Se não conseguir consultar, não publica.

Uso manual:
  python scripts/publicar_agenda.py --status   (mostra a fila, não publica)
"""
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AGENDA = RAIZ / 'agenda.txt'
LOG = RAIZ / 'agenda_log.txt'
BRASILIA = timezone(timedelta(hours=-3))  # o Brasil não tem mais horário de verão
JANELA = (time(10, 0), time(21, 30))

if sys.stdout is None:  # rodando sem janela (pythonw no Windows): grava em arquivo
    sys.stdout = sys.stderr = open(LOG, 'a', encoding='utf-8')

sys.path.insert(0, str(RAIZ / 'scripts'))
import requests
import publish_instagram as ig


def agora_br():
    return datetime.now(BRASILIA).replace(tzinfo=None)


def ler_agenda():
    itens = []
    for linha in AGENDA.read_text(encoding='utf-8').splitlines():
        linha = linha.strip()
        if not linha or linha.startswith('#'):
            continue
        data, hora, pasta = linha.split(maxsplit=2)
        itens.append((datetime.strptime(f'{data} {hora}', '%Y-%m-%d %H:%M'), RAIZ / 'posts' / pasta))
    return sorted(itens)


def normaliza(txt):
    return ' '.join((txt or '').split())[:80]


def posts_do_perfil():
    """Últimos posts do Instagram: [(data_brasilia, inicio_da_legenda)]. Lança erro se falhar."""
    r = requests.get(f'{ig.BASE_URL}/{ig.IG_ID}/media',
                     params={'fields': 'caption,timestamp', 'limit': 40, 'access_token': ig.TOKEN}, timeout=30)
    dados = r.json()
    if 'data' not in dados:
        raise RuntimeError(f'Não consegui consultar o Instagram: {dados}')
    return [(datetime.strptime(m['timestamp'], '%Y-%m-%dT%H:%M:%S%z').astimezone(BRASILIA).date(),
             normaliza(m.get('caption'))) for m in dados['data']]


def ja_no_perfil(pasta, perfil):
    leg = pasta / 'legenda.txt'
    return leg.exists() and normaliza(leg.read_text(encoding='utf-8')) in {c for _, c in perfil}


def status():
    agora = agora_br()
    perfil = posts_do_perfil()
    for quando, pasta in ler_agenda():
        if not pasta.is_dir(): st = 'PASTA NÃO ENCONTRADA'
        elif ja_no_perfil(pasta, perfil): st = 'publicado'
        elif quando <= agora: st = 'atrasado (sai na próxima janela)'
        else: st = 'aguardando'
        print(f'{quando:%d/%m %H:%M}  {pasta.name:<32} {st}')


def main():
    agora = agora_br()
    if not (JANELA[0] <= agora.time() <= JANELA[1]):
        return
    vencidos = [(q, p) for q, p in ler_agenda() if q <= agora]
    if not vencidos:
        return
    try:
        perfil = posts_do_perfil()
    except Exception as e:
        print(f'{agora:%d/%m %H:%M} {e}. Nada publicado.'); return
    if any(d == agora.date() for d, _ in perfil):
        return  # já saiu um post hoje
    pendentes = [(q, p) for q, p in vencidos if p.is_dir() and not ja_no_perfil(p, perfil)]
    if not pendentes:
        return
    quando, pasta = pendentes[0]

    print(f'\n=== {agora:%d/%m/%Y %H:%M} — publicando {pasta.name} (marcado para {quando:%d/%m %H:%M}) ===')
    slides = sorted(pasta.glob('slide*.jpg'), key=lambda p: int(''.join(c for c in p.stem if c.isdigit()) or 0))
    legenda = (pasta / 'legenda.txt').read_text(encoding='utf-8').strip()
    try:
        ig.run([str(s) for s in slides], legenda)
    except SystemExit:
        print('FALHOU (ver mensagem acima). Tenta de novo em 15 minutos.'); return
    except Exception as e:
        print(f'FALHOU: {type(e).__name__}: {e}. Tenta de novo em 15 minutos.'); return
    (pasta / 'PUBLICADO.txt').write_text(f'Publicado em {agora:%d/%m/%Y %H:%M}\n', encoding='utf-8')
    print('OK, publicado.')


if __name__ == '__main__':
    status() if '--status' in sys.argv else main()
