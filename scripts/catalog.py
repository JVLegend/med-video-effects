"""Catálogo público e nomes alternativos. #Tecnologia #Saude"""
import unicodedata

# canonical, friendly name, description, existing renderer name (when available)
CATALOG = [
 ('noise','Mural de vídeos','Cartões de vídeo se acumulam acima do apresentador.',None),
 ('lineup','Cartões numerados','Até três cartões entram em sequência.','lineup'),
 ('locked-on','Foco no rosto','Cantos de enquadramento acompanham uma aproximação suave.','focus'),
 ('orbit','Órbita','Cartões circulam em uma órbita no espaço acima do rosto.',None),
 ('lean-in','Aproximação','Uma aproximação rápida enfatiza a fala.','lean-in'),
 ('backdrop-word','Palavra gigante','Uma palavra grande surge no espaço acima do rosto.',None),
 ('spotlight','Spotlight','O ambiente escurece ao redor do apresentador.','spotlight'),
 ('the-bill','Recibo','Uma nota de papel se desenrola com seus pontos.','receipt'),
 ('moody','Cor cinematográfica','Contraste discreto e sombras frias.','grade'),
 ('swipe','Antes e depois','Um divisor revela a mudança de cor.',None),
 ('todo','Lista de tarefas','Uma lista recebe marcações em sequência.',None),
 ('comment-box','Comentário digitado','Uma pergunta é digitada em um cartão.','comment'),
 ('tap','Botão seguir','Um botão muda de Seguir para Seguindo.',None),
 ('pause-point','Pausa com seta','O quadro congela e uma seta destaca um ponto.',None),
 ('uninstall','Glitch','Uma barra avança enquanto faixas deslocam a imagem.',None),
 ('reel-frame','Moldura de vídeo','A gravação se acomoda em um cartão vertical.',None),
 ('shortcut-rain','Chuva de teclas','Teclas animadas caem no espaço acima do rosto.',None),
 ('reject-stamp','Carimbo','Um carimbo colorido aparece inclinado.','stamp'),
 ('countdown-flip','Contagem regressiva','Números 3, 2 e 1 preparam o próximo assunto.','countdown'),
 ('rabbit-hole','Túnel','Cópias do quadro criam um túnel visual.',None),
 ('cover-star','Capa editorial','Manchete e subtítulo formam uma capa.','cover'),
 ('scribble','Rabiscos','Traços de marcador aparecem ao redor do enquadramento.',None),
 ('glass-widgets','Widgets de vidro','Pequenos cartões translúcidos flutuam acima do rosto.',None),
 ('red-collage','Colagem vermelha','Imagem monocromática e faixas vermelhas de texto.',None),
 ('split-headline','Tela dividida','Um título abre espaço no alto da imagem.','split'),
 ('pastel-word','Palavra pastel','Lavanda, palavra de destaque e cartão de perfil.',None),
 ('check-pills','Pílulas marcadas','Etiquetas azuis recebem marcações uma a uma.',None),
 ('timeline','Timeline','Uma linha de edição acompanha o avanço do trecho.','timeline'),
 ('headline-box','Título em caixa','Uma frase entra em uma caixa branca.','headline'),
 ('profile-wall','Mural de perfil','Uma grade de cartões ocupa o espaço acima do rosto.',None),
 ('tier-list','Ranking','Um item se move para a primeira faixa de uma classificação.',None),
 ('broll-split','Imagem de apoio','Uma imagem de apoio ocupa a parte superior da tela.',None),
 ('phone-fan','Leque de celulares','Cartões de celular se abrem em leque.',None),
 ('dot-reveal','Revelação por pontos','Pontos formam a imagem e dão lugar ao quadro nítido.','dot-reveal'),
 ('headline-wall','Mural de títulos','Manchetes se acumulam em cartões.',None),
 ('checklist','Checklist','Uma lista escura recebe marcações.','checklist'),
 ('liquid-glass-graph','Gráfico de vidro','Um gráfico ilustrativo se desenha em cartão translúcido.',None),
 ('carousel-spin','Carrossel','Cartões giram e desaceleram no espaço superior.',None),
 ('match-cut','Palavra em destaque','Cartões mudam mantendo uma palavra no mesmo lugar.',None),
 ('apple-toggles','Interruptores','Chaves visuais são ligadas uma a uma.',None),
 ('led-sign','Letreiro LED','Uma frase luminosa se acende no alto da imagem.',None),
 ('slow-push','Aproximação lenta','Zoom gradual e fundo mais suave.',None),
 ('over-the-shoulder-zoom','Zoom lateral','A imagem se aproxima de lados alternados com cartões.',None),
 ('messages','Mensagens','Notificações aparecem em sequência.',None),
 ('place-in-grid','Grade de vídeos','O apresentador entra no centro de uma grade 3 por 3.',None),
 ('idea-scan','Scanner de ideias','Uma faixa luminosa revela a palavra principal.',None),
 ('focus-lens','Lente explicativa','Uma lente amplia um detalhe real da sua imagem.',None),
 ('concept-map','Mapa de ideias','Um tema se conecta a três conceitos em sequência.',None),
 ('question-flip','Virada de pergunta','Um cartão gira de pergunta para resposta.',None),
 ('source-pin','Fonte em destaque','Uma referência ganha cartão e sublinhado animado.',None),
 ('idea-pulse','Pulso de ideia','Uma onda luminosa destaca uma frase.',None),
]
EFFECTS = {name: desc for name, _, desc, _ in CATALOG}
ENGINE_NAMES = {name: engine or name for name, _, _, engine in CATALOG}
ALIASES = {engine: name for name, _, _, engine in CATALOG if engine and engine != name}
# One-card glass remains a supported command, now rendered as a widget composition.
ALIASES['glass']='glass-widgets'

def slug(text):
    text=unicodedata.normalize('NFKD',str(text).lower())
    text=''.join(c for c in text if not unicodedata.combining(c))
    return '-'.join(text.replace('_','-').replace('-',' ').split())

FRIENDLY = {slug(friendly): name for name, friendly, _, _ in CATALOG}

def resolve_effect(value):
    key=slug(value)
    name=ALIASES.get(key,FRIENDLY.get(key,key))
    if name not in EFFECTS:
        raise ValueError(f'Efeito desconhecido: {value}. Use o comando list.')
    return name
