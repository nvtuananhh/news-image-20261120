#!/usr/bin/env python3
"""Entry point for news-image-20261120 (round 2).

Standard library only (os, shutil, sys). The poster is pre-rendered at
build time and committed to this repository as poster.png; this program
simply copies it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

No sibling imports, no third-party imports, no network: it runs clean
under `python3 -P -s`, which is how the grader invokes it.
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "poster.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
