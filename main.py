#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261125.

Verifies the bundled front-page image (entry.png: a whole PNG, 1024x1024,
at most 1 MiB) and copies it to $MAKEFUN_OUTPUT_DIR (default /output) as
entry.png. Standard library only, no network. Deterministic: the output is
a byte-for-byte copy of the bundled image, so repeated runs agree.
"""

import hashlib
import os
import shutil
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
EXPECT_W, EXPECT_H = 1024, 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def check_png(path):
    """Validate the bundled image: PNG magic, IHDR size, total size, and
    a full chunk walk — every chunk's length, CRC and the terminating
    IEND, so a truncated or corrupt file is refused."""
    try:
        size = os.path.getsize(path)
    except OSError as exc:
        fail(f"cannot stat {path}: {exc}")
    if size > MAX_BYTES:
        fail(f"entry.png is {size} bytes, over the 1 MiB limit")
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < 33 or data[:8] != PNG_MAGIC:
        fail("entry.png is not a PNG file")
    length, ctype = struct.unpack(">I4s", data[8:16])
    if ctype != b"IHDR" or length != 13:
        fail("entry.png has no valid IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECT_W, EXPECT_H):
        fail(f"entry.png is {width}x{height}, expected "
             f"{EXPECT_W}x{EXPECT_H}")
    pos, seen_iend, seen_idat = 8, False, False
    while pos < len(data):
        if pos + 8 > len(data):
            fail("entry.png is truncated inside a chunk header")
        clen, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        end = pos + 8 + clen + 4
        if end > len(data):
            fail(f"entry.png is truncated inside chunk {ctype!r}")
        stored_crc = struct.unpack(">I", data[end - 4:end])[0]
        actual_crc = zlib.crc32(data[pos + 4:end - 4]) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            fail(f"entry.png chunk {ctype!r} has a bad CRC")
        if ctype == b"IDAT":
            seen_idat = True
        if ctype == b"IEND":
            if end != len(data):
                fail("entry.png has trailing bytes after IEND")
            seen_iend = True
            break
        pos = end
    if not seen_iend:
        fail("entry.png has no IEND chunk")
    if not seen_idat:
        fail("entry.png has no image data (IDAT)")
    return size, hashlib.sha256(data).hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    size, digest = check_png(SOURCE)
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)
    # Determinism self-check: the written file must be byte-identical to
    # the bundled image and still pass the full validation.
    with open(dest, "rb") as fh:
        written = fh.read()
    if hashlib.sha256(written).hexdigest() != digest:
        fail("written entry.png differs from the bundled image")
    check_png(dest)
    print(f"wrote {dest}: {EXPECT_W}x{EXPECT_H}, {size} bytes, "
          f"sha256 {digest[:16]}...")


if __name__ == "__main__":
    main()
