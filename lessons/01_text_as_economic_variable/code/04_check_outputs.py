from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


LESSON_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = LESSON_DIR.parents[1]
OUTPUT_DIR = REPO_DIR / "outputs" / "lesson_01"
VARIABLE_FILE = OUTPUT_DIR / "fomc_text_variables.csv"


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


def main() -> None:
    if not VARIABLE_FILE.exists():
        raise FileNotFoundError(
            f"Missing variable file: {VARIABLE_FILE}. Run 03_build_variables.py first."
        )

    df = pd.read_csv(VARIABLE_FILE)

    summary = pd.DataFrame(
        [
            {"metric": "documents", "value": len(df)},
            {"metric": "manual_rule_label_matches", "value": int(df["label_match"].sum())},
            {"metric": "mean_words", "value": round(float(df["n_words"].mean()), 1)},
            {
                "metric": "mean_hawkish_share_per_100_words",
                "value": round(float(df["hawkish_share_per_100_words"].mean()), 3),
            },
        ]
    )

    summary_path = OUTPUT_DIR / "summary.csv"
    figure_path = OUTPUT_DIR / "fomc_dictionary_variables.png"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    plt.figure(figsize=(7, 4))
    plt.plot(df["date"], df["hawkish_share_per_100_words"], marker="o", label="Hawkish terms")
    plt.plot(df["date"], df["dovish_share_per_100_words"], marker="s", label="Dovish terms")
    plt.xticks(rotation=25, ha="right")
    plt.ylabel("Terms per 100 words")
    plt.title("FOMC statement dictionary variables")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_path, dpi=180)
    plt.close()

    columns = [
        "date",
        "manual_label",
        "predicted_label",
        "label_match",
        "n_words",
        "hawkish_count",
        "dovish_count",
        "hawkish_share_per_100_words",
        "dovish_share_per_100_words",
    ]

    print("Variable table:")
    print(to_markdown_table(df[columns]))
    print()
    print("Summary:")
    print(to_markdown_table(summary))
    print()
    print(f"saved summary to {summary_path}")
    print(f"saved figure to {figure_path}")


if __name__ == "__main__":
    main()
