from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests

from text_utils import choose_encoding, content_tokens, decode_html, read_text, strip_html, tokenize


LESSON_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = LESSON_DIR.parents[1]
SOURCE_FILE = LESSON_DIR / "data" / "source_urls.csv"
RAW_DIR = REPO_DIR / ".cache" / "lesson_02" / "raw_html"
CLEAN_DIR = REPO_DIR / ".cache" / "lesson_02" / "clean_text"
OUTPUT_DIR = REPO_DIR / "outputs" / "lesson_02"


def top_terms(counter: Counter[str], n: int = 12) -> list[tuple[str, int]]:
    return counter.most_common(n)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = pd.read_csv(SOURCE_FILE)
    raw_counter: Counter[str] = Counter()
    clean_counter: Counter[str] = Counter()
    filtered_counter: Counter[str] = Counter()

    for row in sources.to_dict("records"):
        date = row["date"]
        raw_path = RAW_DIR / f"{date}.html"
        clean_path = CLEAN_DIR / f"{date}.txt"
        if not raw_path.exists():
            raise FileNotFoundError(f"Missing raw HTML: {raw_path}. Run 01_download_html.py first.")
        if not clean_path.exists():
            raise FileNotFoundError(f"Missing clean text: {clean_path}. Run 02_clean_corpus.py first.")

        raw_bytes = raw_path.read_bytes()
        response = requests.models.Response()
        response._content = raw_bytes
        response.encoding = "ISO-8859-1"
        chosen_encoding = choose_encoding(response.encoding or "", response.apparent_encoding or "")
        raw_html = decode_html(raw_bytes, chosen_encoding)
        clean_text = read_text(clean_path)

        raw_counter.update(tokenize(strip_html(raw_html)))
        clean_tokens = tokenize(clean_text)
        clean_counter.update(clean_tokens)
        filtered_counter.update(content_tokens(clean_tokens))

    raw_top = top_terms(raw_counter)
    clean_top = top_terms(clean_counter)
    filtered_top = top_terms(filtered_counter)
    rows = []
    for index in range(max(len(raw_top), len(clean_top), len(filtered_top))):
        raw_term, raw_count = raw_top[index] if index < len(raw_top) else ("", "")
        clean_term, clean_count = clean_top[index] if index < len(clean_top) else ("", "")
        filtered_term, filtered_count = filtered_top[index] if index < len(filtered_top) else ("", "")
        rows.append(
            {
                "rank": index + 1,
                "raw_page_term": raw_term,
                "raw_count": raw_count,
                "clean_term": clean_term,
                "clean_count": clean_count,
                "after_stopwords_term": filtered_term,
                "after_stopwords_count": filtered_count,
            }
        )

    top_terms_df = pd.DataFrame(rows)
    top_terms_df.to_csv(OUTPUT_DIR / "top_terms_comparison.csv", index=False, encoding="utf-8-sig")

    plot_terms = pd.DataFrame(filtered_top[:10], columns=["term", "count"]).sort_values("count")
    figure_path = OUTPUT_DIR / "top_content_tokens.png"
    plt.figure(figsize=(7, 4.5))
    plt.barh(plot_terms["term"], plot_terms["count"], color="#2f6b57")
    plt.xlabel("Count after cleaning and stopword removal")
    plt.title("Top content tokens in cleaned FOMC statements")
    plt.tight_layout()
    plt.savefig(figure_path, dpi=180)
    plt.close()

    print(f"saved term comparison to {OUTPUT_DIR / 'top_terms_comparison.csv'}")
    print(f"saved figure to {figure_path}")


if __name__ == "__main__":
    main()
