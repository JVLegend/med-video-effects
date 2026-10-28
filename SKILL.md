---
name: med-video-effects
description: >-
  Aplique seis efeitos locais a vídeos educativos de médicos: foco no rosto, spotlight,
  cor cinematográfica, checklist, tela dividida e título em caixa. Use com vídeos próprios
  e texto fornecido pelo usuário; não transcreve nem produz orientação clínica.
---

# Med Video Effects

#Saude #Tecnologia

Os scripts são relativos à pasta deste `SKILL.md`; use caminhos absolutos ao executá-los a partir de outro diretório.

## Preparar e escolher

- Se `.venv` ainda não existir, execute `python3 scripts/setup.py` nesta pasta. Ele instala dependências apenas no ambiente do clone. Se faltar FFmpeg, siga o erro de instalação; não altere configurações do assistente.
- Python local: `.venv/bin/python` no macOS/Linux, `.venv\Scripts\python.exe` no Windows.
- Consulte `scripts/effects.py list` e a tabela do `README.md` para escolher o efeito. Texto e sentido clínico vêm do usuário ou de uma transcrição que ele forneceu. O renderizador não escuta áudio nem localiza palavras faladas.
- Use os caminhos do vídeo e da saída indicados pelo usuário. Na falta de timing, entradas de 2–4 s funcionam como rascunho. Preserve o original e escolha um nome novo para cada versão.

## Conferir e exportar

Uma entrada simples:

```sh
.venv/bin/python scripts/effects.py preview "/caminho/video.mp4" "/caminho/previa.png" --effect headline --text "Leve suas dúvidas|para a consulta" --start 0 --end 4 --at 2
.venv/bin/python scripts/effects.py render "/caminho/video.mp4" "/caminho/video_editado.mp4" --effect headline --text "Leve suas dúvidas|para a consulta" --start 0 --end 4
```

Para várias entradas, escreva uma lista `effects` com `effect`, `start`, `end` e `text` opcional. Veja `examples/plan.json`. Use `--plan /caminho/plano.json` no lugar de `--effect`. Intervalos sobrepostos são rejeitados. `|` separa até três itens/linhas em checklist/split e duas linhas em headline.

Inspecione prévias no meio de cada efeito, ajustando textos e enquadramento antes de renderizar. O detector é simples: se perder o rosto, foco e spotlight são omitidos; títulos podem ser reduzidos ou omitidos quando falta espaço. Não afirme que houve recorte da pessoa ou tracking preciso sem verificar os quadros.

A exportação usa H.264, 30 fps e largura de 1080 px; `--width 720` gera uma prévia mais leve. AAC é copiado; outros áudios são convertidos para AAC. Vídeo sem áudio continua sem áudio. HDR exige conversão prévia para SDR. Confira início/meio/fim, duração e decodificação antes de entregar. Publicar conteúdo ou enviar vídeos a serviços externos exige pedido separado; este renderizador trabalha localmente.
