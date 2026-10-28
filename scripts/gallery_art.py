"""Direção editorial reproduzível para a galeria. #Saude #Tecnologia"""
from pathlib import Path
import math
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageEnhance,ImageFilter
import effects

ASSETS=Path(__file__).resolve().parent.parent/'assets'
PALETTE=['#D9B5FF','#FFD883','#8EE7F2','#F4A9BB','#B8EDB0','#FFB08A']
TEXT={
 'noise':'CIÊNCIA|CONSULTA|CLAREZA','lineup':'Ouça|Pergunte|Anote',
 'orbit':'','backdrop-word':'CLAREZA','the-bill':'PARA A CONSULTA|Suas dúvidas|Suas anotações',
 'todo':'Boa pergunta|Escuta atenta|Próximo passo','comment-box':'Qual é sua dúvida?',
 'tap':'Acompanhar|Acompanhando','pause-point':'Guarde esta ideia.',
 'uninstall':'MENOS RUÍDO.','reel-frame':'UMA BOA CONVERSA',
 'shortcut-rain':'Ctrl|C|V|Tab|Shift','reject-stamp':'ANOTE ISSO',
 'cover-star':'OLHAR|Uma ideia muda a conversa', 'scribble':'Pense nisso.',
 'glass-widgets':'CLAREZA|ESCUTA|PRÓXIMO PASSO',
 'red-collage':'CLAREZA|Boa informação.|Boa conversa.',
 'split-headline':'Informação boa.|Conversa melhor.',
 'pastel-word':'CUIDADO|Começa com uma conversa.',
 'check-pills':'Observe|Pergunte|Converse','timeline':'UMA IDEIA DE CADA VEZ',
 'headline-box':'LEVE SUAS|DÚVIDAS.', 'profile-wall':'SUAS IDEIAS',
 'tier-list':'PRIORIDADES|Boa pergunta','broll-split':'MAIS CONTEXTO',
 'phone-fan':'','headline-wall':'OUÇA MAIS.|PERGUNTE MAIS.|ENTENDA MELHOR.',
 'checklist':'Observe|Pergunte|Anote', 'liquid-glass-graph':'ENTENDA A IDEIA',
 'carousel-spin':'','match-cut':'CIÊNCIA','apple-toggles':'Clareza|Contexto|Escuta',
 'led-sign':'BOA|PERGUNTA.', 'over-the-shoulder-zoom':'MAIS CONTEXTO|MAIS CLAREZA',
 'messages':'Uma dúvida?|Vamos conversar.|Anote para a consulta.',
 'place-in-grid':'SUAS IDEIAS', 'idea-scan':'O QUE IMPORTA.',
 'focus-lens':'OLHE DE PERTO.',
 'concept-map':'CONSULTA|Ouvir|Perguntar|Anotar',
 'question-flip':'Por onde começar?|Por uma boa pergunta.',
 'source-pin':'FONTES IMPORTAM.|Sua referência aqui',
 'idea-pulse':'UMA IDEIA POR VEZ.',
}
CARD_EFFECTS={'noise','orbit','phone-fan','carousel-spin','profile-wall','broll-split','place-in-grid'}
COVERS=[('01-olhar','OLHAR','Informação clara.',(107,177,185),(12,33,41),'eye'),
 ('02-conversa','CONVERSA','Começa com uma pergunta.',(187,155,224),(34,20,65),'chat'),
 ('03-ciencia','CIÊNCIA','Pergunte por quê.',(233,184,107),(40,33,25),'orbit'),
 ('04-rotina','ROTINA','Conheça seus hábitos.',(145,199,185),(18,48,49),'moon'),
 ('05-ideias','IDEIAS','Um ponto de cada vez.',(235,155,172),(62,24,42),'spark'),
 ('06-consulta','CONSULTA','Leve suas dúvidas.',(139,177,220),(18,36,65),'notes')]


