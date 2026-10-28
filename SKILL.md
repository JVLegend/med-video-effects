---
name: med-video-effects
description: >-
  Edite vídeos educativos de médicos com 51 efeitos locais: títulos, órbita, foco,
  checklist, cartões, vidro, gráficos ilustrativos, notificações e transições.
  Use quando o usuário pedir um efeito pelo nome ou uma edição visual de vídeo próprio.
---

# Med Video Effects

#Saude #Tecnologia

Os caminhos abaixo são relativos a este SKILL.md. Execute scripts por caminho absoluto quando estiver em outra pasta.

## Instalar e preparar

O pedido para instalar este repositório inclui preparar os programas necessários, conforme as permissões do ambiente. Confira o sistema e a presença de Python 3.10+, Git, FFmpeg 6+ e ffprobe; reutilize o que já existir. Os comandos por sistema e os locais de instalação no Claude Code/Codex estão em [docs/AVANCADO.md](docs/AVANCADO.md). Se uma permissão do sistema impedir a instalação, informe exatamente o requisito restante.

Execute `python3 scripts/setup.py` na pasta do clone. Ele cria `.venv` e instala dependências isoladas. Python do projeto: `.venv/bin/python` no macOS/Linux; `.venv\Scripts\python.exe` no Windows. Confirme com `scripts/effects.py doctor`. Não altere configurações globais do assistente para instalar a skill.

## Interpretar o pedido

O usuário pode pedir pelo nome em português, sem slash command. Consulte [docs/CATALOGO.md](docs/CATALOGO.md) ou execute `scripts/effects.py list`. O CLI aceita nomes técnicos, nomes em português e aliases antigos. Use `--effect "Título em caixa"` ou `--effect headline-box`.

Para reproduzir uma thumbnail, consulte `examples/gallery-presets.json`: escolha o item em `presets` pelo nome e aproveite texto, `accent` e imagens locais. O arquivo é uma coleção de alternativas, não uma sequência para executar inteira. O reenquadramento e as capas ilustrativas estão documentados em `assets/README.md`.

Use o vídeo, o texto, as imagens e o destino informados. Pergunte só o que faltar para executar. Sem timing, uma entrada inicial de 2–4 s pode servir como rascunho. O script não transcreve: não invente o segundo em que uma palavra foi dita. Textos clínicos vêm do usuário; gráficos de exemplo são ilustrações, sem validação clínica.

## Conferir e renderizar

```sh
.venv/bin/python scripts/effects.py preview "/caminho/video.mp4" "/caminho/previa.png" --effect "Título em caixa" --text "Leve suas dúvidas|para a consulta" --start 0 --end 4 --at 2
.venv/bin/python scripts/effects.py render "/caminho/video.mp4" "/caminho/video_editado.mp4" --effect "Título em caixa" --text "Leve suas dúvidas|para a consulta" --start 0 --end 4
```

Para várias entradas, escreva uma lista `effects` com `effect`, `start`, `end` e `text` opcional; use `--plan`. Veja `examples/plan.json` e `examples/all-effects.json` (51 efeitos em 102 s). Intervalos sobrepostos são rejeitados. Para cartões/B-roll, use `--images` ou `images` no plano com uma pasta local de JPG/PNG/WebP. Sem imagens, o efeito reutiliza um frame do vídeo.

Inspecione as prévias e ajuste texto/enquadramento antes de exportar. Preserve o original e escolha uma saída nova. O detector é básico; se não encontrar rosto ou espaço, alguns elementos são omitidos. Órbita e palavras usam espaço acima do rosto, sem recorte semântico. Não prometa camadas atrás da pessoa.

AAC é copiado; outros áudios viram AAC. Pausa com seta mantém áudio e duração, congelando só a imagem. HDR precisa ser convertido para SDR. Confira decodificação, duração, início/meio/fim e o áudio antes de entregar. As opções, limites e soluções de problemas estão no guia avançado. Publicação e envio a serviços externos dependem de um pedido separado.
