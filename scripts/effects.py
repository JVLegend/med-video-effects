#!/usr/bin/env python3
"""Seis efeitos locais para vídeos educativos. #Tecnologia #Saude"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

EFFECTS = {
    'focus': 'Foco no rosto: aproximação suave e cantos de enquadramento.',
    'spotlight': 'Luz no apresentador com escurecimento suave ao redor.',
    'grade': 'Cor cinematográfica: contraste suave e sombras frias.',
    'checklist': 'Lista de até três pontos que são marcados em sequência.',
    'split': 'Cartão de título que abre espaço acima do apresentador.',
    'headline': 'Frase em caixa branca com entrada animada.',
}
DEFAULTS = {
    'checklist': 'Observe|Anote suas dúvidas|Converse com seu médico',
    'split': 'Informação clara|para cuidar melhor',
    'headline': 'Saúde com informação',
}
FONT_PATH = None
_FONT_CACHE = {}


def command(args):
    return subprocess.run(args, check=True, capture_output=True).stdout


def ease(x):
    x = max(0., min(1., x))
    return 1 - (1 - x) ** 3


def font(size):
    size = max(10, int(size))
    key = (FONT_PATH, size)
    if key not in _FONT_CACHE:
        candidates = [FONT_PATH] if FONT_PATH else [
            '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            'C:/Windows/Fonts/arialbd.ttf',
        ]
        for path in candidates:
            if path and Path(path).is_file():
                _FONT_CACHE[key] = ImageFont.truetype(path, size)
                break
        else:
            if FONT_PATH:
                raise ValueError(f'Fonte não encontrada: {FONT_PATH}')
            _FONT_CACHE[key] = ImageFont.load_default(size=size)
    return _FONT_CACHE[key]


def fit(lines, width, size):
    while size > 12 and max(font(size).getlength(x) for x in lines) > width:
        size -= 1
    if max(font(size).getlength(x) for x in lines) > width:
        raise ValueError('Texto muito longo. Encurte o texto ou divida com |.')
    return font(size)


def text_center(draw, x, y, text, f, fill):
    # Bounding boxes include font ascenders; keep optical alignment consistent.
    bb = f.getbbox(text)
    draw.text((x - f.getlength(text) / 2, y - (bb[1] + bb[3]) / 2), text, font=f, fill=fill)


def probe(src):
    info = json.loads(command(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(src)]))
    streams = [s for s in info['streams'] if s['codec_type'] == 'video' and not s.get('disposition', {}).get('attached_pic')]
    if not streams:
        raise ValueError('O arquivo não tem vídeo.')
    s = streams[0]
    if s.get('color_transfer') in ('smpte2084', 'arib-std-b67'):
        raise ValueError('Vídeo HDR: converta para SDR antes de usar esta versão.')
    # FFmpeg applies display rotation. Read dimensions from an actual decoded frame.
    png = command(['ffmpeg', '-v', 'error', '-i', str(src), '-map', '0:V:0', '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    frame = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError('Não foi possível decodificar o primeiro quadro.')
    duration = float(s.get('duration') or info['format'].get('duration', 0))
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('Duração inválida ou indisponível.')
    audios = [s for s in info['streams'] if s['codec_type'] == 'audio']
    return frame.shape[1], frame.shape[0], duration, audios[0]['codec_name'] if audios else None


class FaceTracker:
    """OpenCV's bundled Haar detector; no model downloads or network calls."""
    def __init__(self):
        self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if self.detector.empty():
            raise RuntimeError('Detector de rosto não encontrado no OpenCV.')
        self.previous = None
        self.misses = 0
        self.detected = 0

    def update(self, frame):
        h, w = frame.shape[:2]
        scale = min(1., 480 / w)
        small = cv2.resize(frame, (max(1, int(w * scale)), max(1, int(h * scale))))
        gray = cv2.cvtColor(small, cv2.COLOR_RGB2GRAY)
        found = self.detector.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=5, minSize=(35, 35))
        if len(found):
            x, y, fw, fh = max(found, key=lambda r: r[2] * r[3]) / scale
            new = np.array([x + fw / 2, y + fh / 2, fw, fh], dtype=float)
            self.previous = new if self.previous is None else .28 * new + .72 * self.previous
            self.misses = 0
            self.detected += 1
        else:
            self.misses += 1
        # Stop anchoring to a stale detection after one second of missed frames.
        if self.previous is None or self.misses > 30:
            return None
        return self.previous.copy()


