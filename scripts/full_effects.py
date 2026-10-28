"""Composições locais do catálogo completo. #Saude #Tecnologia"""
from pathlib import Path
import math
import creative_effects
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter

DEFAULTS = {
 'noise':'Ideias|Perguntas|Explicações', 'orbit':'Observe|Pergunte|Converse',
 'backdrop-word':'SAÚDE', 'todo':'Observe|Anote suas dúvidas|Converse com seu médico',
 'tap':'Seguir|Seguindo', 'pause-point':'Vale anotar', 'uninstall':'Reorganizando ideias',
 'reel-frame':'Seu vídeo', 'shortcut-rain':'Ctrl|C|V|Enter|Tab', 'scribble':'Anote',
 'glass-widgets':'Próxima consulta|Leve suas dúvidas|Organize suas notas',
 'red-collage':'SAÚDE|Informação clara|Uma ideia por vez', 'pastel-word':'CUIDADO|Converse com seu médico',
 'check-pills':'Observe|Pergunte|Converse', 'profile-wall':'Seu conteúdo',
 'tier-list':'Prioridades|Perguntar', 'broll-split':'Imagem de apoio',
 'phone-fan':'Vídeos para explicar', 'headline-wall':'Observe|Pergunte|Converse',
 'liquid-glass-graph':'Gráfico ilustrativo', 'carousel-spin':'Observe|Pergunte|Converse',
 'match-cut':'SAÚDE', 'apple-toggles':'Clareza|Organização|Boa conversa',
 'led-sign':'Informação clara', 'over-the-shoulder-zoom':'Primeira ideia|Próxima ideia',
 'messages':'Anote suas dúvidas|Leve suas perguntas|Converse na consulta',
 'place-in-grid':'Seu conteúdo',
}
DEFAULTS.update(creative_effects.DEFAULTS)
LIMITS={name:3 for name in DEFAULTS}
LIMITS.update({'tap':2,'pause-point':1,'uninstall':1,'reel-frame':1,'shortcut-rain':8,
               'scribble':1,'backdrop-word':1,'profile-wall':1,'tier-list':2,'broll-split':1,
               'phone-fan':1,'liquid-glass-graph':1,'match-cut':1,'led-sign':2,
               'over-the-shoulder-zoom':2,'place-in-grid':1})
LIMITS.update(creative_effects.LIMITS)
FULL_NAMES=set(DEFAULTS)|{'swipe','rabbit-hole','slow-push'}
MINT=(94,233,193,255); WHITE=(248,250,252,255); INK=(14,29,39,245)


def ease(x):
 x=max(0.,min(1.,x));return 1-(1-x)**3


def rgba(frame):return Image.fromarray(frame).convert('RGBA')


def photo(image,w,h):
 w,h=max(1,int(w)),max(1,int(h));im=image.convert('RGB');ratio=max(w/im.width,h/im.height)
 im=im.resize((max(w,math.ceil(im.width*ratio)),max(h,math.ceil(im.height*ratio))),Image.Resampling.LANCZOS)
 x=(im.width-w)//2;y=(im.height-h)//2
 return im.crop((x,y,x+w,y+h)).convert('RGBA')


def cards_for(e,frame):
 if '_cards' not in e:
  cards=[]
  if e.get('images'):
   folder=Path(e['images']).expanduser()
   paths=[folder] if folder.is_file() else sorted(folder.iterdir())
   for path in paths:
    if path.suffix.lower() in ('.jpg','.jpeg','.png','.webp') and path.is_file():
     with Image.open(path) as im:cards.append(im.convert('RGB').copy())
    if len(cards)>=12:break
   if not cards:raise ValueError('Nenhuma imagem JPG, PNG ou WebP encontrada em --images.')
  e['_cards']=cards or [Image.fromarray(frame).copy()]
 return e['_cards']


