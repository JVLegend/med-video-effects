<div align="center">

![Med Video Effects — Sua explicação merece um vídeo mais claro](assets/hero.png)

**Seis efeitos para transformar uma gravação em uma explicação visual.**

Feito para experimentar vídeos educativos de médicos com **Claude Code** e **Codex**.

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-local-007808?logo=ffmpeg&logoColor=white)
![License MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-16a085)
![Status experimental](https://img.shields.io/badge/status-experimental-f4b942)

[Ver os efeitos](#os-seis-efeitos) · [Começar](#comece-pelo-assistente) · [Instalar](#instalação) · [Usar no terminal](#uso-direto-no-terminal)

</div>

---

## Uma ideia simples

Você grava. O assistente organiza o pedido. O computador aplica os efeitos.

Use um título para abrir uma explicação, um checklist para organizar pontos ou uma mudança de luz para dirigir a atenção. Escolha o texto, o intervalo e o efeito; confira a prévia e exporte o MP4.

O renderizador roda **localmente**, preserva o arquivo original e não precisa de chave de API. O uso de Claude Code ou Codex segue o plano e as permissões da sua ferramenta. Esta é uma base experimental com seis efeitos, pronta para ser adaptada ao seu estilo.

## Os seis efeitos

![Galeria de seis efeitos aplicados a um frame de João Victor](assets/preview.jpg)

| Efeito | Nome no comando | O que acontece | Onde ajuda |
|---|---|---|---|
| **01 · Foco no rosto** | `focus` | Aproximação suave com cantos que acompanham o rosto | Enfatizar um ponto importante |
| **02 · Spotlight** | `spotlight` | Escurece a região ao redor e mantém luz próxima ao apresentador | Reduzir a distração do ambiente |
| **03 · Cor cinematográfica** | `grade` | Contraste discreto e sombras mais frias | Dar acabamento a um trecho |
| **04 · Checklist** | `checklist` | Até três itens recebem marcações em sequência | Organizar dúvidas, etapas ou tópicos |
| **05 · Tela dividida** | `split` | Um cartão abre espaço no alto; a imagem inteira ocupa a parte inferior | Apresentar a ideia central sem cortar o rosto |
| **06 · Título em caixa** | `headline` | Uma frase entra em uma caixa branca | Criar uma abertura clara |

<details>
<summary><strong>Ver uma demonstração animada dos seis efeitos</strong></summary>

![Demonstração animada a partir de um único frame](assets/demo.gif)

O GIF usa um único frame autorizado. Os vídeos reais usam detecção de rosto quadro a quadro; os limites desse detector estão descritos abaixo.

</details>

## Comece pelo assistente

Depois da instalação, informe o caminho do seu vídeo e descreva o resultado.

**No Claude Code:**

```text
/med-video-effects Use meu vídeo /caminho/meu-video.mp4.
Coloque “Leve suas dúvidas para a consulta” em uma caixa branca
nos primeiros 3 segundos. Gere uma prévia antes de exportar.
```

**No Codex:**

```text
$med-video-effects Use /caminho/meu-video.mp4.
De 4 a 8 segundos, crie um checklist com:
“Observe”, “Anote suas dúvidas” e “Converse com seu médico”.
Salve em /caminho/meu-video-editado.mp4.
```

Também funciona com um pedido em linguagem natural, se a ferramenta reconhecer a skill. Use segundos para o timing: esta versão não transcreve nem encontra palavras no áudio automaticamente.

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

`|` separa linhas ou itens. Headline aceita até duas linhas; split e checklist aceitam até três. Os itens do checklist são marcados automaticamente durante o intervalo; não há sincronização por palavra.

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

O [plano de exemplo](examples/plan.json) percorre os seis efeitos e precisa de pelo menos 18 segundos de vídeo. Intervalos sobrepostos são rejeitados. Deixe trechos limpos entre entradas; não é necessário preencher o vídeo inteiro.

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
- Foco e spotlight são omitidos quando não há rosto detectável. Títulos se adaptam ao espaço acima do rosto; podem ser reduzidos ou omitidos se não couberem. **Inspecione as prévias.**
- Spotlight usa uma máscara geométrica suave. Ainda não há recorte semântico de cabelo/corpo, texto atrás da pessoa ou seleção entre vários apresentadores.
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

Os testes geram vídeos temporários para verificar exportação, preservação de áudio, proteção do original e erros de plano. A galeria é gerada pelo próprio renderizador usando o frame autorizado em `assets/`.

Quer contribuir? Abra uma issue com o efeito desejado, uma descrição do movimento e um exemplo que você possa compartilhar. Melhorias de tracking, enquadramento e instalação são bem-vindas. Se abrir um PR visual, inclua antes/depois e como testou.

## Licença e imagens

O código é distribuído sob a [licença MIT](LICENSE). Dependências mantêm suas próprias licenças. As fotografias e os derivados do retrato em `assets/` são exemplos autorizados para este repositório e estão excluídos da licença do código; veja [as informações das imagens](assets/README.md). Substitua pelo seu próprio material.

Criado por [João Victor · @JVLegend](https://github.com/JVLegend).

<!-- #Saude #Tecnologia #JoaoVictor -->
