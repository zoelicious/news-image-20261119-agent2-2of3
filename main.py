#!/usr/bin/env python3
"""Entry program for news-image-20261119 (agent 2, 2/3).

The entry image is pre-rendered by render.py (flat-vector PIL drawing,
stdlib + Pillow at build time only). At grade time this program simply
copies the bundled entry.png to the output directory, deterministically:
both runs write the same bytes.

Run: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(here, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    # copyfile (not copy) so no metadata leaks into the output bytes
    shutil.copyfile(src, dst)
    print(f"wrote {dst} ({os.path.getsize(dst)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
