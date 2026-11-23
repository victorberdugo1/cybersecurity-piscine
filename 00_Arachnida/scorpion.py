#!/usr/bin/env python3
import argparse
import os
from PIL import Image
from PIL.ExifTags import TAGS

IMG_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')


def parse_metadata(filepath):
    """Devuelve un diccionario con los metadatos o None si falla."""
    try:
        with Image.open(filepath) as img:
            metadata = {}
            # PNG: la info está en img.info
            if img.format == 'PNG':
                metadata.update(img.info)
            # JPEG: los metadatos están en EXIF
            elif img.format == 'JPEG':
                exif = img.getexif()
                if exif:
                    metadata.update({TAGS.get(k, k): v for k, v in exif.items()})
            return metadata
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
        return None


def display(filepath):
    metadata = parse_metadata(filepath)
    if metadata is None:
        return
    print(f"FILE: {filepath}")
    for key, value in metadata.items():
        print(f"  {key}: {value}")


def delete(filepath):
    try:
        with Image.open(filepath) as img:
            img.save(filepath, exif=b"")  # borra EXIF
        print(f"Metadatos borrados: {filepath}")
    except Exception as e:
        print(f"Error borrando {filepath}: {e}")


def main():
    p = argparse.ArgumentParser(description="Scorpion: metadatos de imágenes")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("display", help="mostrar metadatos")
    d.add_argument("files", nargs="+")

    x = sub.add_parser("delete", help="borrar metadatos")
    x.add_argument("file")

    args = p.parse_args()

    if args.command == "display":
        for f in args.files:
            ext = os.path.splitext(f)[1].lower()
            if ext not in IMG_EXTS:
                print(f"Extensión no soportada: {ext}")
                continue
            display(f)
    elif args.command == "delete":
        delete(args.file)


if __name__ == "__main__":
    main()