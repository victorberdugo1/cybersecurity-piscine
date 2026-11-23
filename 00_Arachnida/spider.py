#!/usr/bin/env python3

import argparse
import os
from urllib.request import urlopen, Request
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser

IMG_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
HEADERS = {'User-Agent': 'Mozilla/5.0 (Spider/1.0)'}


class PageParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.images = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img' and 'src' in attrs:
            self.images.append(urljoin(self.base_url, attrs['src']))
        elif tag == 'a' and 'href' in attrs:
            self.links.append(urljoin(self.base_url, attrs['href']))


def parse_args():
    p = argparse.ArgumentParser(description="Spider: descarga imágenes de una web")
    p.add_argument('url', help='URL objetivo')
    p.add_argument('-r', '--recursive', action='store_true',
                   help='descarga recursivamente')
    p.add_argument('-l', '--level', type=int, default=5,
                   help='profundidad máxima (default 5)')
    p.add_argument('-p', '--path', default='./data/',
                   help='directorio de descarga (default ./data/)')
    return p.parse_args()


def fetch(url):
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=10) as r:
        return r.read(), r.headers.get('Content-Type', '')


def download(img_url, save_dir):
    name = os.path.basename(urlparse(img_url).path)
    if not name:
        return
    dest = os.path.join(save_dir, name)
    if os.path.exists(dest):
        print(f"  [skip] ya existe {dest}")
        return
    try:
        data, _ = fetch(img_url)
        with open(dest, 'wb') as f:
            f.write(data)
        print(f"  [ok] {dest}")
    except Exception as e:
        print(f"  [error] {img_url}: {e}")


def spider(url, save_dir, recursive, max_level, level=0, visited=None):
    if visited is None:
        visited = set()

    url = url.split('#')[0]
    if url in visited:
        return
    visited.add(url)

    print(f"[nivel {level}] {url}")
    try:
        data, ctype = fetch(url)
    except Exception as e:
        print(f"[error] {url}: {e}")
        return

    if 'text/html' not in ctype:
        return

    html = data.decode('utf-8', errors='ignore')
    parser = PageParser(url)
    parser.feed(html)

    for img in parser.images:
        if img.lower().endswith(IMG_EXTS):
            download(img, save_dir)

    if not recursive or level >= max_level:
        return

    host = urlparse(url).netloc
    for link in parser.links:
        if urlparse(link).netloc != host:
            continue
        spider(link, save_dir, recursive, max_level, level + 1, visited)


def main():
    args = parse_args()
    os.makedirs(args.path, exist_ok=True)
    if not args.recursive:
        args.level = 0
    spider(args.url, args.path, args.recursive, args.level)


if __name__ == '__main__':
    main()
