#!/usr/bin/env python3
"""Exemplos do catálogo com um frame autorizado. #Saude #Tecnologia"""
from pathlib import Path
import math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import effects
from catalog import CATALOG
import gallery_art
import json
import shutil

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'assets'
NEW=['idea-scan','focus-lens','concept-map','question-flip','source-pin','idea-pulse']
POPULAR=['backdrop-word','orbit','red-collage','glass-widgets','split-headline','phone-fan']
COUNT=len(CATALOG)
INFO={name:(i+1,label,desc) for i,(name,label,desc,_) in enumerate(CATALOG)}

def plan(name,end=4):
 index=list(effects.EFFECTS).index(name)
 e=gallery_art.preset(name,index,ASSETS/'demo-cards');e['end']=end
 return e


def display_font(text,width,size):
 path=Path('/System/Library/Fonts/Supplemental/Arial Black.ttf')
 if not path.exists():return effects.fit([text],width,size)
 while size>12:
  f=ImageFont.truetype(str(path),size)
  if f.getlength(text)<=width:return f
  size-=1
 return effects.fit([text],width,size)


def board(items,filename,title,subtitle):
 # Almost all the space belongs to the real rendered portraits.
 columns=3;rows=math.ceil(len(items)/columns)
 tilew,tileh=480,854;gutter=14;margin=24;header=158
 W=columns*tilew+(columns-1)*gutter+margin*2
 H=header+rows*tileh+(rows-1)*gutter+margin
 im=Image.new('RGB',(W,H),(13,17,23));d=ImageDraw.Draw(im)
 d.text((margin,20),'MED VIDEO EFFECTS',font=effects.font(18),fill=(158,174,187))
 d.text((margin,52),title,font=display_font(title,W-margin*2,49),fill=(248,244,235))
 d.text((margin,118),subtitle,font=effects.fit([subtitle],W-margin*2,20),fill=(143,160,173))
 for i,name in enumerate(items):
  x=margin+(i%columns)*(tilew+gutter);y=header+(i//columns)*(tileh+gutter)
  with Image.open(ASSETS/f'{name}.jpg') as photo:
   tile=photo.convert('RGBA').resize((tilew,tileh),Image.Resampling.LANCZOS)
  # Readable title strip belongs to the gallery, not the video effect.
  alpha=np.zeros((tileh,tilew),dtype=np.uint8)
  fadeh=150;alpha[-fadeh:]=np.linspace(0,244,fadeh,dtype=np.uint8)[:,None]
  gradient=Image.new('RGBA',tile.size,(5,9,15,0));gradient.putalpha(Image.fromarray(alpha))
  tile=Image.alpha_composite(tile,gradient);td=ImageDraw.Draw(tile)
  number,label,_=INFO[name];accent=tuple(int(gallery_art.PALETTE[(number-1)%len(gallery_art.PALETTE)][j:j+2],16) for j in (1,3,5))
  td.rounded_rectangle((17,17,75,56),radius=12,fill=(9,17,24,210))
  effects.text_center(td,46,36,str(number).zfill(2),effects.font(22),accent+(255,))
  # A compact, consistent footer stays readable at GitHub's content width.
  td.text((20,tileh-91),label.upper(),font=display_font(label.upper(),tilew-40,30),fill=(255,251,243,255))
  td.text((21,tileh-43),name,font=effects.fit([name],tilew-42,22),fill=accent+(255,))
  td.rectangle((20,tileh-9,tilew-20,tileh-6),fill=accent+(255,))
  mask=Image.new('L',tile.size);ImageDraw.Draw(mask).rounded_rectangle((0,0,tilew-1,tileh-1),radius=19,fill=255)
  tile.putalpha(mask);im.paste(tile.convert('RGB'),(x,y),mask)
 im.save(ASSETS/filename,quality=94,subsampling=0)


def make():
 source=gallery_art.editorial_frame();gallery_art.demo_cards();frame=np.array(source)
 face=effects.FaceTracker().update(frame)
 if face is None:raise RuntimeError('O frame de exemplo precisa de um rosto detectável.')
 print('Rosto detectado:',face,flush=True)
 for name in effects.EFFECTS:
  sample=.48 if name=='dot-reveal' else 1.7 if name=='liquid-glass-graph' else 2.7
  out,_=effects.render_effect(frame.copy(),face.copy(),plan(name),sample)
  Image.fromarray(out).save(ASSETS/f'{name}.jpg',quality=90)
 # Preserve earlier asset URLs with the refreshed canonical preview.
 for alias,name in effects.ALIASES.items():
  if (ASSETS/f'{alias}.jpg').exists():shutil.copyfile(ASSETS/f'{name}.jpg',ASSETS/f'{alias}.jpg')
 board(NEW,'creative-six.jpg','Seis ideias novas para seus vídeos','Scanner · Lente · Mapa · Pergunta e resposta · Fonte · Pulso')
 board(POPULAR,'preview.jpg',f'{COUNT} efeitos. Você escolhe o nome.','Alguns exemplos para começar · Claude Code + Codex')
 names=list(effects.EFFECTS);pages=math.ceil(len(names)/9)
 for i in range(pages):
  board(names[i*9:(i+1)*9],f'gallery-{i+1:02d}.jpg',f'Catálogo de efeitos · {i+1} de {pages}','Retrato real · Presets editoriais · Efeito pelo nome')
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
      f'São {COUNT} efeitos locais. As prévias usam enquadramento editorial, paletas e textos de exemplo. As capas ilustrativas dos cartões acompanham o repositório; você pode usar suas próprias imagens. Os layouts respeitam o espaço disponível e não fazem recorte semântico da pessoa.','',
      '| Nº | Peça por este nome | Nome técnico | O que acontece |','|---|---|---|---|']
 for i,(name,label,desc,_) in enumerate(CATALOG):doc.append(f'| {i+1} | {label} | `{name}` | {desc} |')
 doc+=['','## Seis efeitos criativos novos','','![Seis efeitos novos](../assets/creative-six.jpg)','','Peça “Use Mapa de ideias com Consulta, Dúvidas, Histórico e Próximos passos”. Para Virada de pergunta, forneça a pergunta e a resposta; para Fonte em destaque, forneça o ponto e a referência.']
 for i in range(pages):doc+=['',f'## Galeria {i+1}', '',f'![Exemplos {i*9+1} a {min(COUNT,(i+1)*9)}](../assets/gallery-{i+1:02d}.jpg)']
 doc+=['','## Um pedido com vários efeitos','','```text','Use Título em caixa no início, Órbita de 4 a 7 segundos','e Checklist de 10 a 14 segundos. Preserve minha voz e gere uma prévia.','```','','Contadores, gráficos e rankings são recursos visuais. Forneça seus textos, dados e imagens; os exemplos não demonstram resultados clínicos.','']
 (ROOT/'docs/CATALOGO.md').write_text('\n'.join(doc),encoding='utf-8')
 presets=[]
 for name in names:
  e=plan(name);e={k:v for k,v in e.items() if not k.startswith('_')}
  if 'images' in e:e['images']='assets/demo-cards'
  presets.append(e)
 (ROOT/'examples/gallery-presets.json').write_text(json.dumps({'tags':['#Saude','#Tecnologia'],'source':'assets/editorial-frame.jpg','note':'Escolha um efeito por vez; os presets não formam uma sequência.','presets':{e['effect']:e for e in presets}},ensure_ascii=False,indent=2)+'\n')
 print(f'{COUNT} thumbnails, {pages} galerias editoriais, capa e GIF prontos.',flush=True)

if __name__=='__main__':make()
