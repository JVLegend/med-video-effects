#!/usr/bin/env python3
"""Exemplos do catálogo com um frame autorizado. #Saude #Tecnologia"""
from pathlib import Path
import math
import numpy as np
from PIL import Image,ImageDraw
import effects
from catalog import CATALOG

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'assets'
NEW=['idea-scan','focus-lens','concept-map','question-flip','source-pin','idea-pulse']
POPULAR=['headline-box','orbit']+NEW
COUNT=len(CATALOG)
INFO={name:(i+1,label,desc) for i,(name,label,desc,_) in enumerate(CATALOG)}

def plan(name,end=4):
 return effects.validate_plan([dict(effect=name,start=0,end=end)],end)[0]

def board(items,filename,title,subtitle):
 W,H=1920,2230;im=Image.new('RGB',(W,H),(9,18,29));d=ImageDraw.Draw(im)
 d.rounded_rectangle((70,52,370,98),radius=23,fill=(17,56,58))
 d.text((92,62),'MED VIDEO EFFECTS',font=effects.font(23),fill=(114,234,200))
 d.text((70,138),title,font=effects.fit([title],1770,81),fill=(244,248,250))
 d.text((74,244),subtitle,font=effects.fit([subtitle],1770,34),fill=(154,176,191))
 d.line((74,310,1846,310),fill=(42,63,77),width=2)
 for i,name in enumerate(items):
  col,row=i%4,i//4;x=70+col*450;y=350+row*880
  with Image.open(ASSETS/f'{name}.jpg') as photo:
   im.paste(photo.resize((430,764),Image.Resampling.LANCZOS),(x,y))
  number,label,_=INFO[name]
  d.text((x,y+783),str(number).zfill(2),font=effects.font(24),fill=(103,229,193))
  d.text((x+45,y+782),label.upper(),font=effects.fit([label.upper()],385,24),fill=(242,247,249))
  d.text((x,y+824),name,font=effects.fit([name],430,25),fill=(151,190,189))
 d.text((74,2160),'Escolha pelo nome. Peça à sua IA. Confira a prévia.',font=effects.font(32),fill=(144,169,185))
 im.save(ASSETS/filename,quality=92)

def make():
 source=Image.open(ASSETS/'example-frame.jpg').convert('RGB');frame=np.array(source)
 face=effects.FaceTracker().update(frame)
 if face is None:raise RuntimeError('O frame de exemplo precisa de um rosto detectável.')
 print('Rosto detectado:',face,flush=True)
 for name in effects.EFFECTS:
  sample=.48 if name=='dot-reveal' else 1.7 if name=='liquid-glass-graph' else 2.7
  out,_=effects.render_effect(frame.copy(),face.copy(),plan(name),sample)
  Image.fromarray(out).save(ASSETS/f'{name}.jpg',quality=90)
 board(NEW,'creative-six.jpg','Seis ideias novas para seus vídeos','Scanner · Lente · Mapa · Pergunta e resposta · Fonte · Pulso')
 board(POPULAR,'preview.jpg',f'{COUNT} efeitos. Você escolhe o nome.','Alguns exemplos para começar · Claude Code + Codex')
 names=list(effects.EFFECTS);pages=math.ceil(len(names)/8)
 for i in range(pages):
  board(names[i*8:(i+1)*8],f'gallery-{i+1:02d}.jpg',f'Catálogo de efeitos · {i+1} de {pages}','Todos os exemplos usam o mesmo frame de boca fechada.')
 hero=Image.new('RGB',(1600,580),(9,18,29));d=ImageDraw.Draw(hero)
 d.rounded_rectangle((70,55,345,99),radius=22,fill=(17,56,58));d.text((91,64),'MED VIDEO EFFECTS',font=effects.font(22),fill=(114,234,200))
 d.text((70,145),'Você grava.',font=effects.font(91),fill=(245,249,250))
 d.text((70,254),'Sua IA aplica os efeitos.',font=effects.fit(['Sua IA aplica os efeitos.'],1450,91),fill=(103,229,193))
 d.text((73,394),f'{COUNT} efeitos para vídeos de médicos · Claude Code + Codex',font=effects.font(35),fill=(164,186,202))
 d.text((75,492),'INSTALE UMA VEZ   /   PEÇA PELO NOME   /   CONFIRA O RESULTADO',font=effects.font(24),fill=(132,158,178))
 hero.save(ASSETS/'hero.png')
 gifs=[];small=np.array(source.resize((270,480),Image.Resampling.LANCZOS));sf=face*(270/source.width)
 for name in POPULAR:
  e=plan(name,2)
  for i in range(12):
   out,_=effects.render_effect(small.copy(),sf.copy(),e,i/6)
   tile=Image.new('RGB',(270,520),(9,18,29));tile.paste(Image.fromarray(out),(0,40))
   ImageDraw.Draw(tile).text((12,12),INFO[name][1],font=effects.fit([INFO[name][1]],246,16),fill=(245,249,250))
   gifs.append(tile)
 gifs[0].save(ASSETS/'demo.gif',save_all=True,append_images=gifs[1:],duration=167,loop=0,optimize=True)
 # Generate the reference from the same names used by the command-line tool.
 doc=['# Escolha seu efeito','', '#Saude #Tecnologia','',
      'Escolha um nome e peça à sua IA: **“Use o efeito Órbita no meu vídeo, de 3 a 6 segundos.”**',
      '', '[Voltar ao início](../README.md) · [Opções avançadas](AVANCADO.md)','',
      f'São versões locais dos {COUNT} estilos. Cartões usam suas imagens, quando fornecidas; sem elas, usam um frame do próprio vídeo. Os layouts são adaptados ao espaço disponível e não fazem recorte semântico da pessoa.','',
      '| Nº | Peça por este nome | Nome técnico | O que acontece |','|---|---|---|---|']
 for i,(name,label,desc,_) in enumerate(CATALOG):doc.append(f'| {i+1} | {label} | `{name}` | {desc} |')
 doc+=['','## Seis efeitos criativos novos','','![Seis efeitos novos](../assets/creative-six.jpg)','','Peça “Use Mapa de ideias com Consulta, Dúvidas, Histórico e Próximos passos”. Para Virada de pergunta, forneça a pergunta e a resposta; para Fonte em destaque, forneça o ponto e a referência.']
 for i in range(pages):doc+=['',f'## Galeria {i+1}', '',f'![Exemplos {i*8+1} a {min(COUNT,(i+1)*8)}](../assets/gallery-{i+1:02d}.jpg)']
 doc+=['','## Um pedido com vários efeitos','','```text','Use Título em caixa no início, Órbita de 4 a 7 segundos','e Checklist de 10 a 14 segundos. Preserve minha voz e gere uma prévia.','```','','Contadores, gráficos e rankings são recursos visuais. Forneça seus textos, dados e imagens; os exemplos não demonstram resultados clínicos.','']
 (ROOT/'docs/CATALOGO.md').write_text('\n'.join(doc),encoding='utf-8')
 print(f'{COUNT} thumbnails, {pages} galerias, capa, GIF e catálogo prontos.',flush=True)

if __name__=='__main__':make()
