from __future__ import annotations

import html
import re
from pathlib import Path


LESSON_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = LESSON_DIR.parents[1]
RAW_DIR = REPO_DIR / ".cache" / "lesson_01" / "raw_html"
CLEAN_DIR = REPO_DIR / ".cache" / "lesson_01" / "clean_text"


def strip_html(value: str) -> str:
    value = re.sub(r"(?is)<script.*?</script>", " ", value)
    value = re.sub(r"(?is)<style.*?</style>", " ", value)
    value = re.sub(r"(?is)<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def extract_statement(raw_html: str) -> str:
    start = raw_html.find('<div id="article"')
    if start < 0:
        start = raw_html.find("Recent indicators")

    end = raw_html.find('<div class="lastUpdate"', start)
    if end < 0:
        end = raw_html.find("</main>", start)

    text = strip_html(raw_html[start:end])

    marker = "Recent indicators"
    if marker in text:
        text = text[text.find(marker) :]

    contact = "For media inquiries"
    if contact in text:
        text = text[: text.find(contact)]

    return text.strip()


def main() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    raw_files = sorted(RAW_DIR.glob("*.html"))

    if not raw_files:
        raise FileNotFoundError(
            f"No HTML files found in {RAW_DIR}. Run 01_download_text.py first."
        )

    for raw_file in raw_files:
        raw_html = raw_file.read_text(encoding="utf-8")
        clean_text = extract_statement(raw_html)
        output_path = CLEAN_DIR / f"{raw_file.stem}.txt"
        output_path.write_text(clean_text, encoding="utf-8")

        preview = clean_text[:120].replace("\n", " ")
        print(f"cleaned {raw_file.name}: {len(clean_text.split())} words")
        print(f"preview: {preview}")


if __name__ == "__main__":
    main()
