#!/usr/bin/env python3
"""Recria a galeria com um frame autorizado. #Saude #Tecnologia"""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
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
 'lean-in':('07','APROXIMAÇÃO','Dê ênfase a um trecho da fala.'),
 'lineup':('08','CARTÕES NUMERADOS','Apresente três pontos em sequência.'),
 'receipt':('09','RECIBO','Uma nota se desenrola em papel.'),
 'comment':('10','COMENTÁRIO DIGITADO','Traga uma pergunta para a tela.'),
 'countdown':('11','CONTAGEM REGRESSIVA','Prepare o próximo assunto.'),
 'cover':('12','CAPA EDITORIAL','Abra um tema com uma manchete.'),
 'glass':('13','CARTÃO DE VIDRO','Uma ideia em um cartão translúcido.'),
 'stamp':('14','CARIMBO','Marque um ponto para anotar.'),
 'timeline':('15','TIMELINE','Mostre o avanço do trecho.'),
 'dot-reveal':('16','REVELAÇÃO POR PONTOS','A imagem se forma e ganha nitidez.'),
}
CUSTOM={
 'checklist':'Observe|Anote suas dúvidas|Converse com seu médico',
 'split':'Informação clara|para cuidar melhor',
 'headline':'Leve suas dúvidas|para a consulta',
 'lineup':'Observe|Pergunte|Converse',
 'receipt':'Antes da consulta|Organize suas dúvidas|Leve suas anotações',
 'comment':'Qual assunto você quer entender melhor?',
 'cover':'SAÚDE|Informação para uma boa conversa',
 'glass':'Na próxima consulta|Leve suas dúvidas',
 'stamp':'ANOTE',
 'timeline':'Uma ideia de cada vez',
}

def make():
 source=Image.open(ASSETS/'example-frame.jpg').convert('RGB')
 frame=np.array(source);face=effects.FaceTracker().update(frame)
 if face is None:raise RuntimeError('O frame de exemplo precisa de um rosto detectável.')
 print('Rosto detectado:',face,flush=True)
 examples=[]
 for name in effects.EFFECTS:
  plan=dict(effect=name,start=0,end=4,text=CUSTOM.get(name,''))
  sample=.48 if name=='dot-reveal' else 2.7
  out,_=effects.render_effect(frame.copy(),face.copy(),plan,sample)
  Image.fromarray(out).save(ASSETS/f'{name}.jpg',quality=91)
  examples.append((name,Image.fromarray(out)))
 # Two boards keep sixteen portrait thumbnails readable on GitHub.
 for page in range(2):
  W,H=1920,2230;board=Image.new('RGB',(W,H),(9,18,29));d=ImageDraw.Draw(board)
  d.rounded_rectangle((70,52,370,98),radius=23,fill=(17,56,58))
  d.text((92,62),'EXPERIMENTO · V0.2',font=effects.font(23),fill=(114,234,200))
  title='16 efeitos. Uma boa explicação.' if page==0 else 'Mais formas de explicar com clareza.'
  d.text((70,138),title,font=effects.fit([title],1770,81),fill=(244,248,250))
  d.text((74,244),f'Vídeos educativos para médicos · Claude Code + Codex  /  {page+1} de 2',font=effects.font(34),fill=(154,176,191))
  d.line((74,310,1846,310),fill=(42,63,77),width=2)
  for i,(name,im) in enumerate(examples[page*8:(page+1)*8]):
   col,row=i%4,i//4;x=70+col*450;y=350+row*880
   board.paste(im.resize((430,764),Image.Resampling.LANCZOS),(x,y))
   number,label,sub=LABELS[name]
   d.text((x,y+783),number,font=effects.font(24),fill=(103,229,193))
   d.text((x+45,y+782),label,font=effects.fit([label],385,24),fill=(242,247,249))
   d.text((x,y+824),sub,font=effects.fit([sub],430,22),fill=(151,173,189))
  d.text((74,2160),'Processamento local  /  Áudio preservado  /  Sem chave de API no renderizador',font=effects.font(29),fill=(144,169,185))
  board.save(ASSETS/('preview.jpg' if page==0 else 'preview-more.jpg'),quality=94)
 hero=Image.new('RGB',(1600,580),(9,18,29));hd=ImageDraw.Draw(hero)
 hd.rounded_rectangle((70,55,345,99),radius=22,fill=(17,56,58))
 hd.text((91,64),'MED VIDEO EFFECTS',font=effects.font(22),fill=(114,234,200))
 hd.text((70,145),'Sua explicação merece',font=effects.font(79),fill=(245,249,250))
 hd.text((70,244),'um vídeo mais claro.',font=effects.font(79),fill=(103,229,193))
 hd.text((73,385),'16 efeitos locais para Claude Code e Codex',font=effects.font(35),fill=(164,186,202))
 hd.text((75,474),'PYTHON + FFMPEG     ·     PORTUGUÊS     ·     EXPERIMENTO ABERTO',font=effects.font(24),fill=(132,158,178))
 hero.save(ASSETS/'hero.png')
 # The GIF animates the authorized still; it contains no extra video frames.
 gifs=[];small=np.array(source.resize((270,480),Image.Resampling.LANCZOS));sf=face*(270/source.width)
 for name in effects.EFFECTS:
  for i in range(12):
   plan=dict(effect=name,start=0,end=2,text=CUSTOM.get(name,''))
   out,_=effects.render_effect(small.copy(),sf.copy(),plan,i/6)
   tile=Image.new('RGB',(270,520),(9,18,29));tile.paste(Image.fromarray(out),(0,40))
   ImageDraw.Draw(tile).text((12,12),LABELS[name][1],font=effects.fit([LABELS[name][1]],246,16),fill=(245,249,250))
   gifs.append(tile)
 gifs[0].save(ASSETS/'demo.gif',save_all=True,append_images=gifs[1:],duration=167,loop=0,optimize=True)
 print('16 thumbnails, duas galerias, capa e GIF prontos.',flush=True)

if __name__=='__main__':make()
