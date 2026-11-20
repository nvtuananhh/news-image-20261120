#!/usr/bin/env python3
"""news-image-20261120: render the 20 Nov 2026 front page to /output/entry.png.

Stdlib + Pillow only, no network, deterministic.
"""
import os

from gen_poster import build_poster


def main():
    out = "/output/entry.png"
    os.makedirs("/output", exist_ok=True)
    build_poster(out)


if __name__ == "__main__":
    main()
