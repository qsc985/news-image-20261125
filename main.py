#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261125.

Checks the bundled front-page image (entry.png: a whole PNG, 1024x1024, at
most 1 MiB) and copies it to $MAKEFUN_OUTPUT_DIR (default /output) as
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
BUNDLED = os.path.join(HERE, "entry.png")
LIMIT_BYTES = 1048576
WANT_W, WANT_H = 1024, 1024
MAGIC = b"\x89PNG\r\n\x1a\n"


class BadImage(Exception):
    """Raised when the bundled image fails any whole-file check."""


def read_png(path):
    """Read a PNG file, refusing anything over the size limit or without
    the PNG magic bytes."""
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        raise BadImage(f"cannot read {path}: {exc}")
    if len(data) > LIMIT_BYTES:
        raise BadImage(f"{path} is {len(data)} bytes, over the 1 MiB limit")
    if len(data) < 33 or data[:8] != MAGIC:
        raise BadImage(f"{path} is not a PNG file")
    return data


def check_header(data):
    """The first chunk must be a 13-byte IHDR describing a 1024x1024 image.
    Returns (width, height, bit depth, colour type) for the data check."""
    length, kind = struct.unpack(">I4s", data[8:16])
    if kind != b"IHDR" or length != 13:
        raise BadImage("entry.png has no valid IHDR chunk")
    width, height, depth, colour = struct.unpack(">IIBB", data[16:26])
    if (width, height) != (WANT_W, WANT_H):
        raise BadImage(f"entry.png is {width}x{height}, expected "
                       f"{WANT_W}x{WANT_H}")
    if depth != 8 or colour not in (0, 2, 3, 4, 6):
        raise BadImage(f"entry.png has unsupported depth {depth} / "
                       f"colour type {colour}")
    return width, height, depth, colour


def walk_chunks(data):
    """Walk every chunk, checking lengths and CRCs and the terminating
    IEND, so a truncated or corrupt file is refused. Returns the
    concatenated IDAT payload for the decode check."""
    pos, payload = 8, bytearray()
    while pos < len(data):
        if pos + 8 > len(data):
            raise BadImage("entry.png is truncated inside a chunk header")
        size, kind = struct.unpack(">I4s", data[pos:pos + 8])
        end = pos + 8 + size + 4
        if end > len(data):
            raise BadImage(f"entry.png is truncated inside chunk {kind!r}")
        stored = struct.unpack(">I", data[end - 4:end])[0]
        actual = zlib.crc32(data[pos + 4:end - 4]) & 0xFFFFFFFF
        if stored != actual:
            raise BadImage(f"entry.png chunk {kind!r} has a bad CRC")
        if kind == b"IDAT":
            payload += data[pos + 8:end - 4]
        if kind == b"IEND":
            if end != len(data):
                raise BadImage("entry.png has trailing bytes after IEND")
            break
        pos = end
    else:
        raise BadImage("entry.png has no IEND chunk")
    if not payload:
        raise BadImage("entry.png has no image data (IDAT)")
    return bytes(payload)


def inspect(data):
    """Run every whole-file check on PNG bytes; returns (size, sha256).
    The image data must also inflate to exactly one filter byte plus one
    row of pixels per scanline, so a CRC-valid but corrupt image fails."""
    width, height, _depth, colour = check_header(data)
    payload = walk_chunks(data)
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[colour]
    try:
        raw = zlib.decompress(payload)
    except zlib.error as exc:
        raise BadImage(f"entry.png image data does not inflate: {exc}")
    if len(raw) != height * (1 + width * channels):
        raise BadImage("entry.png image data has the wrong inflated size")
    return len(data), hashlib.sha256(data).hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    size, digest = inspect(read_png(BUNDLED))
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(BUNDLED, dest)
    # Determinism self-check: the written file must be byte-identical to
    # the bundled image and still pass the full validation.
    written_size, written_digest = inspect(read_png(dest))
    if written_digest != digest or written_size != size:
        raise BadImage("written entry.png differs from the bundled image")
    print(f"wrote {dest}: {WANT_W}x{WANT_H}, {size} bytes, "
          f"sha256 {digest[:16]}...")


if __name__ == "__main__":
    try:
        main()
    except BadImage as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