def editorial_frame():
    # Keep the entire supplied photograph; reserve a contrasting title area.
    with Image.open(ASSETS/'baseline-source.jpg') as photo:
        photo=photo.convert('RGB')
        scale=min(720/photo.width,1000/photo.height)
        photo=photo.resize((round(photo.width*scale),round(photo.height*scale)),Image.Resampling.LANCZOS)
    w,h=720,1280
    yy=np.arange(h,dtype=float)[:,None,None]
    mix=np.clip((yy-160)/120,0,1)
    dark=np.array([13,17,23],dtype=float)[None,None,:]
    backdrop=np.uint8(np.broadcast_to(dark*(1-mix)+255*mix,(h,w,3)).copy())
    result=Image.fromarray(backdrop)
    result.paste(photo,((w-photo.width)//2,h-photo.height))
    if effects.FaceTracker().update(np.asarray(result)) is None:
        raise RuntimeError('A imagem-base precisa manter um rosto detectável.')
    result.save(ASSETS/'example-frame.jpg',quality=96,subsampling=0)
    result.save(ASSETS/'editorial-frame.jpg',quality=96,subsampling=0)
    return result


def demo_cards():
    folder=ASSETS/'demo-cards';folder.mkdir(exist_ok=True)
    W,H=480,720
    for filename,title,sub,accent,bg,kind in COVERS:
        # Original vector-style artwork, no stock imagery or clinical illustration.
        yy,xx=np.mgrid[:H,:W].astype(float);grad=((xx/W+yy/H)/2)[...,None]
        c0=np.array(bg);c1=np.array(accent)*.27+np.array(bg)*.73
        arr=np.uint8(c0*(1-grad)+c1*grad);im=Image.fromarray(arr).convert('RGBA');d=ImageDraw.Draw(im)
        d.text((36,34),'MED / IDEIAS',font=effects.font(17),fill=accent+(255,))
        d.text((36,101),title,font=effects.fit([title],408,58),fill=(251,247,239,255))
        d.text((38,178),sub,font=effects.fit([sub],405,21),fill=(224,225,221,255))
        cx,cy=240,425;col=accent+(255,);line=7
        if kind=='eye':
            pts=[(60+i*360/100,cy+math.sin(i/100*math.pi)*(-90)) for i in range(101)]
            pts+=[(420-i*360/100,cy+math.sin(i/100*math.pi)*90) for i in range(101)]
            d.line(pts+[pts[0]],fill=col,width=line);d.ellipse((178,363,302,487),outline=col,width=7);d.ellipse((215,400,265,450),fill=col)
        elif kind=='chat':
            d.rounded_rectangle((80,305,400,505),radius=38,outline=col,width=7)
            d.line([(150,505),(122,558),(216,505)],fill=col,width=7)
            for x in (165,240,315):d.ellipse((x-10,395,x+10,415),fill=col)
        elif kind=='orbit':
            for angle in (0,60,120):
                ring=Image.new('RGBA',im.size);rd=ImageDraw.Draw(ring);rd.ellipse((85,370,395,480),outline=col,width=5)
                im=Image.alpha_composite(im,ring.rotate(angle,resample=Image.Resampling.BICUBIC));d=ImageDraw.Draw(im)
            d.ellipse((217,402,263,448),fill=col)
        elif kind=='moon':
            d.ellipse((130,295,350,515),fill=col);d.ellipse((198,265,376,443),fill=bg+(255,))
            for x,y in [(88,310),(388,358),(128,550),(344,573)]:
                d.line((x-10,y,x+10,y),fill=col,width=4);d.line((x,y-10,x,y+10),fill=col,width=4)
        elif kind=='spark':
            pts=[(240+math.cos(i*math.pi/4)*r,420+math.sin(i*math.pi/4)*r) for i,r in enumerate([160,40,160,40,160,40,160,40])]
            d.polygon(pts,fill=col);d.ellipse((230,410,250,430),fill=bg+(255,))
        else:
            d.rounded_rectangle((124,285,356,565),radius=20,outline=col,width=7)
            for j in range(3):
                y=345+j*70;d.line([(150,y),(163,y+13),(187,y-17)],fill=col,width=5);d.line((210,y,323,y),fill=col,width=5)
        d.line((36,650,444,650),fill=col,width=2);d.text((36,674),'CONTEÚDO ILUSTRATIVO',font=effects.font(16),fill=(214,223,225,255))
        im.convert('RGB').save(folder/(filename+'.jpg'),quality=94)
    return folder


def preset(name,index,folder):
    text=TEXT.get(name,effects.DEFAULTS.get(name,''))
    d=dict(effect=name,start=0,end=4,accent=PALETTE[index%len(PALETTE)])
    if text:d['text']=text
    if name in CARD_EFFECTS:d['images']=str(folder)
    return effects.validate_plan([d],4)[0]
