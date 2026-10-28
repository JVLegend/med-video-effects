# Guia avançado

#Saude #Tecnologia

[Voltar ao início](../README.md) · [Ver os 51 efeitos](CATALOGO.md)

Este guia é opcional. Para começar, basta pedir à sua IA para instalar e usar os efeitos pelo nome.

## Instalação

### 1. Pré-requisitos

- **Python 3.10 ou mais recente** e **Git**.
- **FFmpeg 6 ou mais recente**, incluindo `ffprobe`, disponível no terminal.
- Um vídeo seu, com a pessoa de frente e espaço acima da cabeça para os textos.

| Sistema | Instalar FFmpeg |
|---|---|
| macOS com Homebrew | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Windows com winget | `winget install Gyan.FFmpeg` |

No Windows, abra um terminal novo depois da instalação. Em alguns Linux, instale também `python3-venv`. Os comandos de instalação abaixo são para terminal local; a skill precisa ter acesso aos seus arquivos e poder executar Python/FFmpeg.

### 2. Escolha onde instalar

**Claude Code — skill pessoal:**

```sh
git clone https://github.com/JVLegend/med-video-effects.git ~/.claude/skills/med-video-effects
cd ~/.claude/skills/med-video-effects
python3 scripts/setup.py
```

**Codex — skill pessoal:**

```sh
git clone https://github.com/JVLegend/med-video-effects.git ~/.agents/skills/med-video-effects
cd ~/.agents/skills/med-video-effects
python3 scripts/setup.py
```

No PowerShell, use `python` no lugar de `python3` e `$HOME/.claude/skills/med-video-effects` ou `$HOME/.agents/skills/med-video-effects` no lugar de `~`.

O setup cria `.venv` dentro do clone e instala NumPy, OpenCV e Pillow ali. Ele não altera configurações do assistente e não instala pacotes no Python global. A instalação baixa dependências; **a renderização não envia o vídeo para serviços externos**.

Se a skill não aparecer, reinicie a sessão da ferramenta. Você também pode clonar em qualquer pasta e usar o terminal, sem instalar uma skill.

