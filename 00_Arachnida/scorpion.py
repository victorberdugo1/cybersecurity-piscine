#!/usr/bin/env python3
import argparse
import os
import time
from PIL import Image
from PIL.ExifTags import TAGS

IMG_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')


def parse_metadata(filepath):
    """Devuelve dict con metadatos EXIF/chunks, o {} si no hay."""
    metadata = {}
    try:
        with Image.open(filepath) as img:
            if img.format == 'PNG':
                metadata.update(img.info)
            elif img.format == 'JPEG':
                exif = img.getexif()
                if exif:
                    metadata.update({TAGS.get(k, k): v for k, v in exif.items()})
            # GIF y BMP: no tienen EXIF estándar, se muestran solo datos básicos
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
    return metadata


def display(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in IMG_EXTS:
        print(f"Extensión no soportada: {ext}")
        return

    # Info básica: SIEMPRE se muestra
    print(f"FILE: {filepath}")
    print(f"  Size: {os.path.getsize(filepath)} bytes")
    print(f"  Created: {time.ctime(os.path.getctime(filepath))}")
    print(f"  Modified: {time.ctime(os.path.getmtime(filepath))}")

    try:
        with Image.open(filepath) as img:
            print(f"  Format: {img.format}")
            print(f"  Mode: {img.mode}")
            print(f"  Dimensions: {img.width}x{img.height}")
    except Exception as e:
        print(f"  Error abriendo imagen: {e}")
        return

    # Metadatos: solo si existen
    metadata = parse_metadata(filepath)
    if metadata:
        print("  Metadata:")
        for k, v in metadata.items():
            print(f"    {k}: {v}")
    else:
        print("  Metadata: (none)")


def main():
    p = argparse.ArgumentParser(description="Scorpion: metadatos de imágenes")
    p.add_argument("files", nargs="+", help="Ficheros de imagen")
    args = p.parse_args()

    for f in args.files:
        display(f)
        print()  # línea en blanco entre ficheros


if __name__ == "__main__":
    main()