def tile(api,image,w,h,text='',color=MINT):
 w,h=max(8,int(w)),max(8,int(h));im=photo(image,w,h);d=ImageDraw.Draw(im)
 border=max(1,w//70);d.rounded_rectangle((1,1,w-2,h-2),radius=max(2,w*.07),outline=color,width=border)
 if text and w>=100:
  f=api.fit([text],w*.88,max(10,int(w*.085)));ph=int(f.size*1.8)
  d.rectangle((0,h-ph,w,h),fill=(10,23,30,225))
  api.text_center(d,w/2,h-ph/2,text,f,WHITE)
 return im


def arrow(d,start,end,color,width):
 d.line([start,end],fill=color,width=width)
 angle=math.atan2(end[1]-start[1],end[0]-start[0]);s=width*3.5
 for off in (-.55,.55):
  d.line([end,(end[0]-s*math.cos(angle+off),end[1]-s*math.sin(angle+off))],fill=color,width=width)


def render_full(frame,face,e,t,api):
 if e['effect'] in creative_effects.DEFAULTS:
  return creative_effects.render(frame,face,e,t,api)
 h,w=frame.shape[:2];name=e['effect'];local=t-e['start'];duration=e['end']-e['start']
 p=max(0.,min(1.,local/duration));fade=min(ease(local/.25),max(0.,min(1.,(duration-local)/.25)))
 lines=e.get('text','').split('|');image=rgba(frame);layer=Image.new('RGBA',(w,h));d=ImageDraw.Draw(layer)
 y,space=api.panel_layout(face,w,h,h*.31);space=max(0,space)
 # Camera and full-image treatments do not require title headroom.
 if name=='swipe':
  a=frame.astype(np.float32)/255;lum=a@np.float32([.299,.587,.114]);graded=np.uint8(np.clip((lum[...,None]+(a-lum[...,None])*.65)*255,0,255))
  x=int(w*p);out=frame.copy();out[:,:x]=graded[:,:x];im=rgba(out);dd=ImageDraw.Draw(im)
  dd.line((x,0,x,h),fill=WHITE,width=max(2,w//180));dd.ellipse((x-w*.025,h*.70-w*.025,x+w*.025,h*.70+w*.025),fill=MINT)
  return np.asarray(im.convert('RGB')).copy(),face
 if name=='pause-point':
  if '_frozen' not in e:e['_frozen']=(frame.copy(),None if face is None else face.copy())
  frame,face=e['_frozen'];image=rgba(frame)
  y,space=api.panel_layout(face,w,h,h*.25);space=max(0,space)
  if space>w*.09:
   f=api.fit([lines[0]],w*.75,int(w*.065));api.text_center(d,w/2,y+f.size,lines[0],f,MINT)
   end=(w*.76,y+space*.93);start=(w*.43,y+f.size*1.8)
   if face is not None:end=(min(w*.93,face[0]+face[2]*.65),max(y+f.size*2,face[1]-face[3]*.7))
   k=ease(local/.5);tip=(start[0]+(end[0]-start[0])*k,start[1]+(end[1]-start[1])*k)
   arrow(d,start,tip,MINT,max(2,int(w*.007)))
 elif name=='uninstall':
  out=frame.copy();strength=math.sin(p*math.pi)
  for j in range(6):
   yy=int(h*(j+.5)/6);hh=max(2,h//40);shift=int(w*.035*strength*math.sin(t*23+j))
   out[yy:yy+hh]=np.roll(out[yy:yy+hh],shift,axis=1)
  image=rgba(out)
  if space>w*.09:
   ph=min(space,w*.17);d.rounded_rectangle((w*.08,y,w*.92,y+ph),radius=w*.015,fill=INK)
   f=api.fit([lines[0]],w*.75,int(w*.04));api.text_center(d,w/2,y+ph*.35,lines[0],f,WHITE)
   d.rectangle((w*.12,y+ph*.70,w*.12+w*.76*p,y+ph*.83),fill=(255,105,95,255))
 elif name=='reel-frame':
  k=.94-.08*ease(local/.4);ww=int(w*k);hh=int(h*k)
  image=rgba(np.uint8(frame.astype(float)*.35));mini=photo(Image.fromarray(frame),ww,hh)
  image.alpha_composite(mini,((w-ww)//2,(h-hh)//2))
  d.rounded_rectangle(((w-ww)//2-2,(h-hh)//2-2,(w+ww)//2+2,(h+hh)//2+2),radius=w*.02,outline=WHITE,width=max(2,w//180))
  f=api.fit([lines[0]],w*.72,int(w*.037));api.text_center(d,w/2,h*.96,lines[0],f,WHITE)
 elif name=='rabbit-hole':
  image=rgba(frame)
  for j in range(1,7):
   scale=(.77**j)*(1+.035*math.sin(t*2));ww=int(w*scale);hh=int(h*scale)
   im=photo(Image.fromarray(frame),ww,hh).rotate(math.sin(t)*j*.9,resample=Image.Resampling.BICUBIC)
   image.alpha_composite(im,((w-ww)//2,(h-hh)//2));d.rectangle(((w-ww)//2,(h-hh)//2,(w+ww)//2,(h+hh)//2),outline=(125,242,215,160),width=max(1,w//250))
 elif name=='slow-push':
  out,newface=api.zoom(frame,face,1+.18*ease(p))
  blurred=cv2.GaussianBlur(out,(0,0),max(.4,w*.009))
  yy,xx=np.ogrid[:h,:w]
  cx,cy,fw,fh=newface if newface is not None else (w/2,h*.45,w*.22,h*.16)
  mask=np.clip(1.5-((xx-cx)/(fw*1.2))**2-((yy-cy)/(fh*1.65))**2,0,1)[...,None]
  return np.uint8(np.clip(out*mask+blurred*(1-mask),0,255)),newface
 elif name=='over-the-shoulder-zoom':
  phase=(p*2)%1;side=-1 if p<.5 else 1
  pivot=None if face is None else face.copy()
  if pivot is not None:pivot[0]=np.clip(pivot[0]+side*w*.13,w*.2,w*.8)
  out,face=api.zoom(frame,pivot,1+.16*math.sin(phase*math.pi));image=rgba(out)
  y,space=api.panel_layout(face,w,h,h*.22);space=max(0,space)
  if space>w*.12:
   text=lines[0 if p<.5 else min(1,len(lines)-1)];pw=w*.78;ph=min(space,w*.22)
   d.rounded_rectangle((w*.11,y,w*.89,y+ph),radius=w*.025,fill=INK,outline=MINT,width=max(1,w//250))
   f=api.fit([text],pw*.85,int(w*.048));api.text_center(d,w/2,y+ph*.4,text,f,WHITE)
   pts=[(w*.18+j*w*.064,y+ph*(.80-.26*(j/10)**1.6)) for j in range(11)]
   d.line(pts,fill=MINT,width=max(2,w//150))
 elif name in ('broll-split','place-in-grid'):
  cards=cards_for(e,frame)
  if name=='broll-split':
   split=int(h*.36);image=rgba(frame).filter(ImageFilter.GaussianBlur(w*.02))
   upper=photo(cards[0],w,split);image.paste(upper,(0,0))
   scale=(h-split)/h;lower=photo(Image.fromarray(frame),int(w*scale),h-split);image.alpha_composite(lower,((w-lower.width)//2,split))
   f=api.fit([lines[0]],w*.8,int(w*.04));pw=int(f.getlength(lines[0])+w*.08);ph=int(f.size*1.7)
   d.rounded_rectangle((w*.05,h*.025,w*.05+pw,h*.025+ph),radius=w*.015,fill=INK)
   api.text_center(d,w*.05+pw/2,h*.025+ph/2,lines[0],f,WHITE)
  else:
   image=rgba(frame).filter(ImageFilter.GaussianBlur(w*.02));gap=max(2,int(w*.012));tw=(w-gap*4)//3;th=(h-gap*4)//3
   for j in range(9):
    img=Image.fromarray(frame) if j==4 else cards[j%len(cards)]
    xx=gap+(j%3)*(tw+gap);yy=gap+(j//3)*(th+gap)
    im=tile(api,img,tw,th,'Você' if j==4 else '',MINT if j==4 else WHITE)
    k=ease((local-(0 if j==4 else .15+j*.04))/.3)
    if k>0:
     im.putalpha(im.getchannel('A').point(lambda a:int(a*k)));image.alpha_composite(im,(xx,yy))
 elif space<w*.10:
  return frame,face
 elif name in ('noise','orbit','phone-fan','carousel-spin','profile-wall'):
  cards=cards_for(e,frame);top=y;labels=lines if len(lines)>1 else ['']
  if name=='profile-wall':
   gap=max(2,int(w*.012));tw=int(w*.255);th=int(min(space*.46,w*.19))
   for j in range(6):
    im=tile(api,cards[j%len(cards)],tw,th);xx=int(w*.10+(j%3)*(tw+gap));yy=int(top+(j//3)*(th+gap))
    layer.alpha_composite(im,(xx,yy))
  else:
   n=5 if name in ('noise','phone-fan') else 4;tw=int(w*.18);th=int(min(space*.72,w*.26))
   for j in range(n):
    if name=='noise' and local<j*.17:continue
    if name=='noise':xx=w*.13+j*w*.135;cy=top+space*.5+(j%2-.5)*space*.12;angle=(j-2)*6
    elif name=='phone-fan':xx=w*.5+(j-2)*w*.125*ease(local/.5);cy=top+space*.5+abs(j-2)*space*.04;angle=(j-2)*12*ease(local/.5)
    else:
     speed=local*1.4 if name=='orbit' else 5*(1-math.exp(-local))
     a=j*2*math.pi/n+speed;xx=w*.5+math.cos(a)*w*.30;cy=top+space*.48+math.sin(a)*space*.19;angle=math.sin(a)*5
    im=tile(api,cards[j%len(cards)],tw,th,labels[j%len(labels)]).rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    if im.height>space:im.thumbnail((int(w*.28),int(space)))
    layer.alpha_composite(im,(int(xx-im.width/2),int(np.clip(cy-im.height/2,top,top+space-im.height))))
 elif name in ('backdrop-word','led-sign','pastel-word','red-collage'):
  if name=='pastel-word':image=Image.blend(image,Image.new('RGBA',image.size,(194,178,237,255)),.18)
  if name=='red-collage':image=Image.fromarray(frame).convert('L').convert('RGBA')
  if name=='led-sign':image=Image.blend(image,Image.new('RGBA',image.size,(4,10,20,255)),.38)
  text=lines[0];f=api.fit([text],w*.90,min(int(w*.18),int(space*.50)))
  color=(255,76,82,255) if name=='red-collage' else MINT if name=='led-sign' else WHITE
  if name=='led-sign':
   text=text[:int(len(text)*ease(local/max(.4,duration*.5)))];glow=Image.new('RGBA',(w,h));gd=ImageDraw.Draw(glow)
   api.text_center(gd,w/2,y+space*.35,text,f,color);layer=Image.alpha_composite(layer,glow.filter(ImageFilter.GaussianBlur(w*.012)));d=ImageDraw.Draw(layer)
  api.text_center(d,w/2,y+space*.35,text,f,color)
  for j,sub in enumerate(lines[1:]):
   sf=api.fit([sub],w*.83,int(w*.046));cy=y+space*(.67+j*.22)
   if name=='red-collage':d.rectangle((w*.07,cy-sf.size*.8,w*.93,cy+sf.size*.8),fill=(215,43,53,255))
   api.text_center(d,w/2,cy,sub,sf,WHITE)
 elif name in ('todo','check-pills','apple-toggles','messages','headline-wall','match-cut','tier-list','glass-widgets','liquid-glass-graph','tap','shortcut-rain','scribble'):
  ph=min(space,w*.42);left,right=w*.08,w*.92
  if name in ('todo','check-pills','apple-toggles','messages','headline-wall'):
   rowh=min(ph/max(1,len(lines)),w*.13)
   for j,text in enumerate(lines):
    k=ease((local-j*.25)/.25)
    if not k:continue
    yy=y+j*rowh;rh=rowh*.88;pad=w*.026
    fill=(238,246,241,245) if name=='todo' else (24,47,66,245) if name=='headline-wall' else (31,113,222,245) if name=='check-pills' else (239,244,248,245)
    x0=left+(1-k)*w*.025
    d.rounded_rectangle((x0,yy,right,yy+rh),radius=min(w*.03,rh*.3),fill=fill)
    f=api.fit([text],w*.64,min(int(w*.050),int(rh*.45)))
    cy=yy+rh/2;on=local>=.5+j*max(.3,(duration-.8)/len(lines))
    fg=WHITE if name in ('headline-wall','check-pills') else (20,36,43,255)
    d.text((left+pad,cy),text,font=f,fill=fg,anchor='lm')
    if name=='apple-toggles':
     ww=w*.095;hh=min(rh*.6,w*.05);xx=right-pad-ww
     d.rounded_rectangle((xx,cy-hh/2,xx+ww,cy+hh/2),radius=hh/2,fill=(4,177,130,255) if on else (154,170,179,255))
     r=hh*.4;cx=xx+(ww-hh/2 if on else hh/2);d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=WHITE)
    elif name in ('todo','check-pills') and on:
     xx=right-pad-w*.025;d.line([(xx-w*.016,cy),(xx,cy+w*.014),(xx+w*.029,cy-w*.019)],fill=MINT if name=='todo' else WHITE,width=max(2,w//160))
  elif name=='match-cut':
   j=min(2,int(local/max(.2,duration/3)));pw=w*.84;d.rounded_rectangle((left,y,right,y+ph),radius=w*.02,fill=(247,244,236,255))
   f=api.fit([lines[0]],pw*.83,int(w*.11));api.text_center(d,w/2,y+ph*.45,lines[0],f,(22,33,42,255))
   d.rectangle((w*.15,y+ph*.22,w*.85,y+ph*.68),outline=(235,62,65,255),width=max(2,w//150))
   for r in range(3):d.line((w*.15,y+ph*(.77+r*.055),w*(.73-.07*((r+j)%3)),y+ph*(.77+r*.055)),fill=(130,145,147,255),width=max(1,w//250))
  elif name=='tier-list':
   rh=ph/3
   for j,label in enumerate(['S','A','B']):
    yy=y+j*rh;d.rectangle((left,yy,right,yy+rh*.92),fill=INK)
    d.rectangle((left,yy,left+w*.09,yy+rh*.92),fill=[(236,104,114,255),(241,177,104,255),(116,208,173,255)][j])
    api.text_center(d,left+w*.045,yy+rh*.46,label,api.font(rh*.5),WHITE)
   item=lines[-1];f=api.fit([item],w*.57,int(w*.043));cy=y+ph*.81-(ph*.66)*ease(local/.75)
   d.rounded_rectangle((w*.22,cy-rh*.35,w*.86,cy+rh*.35),radius=w*.015,fill=(13,163,131,255));api.text_center(d,w*.54,cy,item,f,WHITE)
  elif name=='glass-widgets':
   widths=[.49,.35,.63];positions=[(.08,0),(.59,.05),(.18,.56)]
   for j,text in enumerate(lines):
    ww=w*widths[j];hh=ph*.40;xx=w*positions[j][0];yy=y+ph*positions[j][1]+math.sin(t*1.7+j)*w*.006
    region=image.crop((int(xx),int(yy),int(xx+ww),int(yy+hh))).filter(ImageFilter.GaussianBlur(w*.012))
    region=Image.blend(region,Image.new('RGBA',region.size,(237,248,249,255)),.65)
    layer.alpha_composite(region,(int(xx),int(yy)));d.rounded_rectangle((xx,yy,xx+ww,yy+hh),radius=w*.015,outline=WHITE,width=max(1,w//250))
    if ww>=100:
     f=api.fit([text],ww*.86,min(int(w*.042),int(hh*.34)));api.text_center(d,xx+ww/2,yy+hh/2,text,f,(20,37,43,255))
  elif name=='liquid-glass-graph':
   d.rounded_rectangle((left,y,right,y+ph),radius=w*.03,fill=(22,46,55,225),outline=(165,223,221,255),width=max(1,w//200))
   f=api.fit([lines[0]],w*.72,int(w*.040));api.text_center(d,w/2,y+ph*.18,lines[0],f,WHITE)
   vals=[.1,.17,.15,.36,.28,.49,.53,.68,.65,.83];n=max(1,int((len(vals)-1)*ease(p)))
   pts=[(w*.14+i*w*.079,y+ph*(.84-.48*v)) for i,v in enumerate(vals[:n+1])]
   if len(pts)>1:d.line(pts,fill=MINT,width=max(2,w//130))
   sf=api.font(w*.022);api.text_center(d,w/2,y+ph*.93,'ILUSTRAÇÃO · SEM DADOS CLÍNICOS',sf,(161,200,200,255))
  elif name=='tap':
   on=p>.55;text=lines[min(1,len(lines)-1)] if on else lines[0];pw=w*.49;hh=min(ph,w*.14)
   d.rounded_rectangle(((w-pw)/2,y+ph*.2,(w+pw)/2,y+ph*.2+hh),radius=hh*.45,fill=MINT if on else WHITE)
   f=api.fit([text],pw*.8,int(w*.060));api.text_center(d,w/2,y+ph*.2+hh/2,text,f,(16,35,41,255))
  elif name=='shortcut-rain':
   for j in range(9):
    side=w*.115;xx=w*.10+(j%5)*w*.17;yy=y+((local*.19+j*.13)%1)*max(1,ph-side)
    d.rounded_rectangle((xx,yy,xx+side,yy+side),radius=w*.014,fill=(246,247,243,245),outline=MINT,width=max(1,w//250))
    text=lines[j%len(lines)];text=text if side>=50 else text[:2];f=api.fit([text],side*.84,int(w*.034));api.text_center(d,xx+side/2,yy+side/2,text,f,(22,34,43,255))
  elif name=='scribble':
   # Border doodles avoid facial features; no circle is drawn over the face.
   stroke=max(2,w//130);x0,x1=w*.10,w*.90;cy=y+ph*.42
   pts=[(x0+j*(x1-x0)/60,cy+math.sin(j*.35)*ph*.08) for j in range(max(2,int(61*ease(local/.6))))]
   d.line(pts,fill=(255,214,10,255),width=stroke)
   f=api.fit([lines[0]],w*.65,int(w*.07));api.text_center(d,w/2,y+ph*.78,lines[0],f,(255,214,10,255))
   for xx in (w*.06,w*.94):
    yy=face[1] if face is not None else h*.46;d.line((xx,yy-w*.035,xx,yy+w*.035),fill=(255,214,10,255),width=stroke);d.line((xx-w*.025,yy,xx+w*.025,yy),fill=(255,214,10,255),width=stroke)
 else:
  raise RuntimeError(f'Renderizador não implementado: {name}')
 layer.putalpha(layer.getchannel('A').point(lambda a:int(a*fade)))
 return np.asarray(Image.alpha_composite(image,layer).convert('RGB')).copy(),face
