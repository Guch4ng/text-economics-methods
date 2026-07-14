from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


LESSON_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = LESSON_DIR.parents[1]
SOURCE_FILE = LESSON_DIR / "data" / "source_urls.csv"
CLEAN_DIR = REPO_DIR / ".cache" / "lesson_01" / "clean_text"
OUTPUT_DIR = REPO_DIR / "outputs" / "lesson_01"

HAWKISH_TERMS = [
    "inflation",
    "elevated",
    "tightening",
    "increase",
    "increases",
    "higher",
    "restrictive",
    "firming",
]

DOVISH_TERMS = [
    "unemployment",
    "slow",
    "slowed",
    "weaker",
    "decline",
    "declined",
    "cut",
    "cuts",
]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z]+", text.lower())


def term_count(tokens: list[str], terms: list[str]) -> int:
    term_set = set(terms)
    return sum(token in term_set for token in tokens)


def predict_policy_action(text: str) -> str:
    lowered = text.lower()
    if "raise the target range" in lowered:
        return "hike"
    if "lower the target range" in lowered:
        return "cut"
    return "hold"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = pd.read_csv(SOURCE_FILE)
    rows: list[dict[str, object]] = []

    for source in sources.to_dict("records"):
        date = source["date"]
        text_path = CLEAN_DIR / f"{date}.txt"

        if not text_path.exists():
            raise FileNotFoundError(
                f"Missing clean text: {text_path}. Run 02_clean_text.py first."
            )

        text = text_path.read_text(encoding="utf-8")
        tokens = tokenize(text)
        hawkish_count = term_count(tokens, HAWKISH_TERMS)
        dovish_count = term_count(tokens, DOVISH_TERMS)
        predicted_label = predict_policy_action(text)

        rows.append(
            {
                "date": date,
                "url": source["url"],
                "manual_label": source["manual_label"],
                "predicted_label": predicted_label,
                "label_match": source["manual_label"] == predicted_label,
                "n_words": len(tokens),
                "hawkish_count": hawkish_count,
                "dovish_count": dovish_count,
                "hawkish_share_per_100_words": round(100 * hawkish_count / len(tokens), 3),
                "dovish_share_per_100_words": round(100 * dovish_count / len(tokens), 3),
            }
        )

    variables = pd.DataFrame(rows)
    output_path = OUTPUT_DIR / "fomc_text_variables.csv"
    variables.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"saved variables to {output_path}")
    print(variables[["date", "manual_label", "predicted_label", "n_words"]])


if __name__ == "__main__":
    main()
