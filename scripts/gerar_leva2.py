"""
gerar_leva2.py — leva 2 de posts (010 a 015), estilo limpo: fundo claro,
muito espaço em branco, uma ideia por slide.
Uso: python scripts/gerar_leva2.py
"""
from pathlib import Path
import shutil, urllib.request
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
W, H, M = 1080, 1350, 96
BG = (250, 251, 253); NAVY = (11, 39, 72); BLUE = (36, 138, 255)
GRAY = (95, 110, 130); LINE = (226, 232, 240)
FONE = '(11) 98678-0000'

FONTS = RAIZ / 'marca' / 'fonts'
FONTS.mkdir(parents=True, exist_ok=True)
for w in ('Bold', 'Medium', 'Regular'):
    p = FONTS / f'Poppins-{w}.ttf'
    if not p.exists():
        urllib.request.urlretrieve(f'https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-{w}.ttf', p)
def f(w, s): return ImageFont.truetype(str(FONTS / f'Poppins-{w}.ttf'), s)

logo = Image.open(RAIZ / 'marca' / 'logo_quadrata.png').convert('RGBA')
logo = logo.crop(logo.getbbox())
icon = logo.crop((0, 0, logo.width, int(logo.height * 0.70))); icon = icon.crop(icon.getbbox())
icon = icon.resize((60, int(icon.height * 60 / icon.width)), Image.LANCZOS)


def wrap(d, text, font, maxw):
    linhas, atual = [], ''
    for p in text.split():
        t = (atual + ' ' + p).strip()
        if d.textlength(t, font=font) <= maxw: atual = t
        else: linhas.append(atual); atual = p
    return linhas + [atual]


def base(n, total):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    im.paste(icon, (M, 88), icon)
    t = f'{n}/{total}'; fo = f('Medium', 26)
    d.text((W - M - d.textlength(t, font=fo), 100), t, font=fo, fill=GRAY)
    d.text((M, H - 118), '@fabricioquadrata', font=f('Medium', 26), fill=GRAY)
    if n < total:
        # seta desenhada à mão (a Poppins não tem o caractere →)
        xa = W - M; ya = H - 100
        d.line((xa - 34, ya, xa - 2, ya), fill=BLUE, width=3)
        d.polygon([(xa, ya), (xa - 12, ya - 9), (xa - 12, ya + 9)], fill=BLUE)
        t = 'arrasta'; d.text((xa - 48 - d.textlength(t, font=fo), H - 118), t, font=fo, fill=BLUE)
    return im, d


def titulo(d, y, texto, tam, azul_ultima=False):
    fo = f('Bold', tam); lh = int(tam * 1.18)
    linhas = []
    for parte in texto if isinstance(texto, list) else [texto]:
        linhas += wrap(d, parte, fo, W - 2 * M)
    for i, l in enumerate(linhas):
        cor = BLUE if azul_ultima and i == len(linhas) - 1 else NAVY
        d.text((M, y), l, font=fo, fill=cor); y += lh
    return y


def paragrafos(d, y, paras):
    for p in paras:
        estilo, txt = (p[0], p[1:]) if p[:1] in '*!' else ('', p)
        fo = f('Bold', 40) if estilo else f('Regular', 38)
        cor = BLUE if estilo == '!' else NAVY
        for l in wrap(d, txt, fo, W - 2 * M):
            d.text((M, y), l, font=fo, fill=cor); y += 58
        y += 30
    return y


def s_capa(n, tot, s):
    im, d = base(n, tot)
    d.text((M, 360), s['tag'], font=f('Medium', 28), fill=BLUE)
    y = titulo(d, 410, s['titulo'], 84, azul_ultima=True)
    if s.get('sub'):
        d.rectangle((M, y + 30, M + 80, y + 36), fill=BLUE)
        for l in wrap(d, s['sub'], f('Regular', 36), W - 2 * M):
            d.text((M, y + 70), l, font=f('Regular', 36), fill=GRAY); y += 52
    return im


