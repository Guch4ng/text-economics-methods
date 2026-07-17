from __future__ import annotations

from pathlib import Path

import pandas as pd


LESSON_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = LESSON_DIR.parents[1]
OUTPUT_DIR = REPO_DIR / "outputs" / "lesson_02"
DIAGNOSTICS_FILE = OUTPUT_DIR / "cleaning_diagnostics.csv"
TERMS_FILE = OUTPUT_DIR / "top_terms_comparison.csv"
SENTENCE_FILE = OUTPUT_DIR / "sentence_samples.csv"


def to_markdown_table(df: pd.DataFrame) -> str:
    headers = [str(column) for column in df.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        cells = [str(row[column]) for column in df.columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def require_file(path: Path, previous_step: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing output file: {path}. Run {previous_step} first.")


def main() -> None:
    require_file(DIAGNOSTICS_FILE, "02_clean_corpus.py")
    require_file(TERMS_FILE, "03_compare_terms.py")
    require_file(SENTENCE_FILE, "02_clean_corpus.py")

    diagnostics = pd.read_csv(DIAGNOSTICS_FILE)
    terms = pd.read_csv(TERMS_FILE).head(8)
    sentences = pd.read_csv(SENTENCE_FILE).head(4)

    diagnostic_columns = [
        "date",
        "raw_page_words",
        "clean_words",
        "raw_to_clean_ratio",
        "sentences",
        "avg_sentence_words",
        "content_tokens",
        "stopword_removed_pct",
    ]

    print("Cleaning diagnostics:")
    print(to_markdown_table(diagnostics[diagnostic_columns]))
    print()
    print("Top term comparison:")
    print(to_markdown_table(terms))
    print()
    print("Sentence samples:")
    print(to_markdown_table(sentences))
    print()
    print(f"outputs saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