> Guias das ferramentas: [skills no Claude Code](https://code.claude.com/docs/en/skills) e [skills no Codex](https://developers.openai.com/codex/skills/). Este projeto não tem afiliação com Anthropic ou OpenAI.

## Uso direto no terminal

Execute dentro da pasta do clone. Nos exemplos, `.venv/bin/python` é o Python local do macOS/Linux. No Windows, troque por `.venv\Scripts\python.exe`.

**Confira o ambiente e veja os efeitos:**

```sh
.venv/bin/python scripts/effects.py doctor
.venv/bin/python scripts/effects.py list
```

**Gere uma prévia do título no segundo 2:**

```sh
.venv/bin/python scripts/effects.py preview "/caminho/video.mp4" "previa.png" \
  --effect headline --text "Informação clara|para cuidar melhor" \
  --start 0 --end 4 --at 2
```

**Exporte o mesmo efeito em vídeo:**

```sh
.venv/bin/python scripts/effects.py render "/caminho/video.mp4" "video-editado.mp4" \
  --effect headline --text "Informação clara|para cuidar melhor" \
  --start 0 --end 4
```

**Use um checklist:**

```sh
.venv/bin/python scripts/effects.py render "/caminho/video.mp4" "video-checklist.mp4" \
  --effect checklist --text "Observe|Anote suas dúvidas|Converse com seu médico" \
  --start 4 --end 8
```

`|` separa linhas ou itens. Os nomes antigos continuam funcionando. Consulte `scripts/effects.py list` e o catálogo para os nomes atuais; cada efeito tem um limite próprio de linhas, geralmente de uma a três. Comment aceita uma pergunta, quebrada automaticamente em até duas linhas visíveis; stamp e timeline aceitam uma linha. Carimbos aceitam até 32 caracteres; outros textos, até 180, sujeitos ao espaço disponível. O nome do efeito também pode ser escrito em português, entre aspas no terminal. Os itens do checklist são marcados automaticamente durante o intervalo; não há sincronização por palavra.

### Vários efeitos no mesmo vídeo

Crie um plano como este:

```json
{
  "effects": [
    {"effect": "headline", "start": 0, "end": 3, "text": "Informação clara|para cuidar melhor"},
    {"effect": "focus", "start": 4, "end": 6},
    {"effect": "checklist", "start": 7, "end": 11, "text": "Observe|Anote suas dúvidas|Converse com seu médico"}
  ]
}
```

Salve como `meu-plano.json` e execute:

```sh
.venv/bin/python scripts/effects.py preview "/caminho/video.mp4" "checklist-previa.png" \
  --plan "meu-plano.json" --at 9

.venv/bin/python scripts/effects.py render "/caminho/video.mp4" "video-completo.mp4" \
  --plan "meu-plano.json"
```

O [plano inicial](../examples/plan.json) mantém a sequência de seis efeitos e precisa de pelo menos 18 segundos. O [plano dos 51 efeitos](../examples/all-effects.json) demonstra todo o catálogo em 102 segundos; ajuste os intervalos ao seu vídeo. Intervalos sobrepostos são rejeitados. Deixe trechos limpos entre entradas; não é necessário preencher o vídeo inteiro.

### Exemplos de efeitos

```sh
.venv/bin/python scripts/effects.py render "/caminho/video.mp4" "video-pergunta.mp4" \
  --effect comment --text "Qual é sua dúvida?" --start 0 --end 4

.venv/bin/python scripts/effects.py render "/caminho/video.mp4" "video-etapas.mp4" \
  --effect lineup --text "Observe|Pergunte|Converse" --start 4 --end 8

.venv/bin/python scripts/effects.py render "/caminho/video.mp4" "video-pontos.mp4" \
  --effect dot-reveal --start 0 --end 2
```

A contagem regressiva divide o intervalo em três partes iguais. Comentários digitados e cartões usam o tempo do efeito, sem acompanhar palavras faladas. A timeline representa o progresso do trecho, não um dado clínico. Capa e cartão de vidro ficam na frente da imagem, acima do rosto; não há texto atrás da pessoa.

### Ajustes disponíveis

| Opção | Exemplo | Resultado |
|---|---|---|
| `--width` | `--width 720` | Saída mais leve, com altura proporcional |
| `--font` | `--font "/caminho/fonte.ttf"` | Usa uma fonte local de sua escolha |
| `--start` / `--end` | `--start 3 --end 6` | Intervalo em segundos para um efeito |
| `--at` | `--at 4.5` | Instante da prévia PNG |
| `--plan` | `--plan "meu-plano.json"` | Sequência de efeitos em JSON |

A largura padrão é 1080 px; em vídeo vertical 9:16 isso resulta em 1080×1920. A saída usa H.264/MP4 a 30 fps. A rotação do celular é aplicada pelo FFmpeg. AAC é copiado; outros formatos de áudio são convertidos para AAC. Um vídeo sem áudio continua sem áudio. Aumentar a resolução não recupera detalhes perdidos na gravação.

## O que esta versão faz — e seus limites

- O detector de rosto do OpenCV funciona melhor com uma pessoa de frente, luz suficiente e rosto visível. Não usa reconhecimento de identidade.
- Foco, aproximação e spotlight são omitidos quando não há rosto detectável. Títulos se adaptam ao espaço acima do rosto; podem ser reduzidos ou omitidos se não couberem. **Inspecione as prévias.**
- Spotlight usa uma máscara geométrica suave. A aproximação usa zoom digital. Não há recorte semântico de cabelo/corpo ou texto realmente atrás da pessoa. Órbita, cartões e palavras usam o espaço acima do rosto; esta é uma adaptação de enquadramento, não uma máscara de pessoa. Não há seleção entre vários apresentadores.
- Esta versão trabalha com SDR. HDR deve ser convertido antes; o script recusa HDR identificado para evitar exportar cores incorretas.
- As fontes vêm do sistema ou do Pillow. O visual pode variar entre sistemas; use `--font` para padronizar.
- Não há legendas automáticas, transcrição, música, efeitos sonoros ou publicação automática.

### Para quem grava conteúdo de saúde

Use texto que você revisou e material cuja publicação está autorizada. Os exemplos organizam uma explicação; não fornecem diagnóstico, conduta, promessa de resultado ou validação científica. O projeto não analisa prontuários nem verifica afirmações clínicas.

Para testar, prefira uma gravação sua sem pacientes ou informações identificáveis. Os comandos e o vídeo são locais, mas o que você enviar no chat segue as regras da ferramenta de IA usada.

## Problemas comuns

| Situação | Como resolver |
|---|---|
| `ffmpeg` ou `ffprobe` não encontrado | Instale FFmpeg, reabra o terminal e rode `doctor` |
| `No module named cv2/PIL/numpy` | Rode `python3 scripts/setup.py` e use o Python da `.venv` |
| A skill não aparece | Confira a pasta escolhida e reinicie a sessão |
| A saída já existe | Escolha outro nome; o script não sobrescreve arquivos |
| O título ficou pequeno ou não apareceu | Encurte o texto, divida com `|` ou use `split` para criar espaço |
| Foco/spotlight não apareceu | Escolha um trecho de frente e bem iluminado; o rastreamento é básico |
| O render demora | Comece com `--width 720` e efeitos curtos |
| O vídeo tem menos de 18 segundos | Ajuste os intervalos do plano de exemplo à duração do seu vídeo |

## Para desenvolver

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/build_gallery.py
```

A instalação isolada e os testes foram validados em macOS ARM, Python 3.14 e FFmpeg 8.1. As instruções de Linux e Windows ainda precisam de validação nesses sistemas.

Os testes geram vídeos temporários para verificar exportação, preservação de áudio, proteção do original e erros de plano. As seis galerias e os 51 thumbnails são gerados pelo próprio renderizador usando a imagem-base em `assets/`.

Quer contribuir? Abra uma issue com o efeito desejado, uma descrição do movimento e um exemplo que você possa compartilhar. Melhorias de tracking, enquadramento e instalação são bem-vindas. Se abrir um PR visual, inclua antes/depois e como testou.

## Licença e imagens

O código é distribuído sob a [licença MIT](../LICENSE). Dependências mantêm suas próprias licenças. A fotografia indicada pelo usuário e seus derivados em `assets/` estão excluídos da licença do código; a autoria e a licença da fotografia de origem não foram informadas; veja [as informações das imagens](../assets/README.md). Substitua pelo seu próprio material.

Criado por [João Victor · @JVLegend](https://github.com/JVLegend).

<!-- #Saude #Tecnologia #JoaoVictor -->

## Usar imagens próprias

Para efeitos com cartões, mural, órbita, leque e imagem de apoio, forneça uma pasta local de JPG, PNG ou WebP:

```sh
.venv/bin/python scripts/effects.py render "/caminho/video.mp4" "video-orbita.mp4" \
  --effect orbit --images "/caminho/imagens" --start 3 --end 7
```

Em planos JSON, use `"images": "/caminho/imagens"` dentro do efeito. São carregadas até 12 imagens locais. Sem imagens, o efeito reaproveita um frame do vídeo; não baixa B-roll nem inventa uma grade de publicações reais. A composição de vidro usa desfoque e transparência; não simula refração física. O gráfico de exemplo traz a indicação de ilustração e não aceita dados clínicos automaticamente.

A pausa congela o quadro do início do efeito, mantendo o áudio e o tempo do vídeo. Os demais elementos usam posições seguras quando há rosto detectado; revise os casos sem espaço, sem rosto ou com movimento intenso.

### Nomes antigos

`focus`, `grade`, `receipt`, `comment`, `countdown`, `cover`, `glass`, `stamp`, `split` e `headline` continuam aceitos. O catálogo exibe os nomes atuais.

## Seis efeitos de explicação visual

| Nome | Como personalizar com `--text` |
|---|---|
| Scanner de ideias | Uma frase curta que será revelada pela faixa luminosa |
| Lente explicativa | Uma legenda; use `--images` para ampliar um detalhe de imagem própria |
| Mapa de ideias | `Tema central|Conceito 1|Conceito 2|Conceito 3` |
| Virada de pergunta | `Sua pergunta?|Sua resposta` |
| Fonte em destaque | `Seu ponto principal|Sua referência` |
| Pulso de ideia | Uma frase curta para acompanhar a onda luminosa |

Scanner e Pulso são animações gráficas: não analisam imagens, sinais biológicos ou saúde. A Lente amplia pixels existentes e não recupera detalhes. Fonte em destaque exibe o texto fornecido; não busca nem valida publicações. Conceitos e cartões usam o espaço acima do rosto, com redução ou quebra de texto para caber.

## Reproduzir a direção visual das thumbnails

As prévias usam a fotografia indicada pelo usuário, adaptada ao formato vertical com área superior para títulos (`assets/editorial-frame.jpg`), textos curtos e paletas editoriais. Os seis desenhos em `assets/demo-cards/` são capas ilustrativas fornecidas como imagens reais para os efeitos de cartões. Você pode substituí-los pelo seu material.

A cor dos grafismos pode ser alterada com `--accent` ou `accent` no plano:

```sh
.venv/bin/python scripts/effects.py render "/caminho/video.mp4" "video-lilas.mp4" \
  --effect orbit --images "assets/demo-cards" --accent "#D9B5FF" --start 0 --end 4
```

`examples/gallery-presets.json` contém uma coleção por nome, e não um plano para executar todos de uma vez. Escolha o preset desejado e copie o objeto para a lista `effects` de um plano. Ele informa os textos, a cor e as imagens usados nas thumbnails. A cor substitui a paleta de destaque dos grafismos; os demais tratamentos (preto e branco, cor vermelha, iluminação) pertencem ao próprio efeito. A renderização preserva o material original.
