#!/usr/bin/env python3
"""Prepara um ambiente isolado no clone. #Tecnologia #Saude"""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import venv


def main():
    if sys.version_info < (3, 10):
        raise SystemExit('Use Python 3.10 ou mais recente.')
    missing = [x for x in ('ffmpeg', 'ffprobe') if not shutil.which(x)]
    if missing:
        raise SystemExit('Instale FFmpeg antes: macOS: brew install ffmpeg | Ubuntu: sudo apt install ffmpeg | Windows: winget install Gyan.FFmpeg')
    root = Path(__file__).resolve().parent.parent
    env = root / '.venv'
    python = env / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not python.is_file():
        venv.EnvBuilder(with_pip=True).create(env)
    subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(root / 'requirements.txt')], check=True)
    subprocess.run([str(python), str(root / 'scripts/effects.py'), 'doctor'], check=True)
    print(f'Pronto. Python do projeto: {python}')


if __name__ == '__main__':
    main()
