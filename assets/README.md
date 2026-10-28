# Imagens de demonstração

#Tecnologia #Saude

A imagem-base atual foi indicada pelo usuário: [fotografia hospedada no Pinterest](https://i.pinimg.com/736x/1d/2d/b2/1d2db27d7fbd575445f8f6b81f3d64ba.jpg). O arquivo recebido está em `baseline-source.jpg`; autoria e licença da fotografia não foram informadas. Sua disponibilidade nesse endereço não equivale a uma licença de reutilização.

`example-frame.jpg` adapta a fotografia inteira para 720 × 1280, com uma extensão do fundo no topo para acomodar os títulos, sem cortar as mãos ou o rosto. `editorial-frame.jpg` deriva dessa composição com contraste discreto e fundo suavizado, mantendo o enquadramento completo. Nenhum novo rosto foi gerado. A fotografia anterior de João Victor foi substituída nos exemplos atuais.

Galerias, 51 miniaturas e GIF foram produzidos com `scripts/build_gallery.py`. O GIF anima uma fotografia estática e não representa rastreamento em vídeo em movimento. As imagens são exemplos gráficos; não indicam vínculo, profissão, depoimento ou endosso da pessoa retratada.

A licença MIT do código não concede direitos sobre a fotografia, a imagem pessoal ou marcas de terceiros. Para seus próprios vídeos e publicações, use material com autorização apropriada.

A fonte não é distribuída: o renderizador procura uma fonte do sistema e recorre à fonte padrão do Pillow. Você pode fornecer uma fonte local com `--font`.

## Direção editorial das thumbnails

Os textos curtos, as cores de destaque e as imagens dos cartões são presets reais do renderizador. `scripts/gallery_art.py` cria seis capas ilustrativas em `demo-cards/`; elas não são publicações ou resultados clínicos reais. São artes gráficas próprias, sem retratos, licenciadas junto ao código. A galeria adiciona apenas o número e o nome de cada efeito ao rodapé das imagens.

As opções estão em `examples/gallery-presets.json` (coleção de presets, não um plano sequencial). Selecione um item e use seu texto, `accent` e pasta de imagens em uma renderização. Para refazer as imagens, execute `scripts/build_gallery.py`.
