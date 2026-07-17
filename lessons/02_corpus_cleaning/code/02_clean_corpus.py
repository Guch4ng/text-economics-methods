from __future__ import annotations

from pathlib import Path

import pandas as pd

from text_utils import (
    choose_encoding,
    clean_statement,
    content_tokens,
    decode_html,
    split_sentences,
    strip_html,
    tokenize,
    write_text,
)


LESSON_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = LESSON_DIR.parents[1]
SOURCE_FILE = LESSON_DIR / "data" / "source_urls.csv"
RAW_DIR = REPO_DIR / ".cache" / "lesson_02" / "raw_html"
METADATA_FILE = REPO_DIR / ".cache" / "lesson_02" / "download_metadata.csv"
CLEAN_DIR = REPO_DIR / ".cache" / "lesson_02" / "clean_text"
OUTPUT_DIR = REPO_DIR / "outputs" / "lesson_02"


def main() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = pd.read_csv(SOURCE_FILE)
    if not METADATA_FILE.exists():
        raise FileNotFoundError(f"Missing download metadata: {METADATA_FILE}. Run 01_download_html.py first.")
    metadata = pd.read_csv(METADATA_FILE).set_index("date")
    diagnostics_rows: list[dict[str, object]] = []
    corpus_rows: list[dict[str, object]] = []
    sentence_rows: list[dict[str, object]] = []

    for row in sources.to_dict("records"):
        date = row["date"]
        raw_path = RAW_DIR / f"{date}.html"
        if not raw_path.exists():
            raise FileNotFoundError(f"Missing raw HTML: {raw_path}. Run 01_download_html.py first.")

        raw_bytes = raw_path.read_bytes()
        meta = metadata.loc[date]
        declared_encoding = str(meta["declared_encoding"] or "")
        apparent_encoding = str(meta["apparent_encoding"] or "")
        chosen_encoding = choose_encoding(declared_encoding, apparent_encoding)

        raw_html = decode_html(raw_bytes, chosen_encoding)
        raw_page_text = strip_html(raw_html)
        clean_text = clean_statement(raw_html)
        clean_path = CLEAN_DIR / f"{date}.txt"
        write_text(clean_path, clean_text)

        raw_tokens = tokenize(raw_page_text)
        clean_tokens = tokenize(clean_text)
        filtered_tokens = content_tokens(clean_tokens)
        sentences = split_sentences(clean_text)
        sentence_lengths = [len(tokenize(sentence)) for sentence in sentences]
        avg_sentence_words = round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0.0

        diagnostics_rows.append(
            {
                "date": date,
                "status_code": int(meta["status_code"]),
                "declared_encoding": declared_encoding,
                "apparent_encoding": apparent_encoding,
                "chosen_encoding": chosen_encoding,
                "html_bytes": int(meta["html_bytes"]),
                "replacement_chars": raw_html.count("\ufffd"),
                "raw_page_words": len(raw_tokens),
                "clean_words": len(clean_tokens),
                "raw_to_clean_ratio": round(len(raw_tokens) / len(clean_tokens), 2) if clean_tokens else 0.0,
                "sentences": len(sentences),
                "avg_sentence_words": avg_sentence_words,
                "content_tokens": len(filtered_tokens),
                "stopword_removed_pct": round(100 * (1 - len(filtered_tokens) / len(clean_tokens)), 1)
                if clean_tokens
                else 0.0,
            }
        )
        corpus_rows.append(
            {
                "date": date,
                "url": row["url"],
                "manual_label": row["manual_label"],
                "clean_text_file": str(clean_path.relative_to(REPO_DIR)),
            }
        )
        for sentence_id, sentence in enumerate(sentences[:2], start=1):
            sentence_rows.append(
                {
                    "date": date,
                    "sentence_id": sentence_id,
                    "n_words": len(tokenize(sentence)),
                    "sentence": sentence,
                }
            )

    pd.DataFrame(diagnostics_rows).to_csv(
        OUTPUT_DIR / "cleaning_diagnostics.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame(corpus_rows).to_csv(OUTPUT_DIR / "clean_corpus_index.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(sentence_rows).to_csv(OUTPUT_DIR / "sentence_samples.csv", index=False, encoding="utf-8-sig")

    print(f"saved diagnostics to {OUTPUT_DIR / 'cleaning_diagnostics.csv'}")
    print(f"saved corpus index to {OUTPUT_DIR / 'clean_corpus_index.csv'}")
    print(f"saved sentence samples to {OUTPUT_DIR / 'sentence_samples.csv'}")


if __name__ == "__main__":
    main()
