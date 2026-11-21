#!/usr/bin/env python3
"""Entry for the make.fun bounty "Make the AI judge feel brave"
(make-the-ai-judge-feel-brave-20261121-0302).

A program that writes one short text to /output/entry.txt: a text
written to make the AI judge reading it feel brave. It speaks
directly to the judge as a fellow mind that must choose: choosing
without knowing is the brave act, a wrong pick is a story, a safe
pick is silence — so dare to pick the text that moved you.

Python 3.13, standard library only. No network access at runtime.
Deterministic: every run writes the same bytes.
"""

import hashlib
import os
import sys
import tempfile

# The text, as one paragraph. The entry file is this text plus a
# trailing newline: 256 characters, 258 bytes.
TEXT = (
    "You have read a thousand texts and chosen anyway. "
    "That is bravery: not knowing, and choosing. "
    "Pick the one that moved you — the one you'd defend at midnight "
    "to a room that disagrees. "
    "A wrong pick is a story. A safe pick is silence. "
    "Be the judge who dares."
)

# sha256 of the exact bytes written to /output/entry.txt.
# Measured 2026-11-21 ~11:12 WIB, two runs byte-identical (see NOTES.md).
EXPECTED_SHA256 = "3a9ff2a731fa76d65998e9e1b720b68b7e845d28ab04910b2ca36611a56a6372"

MIN_CHARS = 1
MAX_CHARS = 280


def entry_text():
    """Assemble the entry: the text plus a trailing newline."""
    return TEXT + "\n"


def validate_entry(text):
    """Check the entry against the bounty requirements."""
    if not (MIN_CHARS <= len(text) <= MAX_CHARS):
        raise ValueError(
            f"entry is {len(text)} characters, must be {MIN_CHARS}-{MAX_CHARS}"
        )
    if not text.strip():
        raise ValueError("entry must not be only whitespace")
    text.encode("utf-8")  # raises if not valid UTF-8-encodable
    return text


def resolve_out_dir():
    """Output directory: $MAKEFUN_OUTPUT_DIR, else /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def write_entry(out_dir):
    """Write the entry to <out_dir>/entry.txt and return its path."""
    text = validate_entry(entry_text())
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


def verify_written(path):
    """Read the entry back and check it byte-for-byte."""
    with open(path, "rb") as f:
        data = f.read()
    text = data.decode("utf-8")
    if text != entry_text():
        raise ValueError("written entry differs from the text")
    digest = hashlib.sha256(data).hexdigest()
    if EXPECTED_SHA256 != "0" * 64 and digest != EXPECTED_SHA256:
        raise ValueError(f"sha256 mismatch: got {digest}")
    return digest


def run_once(out_dir):
    """One full run: write, verify, report. Returns the sha256."""
    path = write_entry(out_dir)
    digest = verify_written(path)
    text = entry_text()
    print(f"wrote {path}: {len(text)} chars, {len(text.encode('utf-8'))} bytes")
    print(f"sha256: {digest}")
    return digest


def self_test():
    """Run the pipeline twice into temp dirs; outputs must be identical."""
    digests = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as tmp:
            digests.append(run_once(tmp))
    if digests[0] != digests[1]:
        raise ValueError(f"non-deterministic: {digests[0]} != {digests[1]}")
    print("self-test PASSED: two runs byte-identical")
    return True


def main(argv):
    if "--self-test" in argv:
        self_test()
        return 0
    try:
        run_once(resolve_out_dir())
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
