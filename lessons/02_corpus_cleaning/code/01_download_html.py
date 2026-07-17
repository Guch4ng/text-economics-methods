from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests


LESSON_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = LESSON_DIR.parents[1]
SOURCE_FILE = LESSON_DIR / "data" / "source_urls.csv"
RAW_DIR = REPO_DIR / ".cache" / "lesson_02" / "raw_html"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    sources = pd.read_csv(SOURCE_FILE)
    metadata_rows: list[dict[str, object]] = []

    for row in sources.to_dict("records"):
        date = row["date"]
        url = row["url"]
        output_path = RAW_DIR / f"{date}.html"

        response = requests.get(url, timeout=30, headers={"User-Agent": "text-economics-methods/lesson-02"})
        response.raise_for_status()
        output_path.write_bytes(response.content)
        metadata_rows.append(
            {
                "date": date,
                "url": url,
                "status_code": response.status_code,
                "declared_encoding": response.encoding or "",
                "apparent_encoding": response.apparent_encoding or "",
                "html_bytes": len(response.content),
            }
        )

        print(f"downloaded {date}: {url}")
        print(f"saved raw bytes to {output_path}")
        print(f"declared encoding: {response.encoding}; apparent encoding: {response.apparent_encoding}")

    metadata_path = RAW_DIR.parent / "download_metadata.csv"
    pd.DataFrame(metadata_rows).to_csv(metadata_path, index=False, encoding="utf-8-sig")
    print(f"saved download metadata to {metadata_path}")


if __name__ == "__main__":
    main()
