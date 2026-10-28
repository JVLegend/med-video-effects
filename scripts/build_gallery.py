#!/usr/bin/env python3
"""Recria exemplos a partir de um frame autorizado. #Saude #Tecnologia"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import effects

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'assets'
LABELS={
 'focus':('01','FOCO NO ROSTO','Sua explicação em primeiro plano.'),
 'spotlight':('02','SPOTLIGHT','Direcione a atenção para quem fala.'),
 'grade':('03','COR CINEMATOGRÁFICA','Um acabamento discreto para o vídeo.'),
 'checklist':('04','CHECKLIST','Organize os pontos da explicação.'),
 'split':('05','TELA DIVIDIDA','Dê espaço a uma ideia importante.'),
 'headline':('06','TÍTULO EM CAIXA','Uma mensagem clara para abrir.'),
}
CUSTOM={'checklist':'Observe|Anote suas dúvidas|Converse com seu médico','split':'Informação clara|para cuidar melhor','headline':'Leve suas dúvidas|para a consulta'}

def make():
 source=Image.open(ASSETS/'example-frame.jpg').convert('RGB')
 frame=np.array(source);tracker=effects.FaceTracker();face=tracker.update(frame)
 if face is None:raise RuntimeError('O frame de exemplo precisa de um rosto detectável.')
 print('Rosto detectado:',face)
 examples=[]
 for name in effects.EFFECTS:
  plan=dict(effect=name,start=0,end=4,text=CUSTOM.get(name,''))
  out,_=effects.render_effect(frame.copy(),face.copy(),plan,2.7)
  Image.fromarray(out).save(ASSETS/f'{name}.jpg',quality=91)
  examples.append(Image.fromarray(out))
 # Portrait gallery: all images are real renderer output, not mockups.
 W=1620;H=2440
 board=Image.new('RGB',(W,H),(9,18,29));d=ImageDraw.Draw(board)
 d.rounded_rectangle((70,62,338,104),radius=21,fill=(17,56,58))
 d.text((92,70),'EXPERIMENTO · V0.1',font=effects.font(21),fill=(114,234,200))
 d.text((70,142),'Seis efeitos. Uma boa explicação.',font=effects.font(73),fill=(244,248,250))
 d.text((74,244),'Vídeos educativos para médicos · Claude Code + Codex',font=effects.font(32),fill=(154,176,191))
 d.line((74,320,1546,320),fill=(42,63,77),width=2)
 for i,(name,im) in enumerate(zip(effects.EFFECTS,examples)):
  col,row=i%3,i//3;x=70+col*500;y=372+row*960
  thumb=im.resize((470,836),Image.Resampling.LANCZOS)
  board.paste(thumb,(x,y))
  number,label,sub=LABELS[name]
  d.text((x,y+856),number,font=effects.font(23),fill=(103,229,193))
  title=effects.fit([label],405,24)
  d.text((x+45,y+854),label,font=title,fill=(242,247,249))
  d.text((x,y+900),sub,font=effects.fit([sub],470,22),fill=(151,173,189))
 d.text((74,2332),'Processamento local  /  Áudio preservado  /  Sem chave de API no renderizador',font=effects.font(25),fill=(144,169,185))
 board.save(ASSETS/'preview.jpg',quality=94)
 hero=Image.new('RGB',(1600,580),(9,18,29));hd=ImageDraw.Draw(hero)
 hd.rounded_rectangle((70,55,345,99),radius=22,fill=(17,56,58));hd.text((91,64),'MED VIDEO EFFECTS',font=effects.font(22),fill=(114,234,200))
 hd.text((70,145),'Sua explicação merece',font=effects.font(79),fill=(245,249,250))
 hd.text((70,244),'um vídeo mais claro.',font=effects.font(79),fill=(103,229,193))
 hd.text((73,385),'6 efeitos locais para Claude Code e Codex',font=effects.font(35),fill=(164,186,202))
 hd.text((75,474),'PYTHON + FFMPEG     ·     PORTUGUÊS     ·     EXPERIMENTO ABERTO',font=effects.font(24),fill=(132,158,178))
 hero.save(ASSETS/'hero.png')
 # Short animated preview uses only the same authorized still image.
 gifs=[]
 small=np.array(source.resize((270,480),Image.Resampling.LANCZOS));sf=face*(270/source.width)
 for name in effects.EFFECTS:
  for i in range(16):
   t=i/8;plan=dict(effect=name,start=0,end=2,text=CUSTOM.get(name,''))
   out,_=effects.render_effect(small.copy(),sf.copy(),plan,t)
   tile=Image.new('RGB',(270,520),(9,18,29));tile.paste(Image.fromarray(out),(0,40))
   ImageDraw.Draw(tile).text((12,12),LABELS[name][1],font=effects.fit([LABELS[name][1]],246,16),fill=(245,249,250))
   gifs.append(tile)
 gifs[0].save(ASSETS/'demo.gif',save_all=True,append_images=gifs[1:],duration=125,loop=0,optimize=True)
 print('Galeria e GIF prontos.')

if __name__=='__main__':make()
