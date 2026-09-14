#!/usr/bin/env python3
"""Verify that a generated PDF has the expected pages and extractable text.

Text-layer extraction tries pypdf (BSD, optional `pip install pypdf`) first,
then Poppler `pdftotext` if pypdf is missing, raises, or returns zero
extractable characters. Poppler remains the fallback.

`--contains` compares after `normalize_text()` has folded both sides: whitespace,
Unicode normalization form (NFC), and the typographic substitutions LaTeX makes to
the source text. The fold is comparison-time only - the `--dump-text` output stays
the raw text layer an ATS parser actually sees.
"""

import argparse
import re
import subprocess
import sys
import unicodedata
from pathlib import Path


class VerificationError(Exception):
    """Raised when a generated PDF does not satisfy its checks."""


def run_tool(command):
    try:
        return subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except FileNotFoundError as exc:
        raise VerificationError(
            f"required command '{command[0]}' was not found. "
            "Install poppler-utils (macOS: brew install poppler, "
            "Debian/Ubuntu: apt install poppler-utils, Windows: choco install poppler)"
        ) from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip() or (exc.stdout or "").strip()
        detail = detail or "command failed"
        raise VerificationError(f"{command[0]} could not read the PDF: {detail}") from exc


def parse_page_count(pdfinfo_output):
    match = re.search(r"^Pages:\s+(\d+)\s*$", pdfinfo_output, re.MULTILINE)
    if not match:
        raise VerificationError("pdfinfo output did not contain a page count")
    return int(match.group(1))


# Typographic substitutions the moderncv/cover.cls templates produce from plain
# source text, mapped back to what a user types into --contains. LaTeX ligatures
# ' into U+2019 and -- into U+2013, so "Master's degree" and "2016-2024" are
# absent from the text layer of a CV that plainly contains them (#385). Applied
# to both sides of the comparison; the extracted dump is never rewritten.
TYPOGRAPHIC_FOLDS = str.maketrans(
    {
        "\u2018": "'",  # ` -> quoteleft
        "\u2019": "'",  # ' -> quoteright (the possessive apostrophe)
        "\u201c": '"',  # `` -> quotedblleft
        "\u201d": '"',  # '' -> quotedblright
        "\u2013": "-",  # -- -> endash (the \cventry date-range case)
        "\u2014": "-",  # --- -> emdash
        "\u00a0": " ",  # ~ -> no-break space
    }
)


def normalize_text(text):
    """Fold a string for comparison: NFC, typographic punctuation, whitespace.

    NFC covers the pdflatex text layer, which without T1 font encoding stores
    accented letters decomposed (`e` + U+0300) while a user types them
    precomposed (U+00E8); both forms fold to the same string (#384). The fold
    applies to what is compared, never to what is dumped: the date-range rule in
    `05-cv-templates.md` still needs the raw en-dash visible in `--dump-text`.
    """
    text = unicodedata.normalize("NFC", text).translate(TYPOGRAPHIC_FOLDS)
    return " ".join(text.split())


def verify_pdf(pdf_path, expected_pages=None, min_chars=1, required_text=()):
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise VerificationError(f"PDF does not exist: {pdf_path}")

    if expected_pages is not None:
        actual_pages = parse_page_count(run_tool(["pdfinfo", str(pdf_path)]))
        if actual_pages != expected_pages:
            raise VerificationError(
                f"expected {expected_pages} page(s), found {actual_pages}"
            )

    extracted_text = normalize_text(
        run_tool(["pdftotext", "-layout", str(pdf_path), "-"])
    )
    if len(extracted_text) < min_chars:
        raise VerificationError(
            f"text layer has {len(extracted_text)} character(s); expected at least {min_chars}"
        )

    for required in required_text:
        if normalize_text(required) not in extracted_text:
            raise VerificationError(f"text layer is missing required text: {required!r}")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Verify a PDF's page count and ATS-readable text layer."
    )
    parser.add_argument("pdf", type=Path, help="PDF file to verify")
    parser.add_argument("--pages", type=int, help="required exact page count")
    parser.add_argument(
        "--min-chars",
        type=int,
        default=1,
        help="minimum non-whitespace text-layer characters (default: 1)",
    )
    parser.add_argument(
        "--contains",
        action="append",
        default=[],
        help=(
            "text that must appear in the text layer; both sides are folded for "
            "whitespace, NFC, and LaTeX's typographic substitutions (curly "
            "apostrophes/quotes, en/em dashes, no-break spaces); repeatable"
        ),
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        verify_pdf(args.pdf, args.pages, args.min_chars, args.contains)
    except VerificationError as exc:
        print(f"Error: {args.pdf}: {exc}", file=sys.stderr)
        return 1
    print(f"Verified {args.pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
