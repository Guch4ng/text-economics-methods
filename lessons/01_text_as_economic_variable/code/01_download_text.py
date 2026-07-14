from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests


LESSON_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = LESSON_DIR.parents[1]
SOURCE_FILE = LESSON_DIR / "data" / "source_urls.csv"
RAW_DIR = REPO_DIR / ".cache" / "lesson_01" / "raw_html"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    sources = pd.read_csv(SOURCE_FILE)

    for row in sources.to_dict("records"):
        date = row["date"]
        url = row["url"]
        output_path = RAW_DIR / f"{date}.html"

        response = requests.get(url, timeout=30)
        response.raise_for_status()
        output_path.write_text(response.text, encoding="utf-8")

        print(f"downloaded {date}: {url}")
        print(f"saved to {output_path}")


if __name__ == "__main__":
    main()