def s_texto(n, tot, s):
    im, d = base(n, tot)
    y = titulo(d, 300, s['titulo'], 62)
    d.rectangle((M, y + 26, M + 80, y + 32), fill=BLUE)
    paragrafos(d, y + 80, s['paras'])
    return im


def s_lista(n, tot, s):
    im, d = base(n, tot)
    y = titulo(d, 260, s['titulo'], 62) + 40
    for i, (t, sub) in enumerate(s['itens'], 1):
        d.line((M, y, W - M, y), fill=LINE, width=2); y += 36
        d.text((M, y), f'{i:02d}', font=f('Bold', 38), fill=BLUE)
        for l in wrap(d, t, f('Medium', 38), W - 2 * M - 90):
            d.text((M + 90, y), l, font=f('Medium', 38), fill=NAVY); y += 54
        if sub:
            for l in wrap(d, sub, f('Regular', 31), W - 2 * M - 90):
                d.text((M + 90, y + 2), l, font=f('Regular', 31), fill=GRAY); y += 44
        y += 30
    return im


def s_cta(n, tot, s):
    im, d = base(n, tot)
    y = titulo(d, 330, s['titulo'], 72, azul_ultima=True)
    for l in wrap(d, s['texto'], f('Regular', 36), W - 2 * M):
        d.text((M, y + 30), l, font=f('Regular', 36), fill=GRAY); y += 52
    y += 120
    d.text((M, y), 'WhatsApp 24h', font=f('Medium', 30), fill=BLUE)
    d.text((M, y + 45), FONE, font=f('Bold', 72), fill=NAVY)
    d.rectangle((M, y + 150, M + 80, y + 156), fill=BLUE)
    d.text((M, y + 185), 'ou chama no direct', font=f('Regular', 32), fill=GRAY)
    return im


TIPOS = {'capa': s_capa, 'texto': s_texto, 'lista': s_lista, 'cta': s_cta}

