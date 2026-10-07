# Instagram @fabricioquadrata — Quadrata Seguros

## Idioma (regra obrigatória)
- Sempre responder, criar slides, legendas e tudo mais em **português do Brasil**, com linguagem natural de corretor de seguros.
- Nunca usar inglês, a não ser em nomes técnicos (ex.: nomes de arquivos, comandos, "WhatsApp", "direct").

Esta pasta publica posts no Instagram **@fabricioquadrata**.

## Quem é o Fabrício
- Consultor **digital** da Quadrata Seguros, atende **online 24 horas**.
- Integrado ao WhatsApp **(11) 98678-0000**, que responde automaticamente.
- Resolve: cotação de seguros, dúvidas sobre apólice, renovação e orientação em caso de sinistro.
- Tom: próximo, direto, sem "juridiquês". Frases curtas. Sempre terminar com chamada para WhatsApp ou direct.

## Identidade visual
- Logo: `marca/logo_quadrata.png` (fundo transparente)
- Azul: `#248AFF` · Marinho: `#0B2748` · Branco `#FFFFFF`
- Fonte: Poppins (Bold para títulos, Medium/Regular para texto)
- Formato: carrossel 1080×1350 (retrato), JPG, 2 a 10 slides
- Rodapé de todo slide: `@fabricioquadrata`
- Referência de layout: `marca/exemplo_gerador_carrossel.py` (ajustar caminhos antes de usar)

## Estrutura
```
posts/
  001_apresentacao_fabricio/
    slide1.jpg, slide2.jpg, ...   (numerados na ordem)
    legenda.txt                    (UTF-8, com hashtags no final)
    PUBLICAR.bat                   (dois cliques publica este post)
    PUBLICADO.txt                  (criado automaticamente depois de publicar)
scripts/
  publish_instagram.py   (API graph.instagram.com)
  publicar_pasta.py      (publica uma pasta de posts/)
  testar_conexao.py
credenciais.txt          (token — NUNCA enviar ao GitHub nem mostrar em chat)
inspiracao/              (peças de referência de outras marcas, ver LEIA-ME.txt; nunca publicar nem copiar logo/texto)
```

## Como criar um post novo
1. Criar a pasta `posts/NNN_tema_curto` (próximo número livre).
2. Gerar os slides `slide1.jpg`... e a `legenda.txt` seguindo a identidade acima.
3. Copiar o `PUBLICAR.bat` de outro post para a pasta nova.
4. **Mostrar os slides e a legenda para aprovação.** Nunca publicar sem o "ok" explícito.

## Como publicar
`python scripts/publicar_pasta.py posts/NNN_tema` (pede confirmação "S"), ou dois cliques no `PUBLICAR.bat` da pasta.

## Publicação automática
- `agenda.txt` lista data, hora (Brasília) e pasta. Um **Cron Job no Render** (`render.yaml`, serviço `fabricio-instagram-agenda`, separado do robô de mensagens) roda `scripts/publicar_agenda.py` a cada 15 min.
- Regras: só entre 10:00 e 21:30, no máximo 1 post por dia. Antes de publicar consulta o Instagram; se a legenda já está no perfil, não repete. Se não conseguir consultar, não publica.
- O Render lê os arquivos do GitHub: **post novo ou agenda nova só vale depois do `git push`**. `credenciais.txt` está no `.gitignore`; o token fica nas variáveis de ambiente do Render.
- Usar só UM agendador (Render). `INSTALAR_AGENDADOR.bat` (Windows) é plano B; se instalado, desligar com `DESINSTALAR_AGENDADOR.bat`.
- **Só colocar na agenda posts que o usuário já aprovou.**
- Ver a fila: `python scripts/publicar_agenda.py --status`.

## Cuidados
- O token em `credenciais.txt` é o MESMO usado pelo robô de mensagens no Render. Vence em **27/11/2026**; ao renovar, atualizar aqui e no Render.
- Não mexer na pasta da Mariana (`..\`) nem nas configurações de webhook.
- Pastas com `PUBLICADO.txt` já foram ao ar; não publicar de novo.
