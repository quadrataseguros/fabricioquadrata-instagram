from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
BLUE=(36,138,255); NAVY=(11,39,72); WHITE=(255,255,255); LIGHT=(234,243,255)
F='/usr/share/fonts/truetype/google-fonts/Poppins-'
def f(w,s): return ImageFont.truetype(F+w+'.ttf',s)
logo=Image.open('/root/.claude/uploads/8a7d49de-92fd-5ae3-ae86-ad7f8d856447/2bd38042-image.png').convert('RGBA')
bb=logo.getbbox(); logo=logo.crop(bb)
icon=logo.crop((0,0,logo.width,int(logo.height*0.70)))  # só o símbolo
icon=icon.crop(icon.getbbox())
def paste(img,src,w,xy):
    s=src.resize((w,int(src.height*w/src.width)),Image.LANCZOS); img.paste(s,xy,s); return s.size
def ctext(d,y,t,font,fill):
    w=d.textlength(t,font=font); d.text(((W-w)/2,y),t,font=font,fill=fill)
def footer(d,fill,dots,active):
    ctext(d,H-95,'@fabricioquadrata',f('Medium',30),fill)
    x0=W/2-(dots*28)/2
    for i in range(dots):
        c=fill if i==active else tuple(int(v*0.45+ (255 if fill!=WHITE else 0)*0) for v in fill)
        d.ellipse((x0+i*28,H-135,x0+i*28+12,H-123),fill=fill if i==active else (fill[0]//2+60,fill[1]//2+60,fill[2]//2+60))

# Slide 1
im=Image.new('RGB',(W,H),WHITE); d=ImageDraw.Draw(im)
d.rectangle((0,0,W,18),fill=BLUE)
sw,sh=paste(im,logo,420,((W-420)//2,130))
y=130+sh+90
ctext(d,y-20,'Conheça o Fabrício',f('Bold',76),NAVY)
ctext(d,y+80,'seu consultor digital',f('Bold',76),BLUE)
d.rounded_rectangle((W/2-190,y+215,W/2+190,y+290),radius=38,fill=BLUE)
ctext(d,y+226,'Online 24 horas',f('Bold',38),WHITE)
footer(d,NAVY,3,0); im.save('slide1.jpg',quality=92)

# Slide 2
im=Image.new('RGB',(W,H),NAVY); d=ImageDraw.Draw(im)
paste(im,icon,120,(90,110))
d.text((90,290),'O que o Fabrício',font=f('Bold',72),fill=WHITE)
d.text((90,380),'resolve pra você',font=f('Bold',72),fill=BLUE)
items=['Cotação de seguros','Dúvidas sobre sua apólice','Renovação do seguro','Orientação em caso de sinistro','Tudo pelo WhatsApp, a qualquer hora']
y=540
for it in items:
    d.rounded_rectangle((90,y,W-90,y+100),radius=24,fill=(20,55,98))
    d.ellipse((125,y+34,157,y+66),fill=BLUE)
    d.text((190,y+22),it,font=f('Medium',36),fill=WHITE)
    y+=122
footer(d,WHITE,3,1); im.save('slide2.jpg',quality=92)

# Slide 3
im=Image.new('RGB',(W,H),BLUE); d=ImageDraw.Draw(im)
card=Image.new('RGBA',(360,360),(0,0,0,0)); cd=ImageDraw.Draw(card); cd.rounded_rectangle((0,0,359,359),radius=60,fill=WHITE)
im.paste(card,((W-360)//2,170),card); paste(im,icon,250,((W-250)//2,225))
ctext(d,590,'Fale com o Fabrício',f('Bold',76),WHITE)
ctext(d,685,'agora mesmo',f('Bold',76),NAVY)
ctext(d,835,'WhatsApp',f('Medium',38),WHITE)
d.rounded_rectangle((150,895,W-150,1015),radius=60,fill=NAVY)
ctext(d,915,'(11) 98678-0000',f('Bold',56),WHITE)
ctext(d,1050,'ou chama no direct',f('Medium',36),WHITE)
footer(d,WHITE,3,2); im.save('slide3.jpg',quality=92)