def zoom(frame, face, amount):
    h, w = frame.shape[:2]
    cx, cy = (face[0], face[1]) if face is not None else (w / 2, h * .45)
    cw, ch = w / amount, h / amount
    left = max(0, min(w - cw, cx - cw / 2))
    top = max(0, min(h - ch, cy - ch * .43))
    matrix = np.float32([[amount, 0, -left * amount], [0, amount, -top * amount]])
    out = cv2.warpAffine(frame, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    new = None if face is None else np.array([(face[0] - left) * amount, (face[1] - top) * amount, face[2] * amount, face[3] * amount])
    return out, new


def panel_layout(face, w, h, desired):
    # Stay above the forehead; reject layouts that cannot hold readable text.
    limit = face[1] - face[3] * .66 - h * .035 if face is not None else h * .32
    y = int(h * .055)
    height = int(min(desired, limit - y))
    return y, height


def render_effect(frame, face, e, t):
    h, w = frame.shape[:2]
    local, duration = t - e['start'], e['end'] - e['start']
    fade = min(ease(local / .26), max(0., min(1., (e['end'] - t) / .24)))
    kind = e['effect']
    if kind == 'grade':
        src = frame.astype(np.float32) / 255
        luminance = src @ np.array([.299, .587, .114], dtype=np.float32)
        out = (src - luminance[..., None]) * .85 + luminance[..., None]
        out = (out - .5) * 1.08 + .5
        out += (1 - luminance[..., None]) * np.array([-.025, .012, .035], dtype=np.float32)
        return np.uint8(np.clip((src * (1 - fade) + out * fade) * 255, 0, 255)), face
    if kind == 'spotlight':
        # Face is a geometric light source, not semantic person segmentation.
        if face is None:
            return frame, face
        cx, cy, fw, fh = face
        yy, xx = np.ogrid[:h, :w]
        ellipse = ((xx - cx) / (fw * 1.4)) ** 2 + ((yy - (cy + fh * .55)) / (fh * 1.8)) ** 2
        light = np.clip((1.5 - ellipse) / .75, 0, 1)
        light = .18 + .82 * light
        gain = 1 - fade + fade * light
        return np.uint8(np.clip(frame * gain[..., None], 0, 255)), face
    if kind == 'focus':
        if face is None:
            return frame, face
        frame, face = zoom(frame, face, 1 + .09 * fade)
        cx, cy, fw, fh = face
        pad = fw * .18
        x0, y0, x1, y1 = cx - fw / 2 - pad, cy - fh / 2 - pad, cx + fw / 2 + pad, cy + fh / 2 + pad
        layer = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(layer)
        length, stroke = fw * .19, max(2, int(w / 180))
        for x, y, sx, sy in [(x0,y0,1,1),(x1,y0,-1,1),(x0,y1,1,-1),(x1,y1,-1,-1)]:
            d.line([(x, y + sy * length),(x, y),(x + sx * length, y)], fill=(80, 230, 191, int(255 * fade)), width=stroke)
        return np.array(Image.alpha_composite(Image.fromarray(frame).convert('RGBA'), layer).convert('RGB')), face

    lines = e['text'].split('|')
    image = Image.fromarray(frame).convert('RGBA')
    layer = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(layer)
    if kind == 'split':
        # Create genuine headroom by resizing the whole shot into the lower panel.
        header = int(h * .30 * fade)
        if header < 2:
            return frame, face
        lower = Image.fromarray(frame).resize((max(2, int(w * (h - header) / h)), h - header), Image.Resampling.LANCZOS)
        backdrop = Image.fromarray(frame).filter(ImageFilter.GaussianBlur(w * .025))
        image = backdrop.convert('RGBA')
        image.paste(lower, ((w - lower.width) // 2, header))
        d.rectangle((0, 0, w, header), fill=(246, 245, 240, 255))
        size = min(int(w * .095), int(header * .62 / len(lines)))
        f = fit(lines, w * .86, max(12, size))
        step = f.size * 1.22
        for j, line in enumerate(lines):
            text_center(d, w / 2, header / 2 + (j - (len(lines) - 1) / 2) * step, line, f, (18, 24, 30, 255))
        d.rectangle((0, max(0, header - max(3, w // 180)), w, header), fill=(0, 166, 133, 255))
        if face is not None:
            ratio = (h - header) / h
            face = np.array([face[0] * ratio + (w - w * ratio) / 2, face[1] * ratio + header, face[2] * ratio, face[3] * ratio])
    elif kind == 'headline':
        y, available = panel_layout(face, w, h, h * .22)
        if available < w * .06:
            return frame, face
        size = min(int(w * .068), int(available / (1.5 * len(lines))))
        f = fit(lines, w * .80, max(12, size))
        ph = int(f.size * (1.4 * len(lines)) + w * .035)
        if ph > available:
            return frame, face
        widths = [f.getlength(s) for s in lines]
        pw = int(max(widths) + w * .08)
        left = (w - pw) // 2
        slide = int((1 - ease(local / .3)) * w * .035)
        d.rounded_rectangle((left, y + slide, left + pw, y + slide + ph), radius=w * .012, fill=(255,255,255,255))
        for j, line in enumerate(lines):
            text_center(d, w / 2, y + slide + ph / 2 + (j - (len(lines) - 1) / 2) * f.size * 1.4, line, f, (18,24,30,255))
    elif kind == 'checklist':
        y, available = panel_layout(face, w, h, h * .29)
        if available < w * .14:
            return frame, face
        f = fit(lines, w * .66, min(int(w * .049), int(available / (len(lines) * 1.9))))
        step = f.size * 1.9
        ph = min(available, int(step * len(lines) + w * .045))
        x0, x1 = int(w * .07), int(w * .93)
        d.rounded_rectangle((x0, y, x1, y + ph), radius=w * .025, fill=(14,29,34,240), outline=(94,120,125,180), width=2)
        for j, line in enumerate(lines):
            cy = y + ph / 2 + (j - (len(lines) - 1) / 2) * step
            box = f.size * .7; bx = x0 + w * .035
            checked = local >= .45 + j * max(.45, (duration - .9) / len(lines))
            d.rounded_rectangle((bx, cy-box/2,bx+box,cy+box/2),radius=box*.2,fill=(0,166,133,255) if checked else (27,46,51,255),outline=(75,214,178,255),width=max(1,int(w*.002)))
            if checked:
                d.line([(bx+box*.2,cy),(bx+box*.43,cy+box*.22),(bx+box*.82,cy-box*.25)], fill=(255,255,255,255), width=max(2,int(w*.004)))
            d.text((bx+box+w*.03,cy),line,font=f,fill=(245,250,250,255),anchor='lm')
    if kind != 'split':
        layer.putalpha(layer.getchannel('A').point(lambda x: int(x * fade)))
    return np.array(Image.alpha_composite(image, layer).convert('RGB')), face


def validate_plan(items, duration):
    if not isinstance(items, list) or not items:
        raise ValueError('O plano precisa de uma lista não vazia em effects.')
    clean = []
    for raw in items:
        if not isinstance(raw, dict) or raw.get('effect') not in EFFECTS:
            raise ValueError(f'Efeito inválido. Escolha: {", ".join(EFFECTS)}')
        start = float(raw.get('start', 0)); end = min(float(raw.get('end', duration)), duration)
        if not math.isfinite(start) or not math.isfinite(end) or start < 0 or end <= start:
            raise ValueError(f'Intervalo inválido: {start}–{end}.')
        text = str(raw.get('text', DEFAULTS.get(raw['effect'], '')))
        if raw['effect'] in DEFAULTS:
            lines = text.split('|')
            limit = 3 if raw['effect'] in ('split', 'checklist') else 2
            if len(lines) > limit or any(not line.strip() for line in lines) or len(text) > 180:
                raise ValueError(f'Texto inválido para {raw["effect"]}: até {limit} linhas/itens e 180 caracteres.')
        item = dict(effect=raw['effect'], start=start, end=end, text=text)
        # Spatial effects have different coordinate systems. Prevent accidental stacks.
        for other in clean:
            if start < other['end'] and end > other['start']:
                raise ValueError('Efeitos sobrepostos não são suportados; use intervalos separados.')
        clean.append(item)
    return clean


def run_video(args):
    global FONT_PATH
    FONT_PATH = args.font
    src, dst = Path(args.input).expanduser().resolve(), Path(args.output).expanduser().resolve()
    if not src.is_file():
        raise ValueError(f'Vídeo não encontrado: {src}')
    if dst.exists() or src == dst:
        raise ValueError('A saída já existe. Escolha um novo nome; o original é preservado.')
    if not dst.parent.is_dir():
        raise ValueError('A pasta de saída não existe; crie-a antes de renderizar.')
    if args.mode == 'render' and dst.suffix.lower() != '.mp4':
        raise ValueError('Use extensão .mp4 para o vídeo de saída.')
    if args.mode == 'preview' and dst.suffix.lower() != '.png':
        raise ValueError('Use extensão .png para a prévia.')
    sw, sh, duration, audio = probe(src)
    if args.plan:
        data = json.loads(Path(args.plan).read_text(encoding='utf-8'))
        items = data.get('effects') if isinstance(data, dict) else data
    else:
        items = [dict(effect=args.effect, start=args.start, end=args.end if args.end is not None else duration)]
        if args.text is not None:
            items[0]['text'] = args.text
    plan = validate_plan(items, duration)
    if args.mode == 'preview' and not 0 <= args.at < duration:
        raise ValueError('--at precisa estar dentro da duração do vídeo.')
    width = args.width
    height = max(2, int(round(width * sh / sw / 2)) * 2)
    if max(width, height) > 7680:
        raise ValueError('Resolução de saída muito grande; reduza --width.')
    tracker = FaceTracker()
    vf = f'fps=30,scale={width}:{height}:flags=bicubic,format=rgb24'
    decoder = subprocess.Popen(['ffmpeg','-v','error','-i',str(src),'-map','0:V:0','-vf',vf,'-f','rawvideo','-'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fd, temporary = tempfile.mkstemp(prefix='.medfx-', suffix=dst.suffix, dir=dst.parent)
    os.close(fd)
    encoder = None
    frames = 0
    try:
        if args.mode == 'render':
            cmd = ['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r','30','-i','-','-i',str(src),'-map','0:v','-map','1:a:0?','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p']
            cmd += ['-c:a','copy'] if audio == 'aac' else ['-c:a','aac','-b:a','160k']
            cmd += ['-map_metadata','-1','-shortest','-movflags','+faststart',temporary]
            encoder = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        target = int(args.at * 30) if args.mode == 'preview' else None
        while True:
            data = decoder.stdout.read(width * height * 3)
            if not data:
                break
            if len(data) != width * height * 3:
                raise RuntimeError('Quadro incompleto na decodificação.')
            frame = np.frombuffer(data, np.uint8).reshape(height, width, 3).copy()
            t = frames / 30
            active = [e for e in plan if e['start'] <= t < e['end']]
            face = tracker.update(frame) if active else None
            if args.mode == 'preview' and frames != target:
                frames += 1
                continue
            for e in active:
                frame, face = render_effect(frame, face, e, t)
            if args.mode == 'preview':
                Image.fromarray(frame).save(temporary, format='PNG')
                break
            encoder.stdin.write(frame.tobytes())
            if frames % 150 == 0:
                print(f'{t:.1f}s / {duration:.1f}s', flush=True)
            frames += 1
        if args.mode == 'preview':
            decoder.terminate()
        decoder.stdout.close()
        decerr = decoder.stderr.read().decode(errors='replace')
        code = decoder.wait()
        if args.mode != 'preview' and code:
            raise RuntimeError(f'FFmpeg não decodificou o arquivo: {decerr[-1200:]}')
        if encoder:
            encoder.stdin.close()
            error = encoder.stderr.read().decode(errors='replace')
            if encoder.wait():
                raise RuntimeError(f'FFmpeg não exportou o vídeo: {error[-1200:]}')
        if not Path(temporary).stat().st_size:
            raise RuntimeError('Nenhum quadro foi exportado.')
        if dst.exists():
            raise ValueError('A saída passou a existir durante o trabalho. Escolha outro nome.')
        os.replace(temporary, dst)
        print(f'Salvo: {dst}')
        if tracker.detected == 0:
            print('Aviso: nenhum rosto detectado; foco/luz foram omitidos e títulos usam posição superior padrão.', file=sys.stderr)
    finally:
        for proc in (decoder, encoder):
            if proc and proc.poll() is None:
                proc.kill(); proc.wait()
        Path(temporary).unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='mode', required=True)
    sub.add_parser('list', help='Lista os seis efeitos')
    sub.add_parser('doctor', help='Confere dependências locais')
    for mode in ('render', 'preview'):
        s = sub.add_parser(mode)
        s.add_argument('input'); s.add_argument('output')
        choice = s.add_mutually_exclusive_group(required=True)
        choice.add_argument('--effect', choices=EFFECTS); choice.add_argument('--plan')
        s.add_argument('--start', type=float, default=0); s.add_argument('--end', type=float)
        s.add_argument('--text'); s.add_argument('--width', type=int, default=1080)
        s.add_argument('--font', help='Caminho de uma fonte TTF/OTF local')
        if mode == 'preview':
            s.add_argument('--at', type=float, required=True)
    args = p.parse_args()
    if args.mode == 'list':
        for k, desc in EFFECTS.items():
            print(f'{k:12} {desc}')
        return 0
    missing = [x for x in ('ffmpeg','ffprobe') if not shutil.which(x)]
    if missing:
        p.error('Instale primeiro: ' + ', '.join(missing))
    if args.mode == 'doctor':
        FaceTracker()
        print(f'OK · Python {sys.version.split()[0]} · OpenCV {cv2.__version__} · FFmpeg/ffprobe disponíveis')
        return 0
    if not 240 <= args.width <= 3840 or args.width % 2:
        p.error('--width precisa ser par, entre 240 e 3840.')
    try:
        run_video(args)
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f'Erro: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
