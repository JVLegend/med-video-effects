"""Seis efeitos para tornar explicações visuais. #Saude #Tecnologia"""
import math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

DEFAULTS={
 'idea-scan':'Uma ideia importante',
 'focus-lens':'Veja de perto',
 'concept-map':'Consulta|Dúvidas|Histórico|Próximos passos',
 'question-flip':'Como se preparar?|Leve suas dúvidas',
 'source-pin':'Seu ponto principal|Adicione a referência',
 'idea-pulse':'Uma ideia de cada vez',
}
LIMITS={'idea-scan':1,'focus-lens':1,'concept-map':4,'question-flip':2,'source-pin':2,'idea-pulse':1}
MINT=(94,233,193,255);WHITE=(248,250,252,255);INK=(14,29,39,245)


def ease(x):
 x=max(0.,min(1.,x));return 1-(1-x)**3


def render(frame,face,e,t,api):
 h,w=frame.shape[:2];name=e['effect'];local=t-e['start'];duration=e['end']-e['start']
 fade=min(ease(local/.25),max(0.,min(1.,(duration-local)/.25)))
 image=Image.fromarray(frame).convert('RGBA');layer=Image.new('RGBA',(w,h));d=ImageDraw.Draw(layer)
 y,space=api.panel_layout(face,w,h,h*.30)
 if space<w*.13:return frame,face
 lines=e['text'].split('|');left,right=w*.08,w*.92;ph=min(space,w*.43)
 stroke=max(2,int(w*.004))
 if name=='idea-scan':
  # The scanner reveals typography, without analysing the person or video.
  d.rounded_rectangle((left,y,right,y+ph),radius=w*.025,fill=INK,outline=(67,99,111,255),width=stroke)
  f=api.fit(lines,w*.70,min(int(w*.080),int(ph*.23)))
  text=Image.new('RGBA',(w,h));td=ImageDraw.Draw(text)
  api.text_center(td,w/2,y+ph*.52,lines[0],f,WHITE)
  reveal=min(1.,local/.85)
  clip=Image.new('L',(w,h));ImageDraw.Draw(clip).rectangle((0,y,w,y+ph*reveal),fill=255)
  text.putalpha(Image.fromarray(np.minimum(np.asarray(text.getchannel('A')),np.asarray(clip)).astype(np.uint8)))
  layer=Image.alpha_composite(layer,text);d=ImageDraw.Draw(layer)
  scan=y+ph*(.08+.84*((local*.65)%1))
  glow=Image.new('RGBA',(w,h));gd=ImageDraw.Draw(glow)
  gd.line((left+w*.025,scan,right-w*.025,scan),fill=MINT,width=stroke*3)
  layer=Image.alpha_composite(layer,glow.filter(ImageFilter.GaussianBlur(w*.009)));d=ImageDraw.Draw(layer)
  d.line((left+w*.025,scan,right-w*.025,scan),fill=MINT,width=stroke)
  # Corner ticks reinforce the motion even when viewed without text.
  for xx in [left+w*.025,right-w*.025]:d.line((xx,y+ph*.1,xx,y+ph*.21),fill=MINT,width=stroke)
 elif name=='focus-lens':
  pictures=api.cards_for(e,frame);photo=pictures[0].convert('RGB')
  diameter=int(min(ph*.78,w*.30));cx=w*.43;cy=y+diameter/2+w*.01
  if not e.get('images') and face is not None:
   fx,fy,fw,_=face;radius=fw*.76
  else:fx,fy=photo.width/2,photo.height/2;radius=min(photo.size)*.32
  radius=max(2,radius/(1+.18*ease(local/.65)))
  # Move within the actual picture; the pixels remain real, not generated detail.
  fx=np.clip(fx,radius,max(radius,photo.width-radius));fy=np.clip(fy,radius,max(radius,photo.height-radius))
  crop=photo.crop((int(fx-radius),int(fy-radius),int(fx+radius),int(fy+radius)))
  crop=crop.resize((diameter,diameter),Image.Resampling.LANCZOS).convert('RGBA')
  mask=Image.new('L',crop.size);ImageDraw.Draw(mask).ellipse((0,0,diameter-1,diameter-1),fill=255);crop.putalpha(mask)
  layer.alpha_composite(crop,(int(cx-diameter/2),int(cy-diameter/2)))
  d=ImageDraw.Draw(layer);r=diameter/2
  d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=MINT,width=stroke*2)
  d.line((cx+r*.72,cy+r*.72,cx+r*1.15,cy+r*1.15),fill=MINT,width=stroke*3)
  f=api.fit(lines,w*.76,min(int(w*.045),int(ph*.14)))
  api.text_center(d,w/2,y+ph*.93,lines[0],f,WHITE)
 elif name=='concept-map':
  center=(w*.50,y+ph*.20);nodew=w*.245;nodeh=ph*.26
  # Lines grow before their destination nodes appear.
  leaves=lines[1:] or ['Ideia'];positions=[w/2+(j-(len(leaves)-1)/2)*w*.285 for j in range(len(leaves))]
  for j,(text,xx) in enumerate(zip(leaves,positions)):
   k=ease((local-.25-j*.17)/.45);end=(xx,y+ph*.75)
   bend=(center[0],y+ph*.47);tip=(bend[0]+(end[0]-bend[0])*k,bend[1]+(end[1]-bend[1])*k)
   if k>0:
    d.line([center,bend,tip],fill=MINT,width=stroke)
    if k>.75:
     d.rounded_rectangle((xx-nodew/2,end[1]-nodeh/2,xx+nodew/2,end[1]+nodeh/2),radius=w*.014,fill=INK,outline=MINT,width=max(1,stroke//2))
     size=max(10,min(int(w*.040),int(nodeh*.40)));f=api.font(size)
     rows=['']
     for word in text.split():
      candidate=(rows[-1]+' '+word).strip()
      if f.getlength(candidate)>nodew*.88 and rows[-1]:rows.append(word)
      else:rows[-1]=candidate
     if len(rows)>2 or max(f.getlength(row) for row in rows)>nodew*.88:
      raise ValueError('Encurte os conceitos do Mapa de ideias para esta resolução.')
     for row,textrow in enumerate(rows):
      api.text_center(d,xx,end[1]+(row-(len(rows)-1)/2)*f.size*1.1,textrow,f,WHITE)
  pw=w*.45;nh=ph*.29
  d.rounded_rectangle((center[0]-pw/2,center[1]-nh/2,center[0]+pw/2,center[1]+nh/2),radius=w*.018,fill=MINT)
  f=api.fit([lines[0]],pw*.85,int(w*.052));api.text_center(d,*center,lines[0],f,(15,38,43,255))
 elif name=='question-flip':
  # Perspective is expressed as horizontal scale, with readable holds on both faces.
  p=local/duration;turn=max(0.,min(1.,(p-.38)/.24));back=turn>=.5
  scale=max(.025,abs(math.cos(turn*math.pi)))
  pw=int(w*.82);hh=int(min(ph,w*.29));card=Image.new('RGBA',(pw,hh));cd=ImageDraw.Draw(card)
  fill=MINT if back else (247,246,239,255);ink=(18,39,44,255)
  cd.rounded_rectangle((0,0,pw-1,hh-1),radius=w*.024,fill=fill)
  title='RESPOSTA' if back else 'PERGUNTA';api.text_center(cd,pw/2,hh*.23,title,api.font(min(w*.029,hh*.17)),ink)
  text=lines[min(1,len(lines)-1)] if back else lines[0]
  f=api.fit([text],pw*.86,min(int(w*.063),int(hh*.28)));api.text_center(cd,pw/2,hh*.61,text,f,ink)
  narrowed=card.resize((max(1,int(pw*scale)),hh),Image.Resampling.LANCZOS)
  layer.alpha_composite(narrowed,(int((w-narrowed.width)/2),y))
 elif name=='source-pin':
  hh=min(ph,w*.31);d.rounded_rectangle((left,y,right,y+hh),radius=w*.022,fill=(246,247,243,250))
  # The paper icon and animated underline call attention to a supplied citation.
  ix=left+w*.03;iy=y+hh*.15;iw=w*.07;ih=hh*.34
  d.rounded_rectangle((ix,iy,ix+iw,iy+ih),radius=w*.006,outline=(0,139,116,255),width=stroke)
  for j in range(3):d.line((ix+iw*.20,iy+ih*(.27+j*.19),ix+iw*.80,iy+ih*(.27+j*.19)),fill=(0,139,116,255),width=max(1,stroke//2))
  f=api.fit([lines[0]],w*.66,min(int(w*.060),int(hh*.23)))
  d.text((ix+iw+w*.035,y+hh*.30),lines[0],font=f,fill=(18,39,44,255),anchor='lm')
  text=lines[1] if len(lines)>1 else 'Adicione a referência'
  f=api.fit([text],w*.74,min(int(w*.038),int(hh*.18)))
  d.text((left+w*.035,y+hh*.71),text,font=f,fill=(0,111,94,255),anchor='lm')
  length=min(w*.74,f.getlength(text))*ease((local-.3)/.7)
  d.line((left+w*.035,y+hh*.87,left+w*.035+length,y+hh*.87),fill=(0,166,133,255),width=stroke)
 elif name=='idea-pulse':
  # A typographic pulse is an editorial cue, never a measured physiological signal.
  d.rounded_rectangle((left,y,right,y+ph),radius=w*.025,fill=INK)
  f=api.fit(lines,w*.74,min(int(w*.078),int(ph*.29)))
  api.text_center(d,w/2,y+ph*.31,lines[0],f,WHITE)
  phase=(local*.48)%1;points=[]
  for j in range(121):
   xx=j/120;dx=xx-phase
   pulse=math.sin(dx*math.pi*15)*math.exp(-(dx/.10)**2)
   points.append((left+w*.035+xx*w*.77,y+ph*.73-pulse*ph*.16))
  d.line(points,fill=MINT,width=stroke)
  pos=points[min(120,int(phase*120))];radius=w*(.006+.004*(.5+.5*math.sin(local*7)))
  d.ellipse((pos[0]-radius,pos[1]-radius,pos[0]+radius,pos[1]+radius),fill=WHITE)
 else:raise RuntimeError(f'Efeito criativo não implementado: {name}')
 layer.putalpha(layer.getchannel('A').point(lambda a:int(a*fade)))
 return np.asarray(Image.alpha_composite(image,layer).convert('RGB')).copy(),face
