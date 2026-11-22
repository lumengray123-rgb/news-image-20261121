"""Entry program for the news-image-20261121 competition.

Copies the pre-drawn front page (entry.png, in this repository) to the
output directory as entry.png. Standard library only, no network, fully
deterministic: the same bytes are written on every run.
"""
import os
import sys

SOURCE_NAME = "entry.png"
OUTPUT_NAME = "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    with open(source, "rb") as handle:
        data = handle.read()
    if not data.startswith(PNG_MAGIC):
        print(f"error: {source} is not a PNG file", file=sys.stderr)
        return 1
    if len(data) > MAX_BYTES:
        print(f"error: {source} is {len(data)} bytes, over the 1 MiB limit",
              file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    destination = os.path.join(out_dir, OUTPUT_NAME)
    with open(destination, "wb") as handle:
        handle.write(data)
    print(f"wrote {destination} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
