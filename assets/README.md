# Imagens de demonstração

#JoaoVictor #Tecnologia

O frame em `example-frame.jpg` (instante 0,10 s do vídeo autorizado, boca fechada e olhos abertos) e suas versões com efeitos mostram João Victor, que autorizou seu uso como exemplo neste repositório. Galeria, thumbnails e GIF foram produzidos com `scripts/build_gallery.py`; o GIF anima um único frame e não representa tracking em vídeo em movimento.

A licença MIT do código não concede direitos de imagem sobre o retrato. Use seu próprio material para gerar novos exemplos. Não reutilize o rosto em anúncios ou como endosso.

A fonte não é distribuída: o renderizador procura uma fonte do sistema e recorre à fonte padrão do Pillow. Você pode fornecer uma fonte local com `--font`.

## Direção editorial das thumbnails

As prévias atuais usam `editorial-frame.jpg`, derivado do mesmo frame autorizado com reenquadramento próximo, contraste discreto e fundo suavizado. A boca permanece fechada; nenhum novo rosto foi gerado.

Os textos curtos, as cores de destaque e as imagens dos cartões são presets reais do renderizador. `scripts/gallery_art.py` cria seis capas ilustrativas em `demo-cards/`; elas não são publicações ou resultados clínicos reais. São artes gráficas próprias, sem retratos, licenciadas junto ao código. A galeria adiciona apenas o número e o nome de cada efeito ao rodapé das imagens.

As opções estão em `examples/gallery-presets.json` (coleção de presets, não um plano sequencial). Selecione um item e use seu texto, `accent` e pasta de imagens em uma renderização. Para refazer as imagens, execute `scripts/build_gallery.py`.