POSTS = {
'010_chuva_alagamento': ([
    dict(t='capa', tag='SEGURO AUTO', titulo=['Chuva forte:', 'seu seguro cobre', 'alagamento?'],
         sub='A resposta está na sua apólice.'),
    dict(t='texto', titulo='Depende da cobertura', paras=[
        'Na cobertura compreensiva, que é a mais completa, alagamento e enchente costumam estar incluídos.',
        'Se o seu seguro é só contra roubo ou só para terceiros, o carro alagado fica sem cobertura.']),
    dict(t='lista', titulo='Se o carro alagar', itens=[
        ('Não tente ligar o motor', 'Isso pode causar um estrago ainda maior.'),
        ('Fotografe o local e a água', 'As fotos ajudam na hora do aviso.'),
        ('Chame a assistência 24h', 'O guincho leva o carro com segurança.'),
        ('Avise o Fabrício', 'Ele orienta o passo a passo do sinistro.')]),
    dict(t='cta', titulo=['Não sabe o que o', 'seu seguro cobre?'],
         texto='Chama o Fabrício que ele confere com você.'),
], """Choveu forte e a rua virou rio? 🌧️🚗

Muita gente só descobre na hora do aperto que o seguro não cobre alagamento. Isso depende do tipo de cobertura que você contratou.

Na cobertura compreensiva, alagamento e enchente costumam estar incluídos. Seguro só contra roubo ou só para terceiros não cobre.

E se o carro alagar: não tente ligar o motor, fotografe tudo, chame o guincho e avise a gente.

📲 Quer saber o que o seu seguro cobre? Chama o Fabrício no WhatsApp 24h: (11) 98678-0000
Ou manda um direct.

#seguroauto #chuva #alagamento #enchente #segurodecarro #dicasdeseguro #quadrataseguros #corretoradeseguros"""),

'011_o_que_e_franquia': ([
    dict(t='capa', tag='SEGURO AUTO', titulo=['Franquia:', 'o que é e quando', 'você paga'],
         sub='Explicado sem complicação.'),
    dict(t='texto', titulo='O que é franquia', paras=[
        'É a parte do conserto que fica por sua conta quando o carro tem um dano parcial.',
        'A seguradora paga o restante.']),
    dict(t='texto', titulo='Na prática', paras=[
        'Conserto: R$ 6.000', 'Franquia: R$ 3.000',
        '!Você paga R$ 3.000.', '!O seguro paga R$ 3.000.']),
    dict(t='lista', titulo='Bom saber', itens=[
        ('Roubo e perda total não têm franquia', 'A indenização segue o que está na apólice.'),
        ('Franquia maior, parcela menor', 'E o contrário também vale.'),
        ('Dá pra escolher', 'O Fabrício compara as opções com você.')]),
    dict(t='cta', titulo=['Qual franquia', 'vale a pena pra você?'],
         texto='O Fabrício simula as opções sem compromisso.'),
], """Você sabe o que é franquia? 🤔

É a parte do conserto que fica por sua conta quando o carro tem um dano parcial. O resto, a seguradora paga.

Exemplo: conserto de R$ 6.000 com franquia de R$ 3.000. Você paga R$ 3.000 e o seguro paga R$ 3.000.

Em roubo e perda total não tem franquia. E quanto maior a franquia, menor a parcela do seguro.

📲 Quer comparar as opções? Chama o Fabrício no WhatsApp 24h: (11) 98678-0000
Ou manda um direct.

Salva pra não esquecer 📌

#seguroauto #franquia #segurodecarro #dicasdeseguro #educacaofinanceira #quadrataseguros #corretoradeseguros"""),

'012_mitos_seguro_de_vida': ([
    dict(t='capa', tag='SEGURO DE VIDA', titulo=['3 mitos que', 'deixam você', 'sem proteção']),
    dict(t='texto', titulo='Mito 1: “É caro”', paras=[
        'Tem seguro de vida que custa menos que uma pizza por mês.',
        'O valor depende da sua idade e da cobertura que você escolhe.']),
    dict(t='texto', titulo='Mito 2: “Só serve depois que eu morrer”', paras=[
        'Muitos planos cobrem invalidez e doenças graves.',
        'Ou seja: o seguro pode ajudar você em vida também.']),
    dict(t='texto', titulo='Mito 3: “Já tenho pelo trabalho”', paras=[
        'O seguro da empresa costuma acabar quando você sai do emprego.',
        'E o valor nem sempre é suficiente pra sua família.']),
    dict(t='cta', titulo=['Quanto custa', 'pra você?'],
         texto='A cotação é rápida e sem compromisso.'),
], """3 mitos sobre seguro de vida que muita gente ainda acredita 👇

1️⃣ "É caro." Tem plano que custa menos que uma pizza por mês.
2️⃣ "Só serve depois que eu morrer." Muitos planos cobrem invalidez e doenças graves.
3️⃣ "Já tenho pelo trabalho." Esse seguro costuma acabar quando você sai da empresa.

Qual desses você já ouviu? Conta aqui nos comentários.

📲 Faz sua cotação com o Fabrício no WhatsApp 24h: (11) 98678-0000
Ou manda um direct.

#segurodevida #mitos #protecaofamiliar #familia #planejamentofinanceiro #quadrataseguros #corretoradeseguros"""),

'013_antes_de_renovar': ([
    dict(t='capa', tag='RENOVAÇÃO', titulo=['Seu seguro', 'vence este mês?'],
         sub='Confere estas 3 coisas antes de renovar.'),
    dict(t='lista', titulo='Antes de renovar', itens=[
        ('Seu bônus', 'Um ano sem sinistro vira desconto na renovação.'),
        ('Seus dados', 'Mudou de endereço ou tem condutor novo? Atualize.'),
        ('Outras seguradoras', 'Renovar no automático nem sempre é o melhor preço.')]),
    dict(t='texto', titulo='Não deixa vencer', paras=[
        'Com o seguro vencido, o carro fica sem proteção.',
        'E se passar do prazo, você pode perder o bônus que juntou.']),
    dict(t='cta', titulo=['O Fabrício compara', 'pra você'],
         texto='Manda a placa e a data de vencimento no WhatsApp.'),
], """Seu seguro vence este mês? 📅

Antes de renovar no automático, confere 3 coisas:

✅ Seu bônus: um ano sem sinistro vira desconto
✅ Seus dados: endereço e condutores atualizados
✅ Outras seguradoras: às vezes dá pra pagar menos pela mesma proteção

E não deixa vencer. Além de ficar sem proteção, você pode perder o bônus que juntou.

📲 Manda a placa e a data de vencimento pro Fabrício no WhatsApp 24h: (11) 98678-0000
Ou manda um direct.

#renovacao #seguroauto #bonus #segurodecarro #dicasdeseguro #quadrataseguros #corretoradeseguros"""),

'014_mora_de_aluguel': ([
    dict(t='capa', tag='SEGURO RESIDENCIAL', titulo=['Mora de', 'aluguel?'],
         sub='Suas coisas também podem ter seguro.'),
    dict(t='texto', titulo='O imóvel é do dono. As coisas são suas.', paras=[
        'Móveis, eletrônicos e eletrodomésticos podem ser protegidos com o seguro residencial.',
        'Ele vale pra quem mora de aluguel também.']),
    dict(t='lista', titulo='O que costuma estar incluso', itens=[
        ('Incêndio', ''), ('Roubo e furto', ''), ('Danos elétricos', ''),
        ('Chaveiro, encanador e eletricista', 'Assistência 24h pros imprevistos do dia a dia.')]),
    dict(t='cta', titulo=['Custa menos do', 'que você imagina'],
         texto='Pede sua cotação pro Fabrício.'),
], """Mora de aluguel? Então esse post é pra você 🏠

O imóvel é do dono, mas os móveis, a TV, a geladeira e o notebook são seus. E tudo isso pode ter seguro.

O seguro residencial costuma incluir incêndio, roubo, danos elétricos e assistência 24h com chaveiro, encanador e eletricista.

E custa bem menos do que a maioria das pessoas imagina.

📲 Pede sua cotação pro Fabrício no WhatsApp 24h: (11) 98678-0000
Ou manda um direct.

Marca aquele amigo que mora de aluguel 👇

#seguroresidencial #aluguel #moradealuguel #casa #apartamento #quadrataseguros #corretoradeseguros"""),

'015_cotacao_pelo_whatsapp': ([
    dict(t='capa', tag='COMO FUNCIONA', titulo=['Cotação pelo', 'WhatsApp em', '3 passos'],
         sub='Sem ligação, sem fila, a qualquer hora.'),
    dict(t='lista', titulo='É assim:', itens=[
        ('Manda um oi', f'No {FONE}, a qualquer hora do dia.'),
        ('Responde umas perguntas', 'Coisas simples, como CEP e dados do que você quer proteger.'),
        ('Recebe as opções', 'E escolhe a que cabe no seu bolso.')]),
    dict(t='cta', titulo=['Bora testar?'], texto='Manda um oi agora mesmo.'),
], """Fazer cotação de seguro não precisa ser chato 😉

Com o Fabrício é pelo WhatsApp, em 3 passos:
1️⃣ Manda um oi
2️⃣ Responde umas perguntas simples
3️⃣ Recebe as opções e escolhe a que cabe no seu bolso

Sem ligação, sem fila, a qualquer hora do dia ou da noite.

📲 WhatsApp 24h: (11) 98678-0000
Ou manda um direct.

#cotacao #seguro #whatsapp #atendimento24h #seguroauto #segurodevida #quadrataseguros #corretoradeseguros"""),
}

bat = RAIZ / 'posts' / '001_apresentacao_fabricio' / 'PUBLICAR.bat'
for pasta, (slides, legenda) in POSTS.items():
    dest = RAIZ / 'posts' / pasta
    if (dest / 'PUBLICADO.txt').exists():
        print('Pulando (já publicado):', pasta); continue
    dest.mkdir(exist_ok=True)
    for i, s in enumerate(slides, 1):
        TIPOS[s['t']](i, len(slides), s).save(dest / f'slide{i}.jpg', quality=93)
    (dest / 'legenda.txt').write_text(legenda + '\n', encoding='utf-8')
    shutil.copy(bat, dest / 'PUBLICAR.bat')
    print(f'OK: {pasta} ({len(slides)} slides)')
