from __future__ import annotations

import html
import math
import re
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests


SEED = 20260723
BASE_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = REPO_DIR / "outputs" / "lesson_04"
SOURCE_FILE = DATA_DIR / "source_urls.csv"

STOPWORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "did",
    "do",
    "does",
    "doing",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "just",
    "me",
    "more",
    "most",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "now",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "she",
    "should",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "will",
    "with",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
}


def fetch_html(url: str) -> str:
    response = requests.get(url, timeout=30, headers={"User-Agent": "text-economics-methods/0.4"})
    response.raise_for_status()
    declared_encoding = response.encoding or ""
    apparent_encoding = response.apparent_encoding or ""
    if declared_encoding.lower() == "iso-8859-1" and apparent_encoding.lower().startswith("utf"):
        encoding = apparent_encoding
    else:
        encoding = declared_encoding or apparent_encoding or "utf-8"
    return response.content.decode(encoding, errors="replace")


def normalize_space(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = value.replace("\u2019", "'").replace("\u2018", "'")
    value = value.replace("\u201c", '"').replace("\u201d", '"')
    value = value.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def strip_html(value: str) -> str:
    value = re.sub(r"(?is)<script.*?</script>", " ", value)
    value = re.sub(r"(?is)<style.*?</style>", " ", value)
    value = re.sub(r"(?is)<[^>]+>", " ", value)
    return normalize_space(html.unescape(value))


def extract_article_html(raw_html: str) -> str:
    start = raw_html.find('<div id="article"')
    if start < 0:
        raise ValueError("Cannot find Federal Reserve article container.")
    end_candidates = [
        raw_html.find('<div class="lastUpdate"', start),
        raw_html.find("</main>", start),
        raw_html.find('<div id="related-info"', start),
    ]
    end_candidates = [value for value in end_candidates if value > start]
    end = min(end_candidates) if end_candidates else len(raw_html)
    return raw_html[start:end]


def clean_statement(raw_html: str) -> str:
    text = strip_html(extract_article_html(raw_html))
    for marker in ["Recent indicators", "Information received"]:
        if marker in text:
            text = text[text.find(marker) :]
            break
    for marker in ["For media inquiries", "Implementation Note issued"]:
        if marker in text:
            text = text[: text.find(marker)]
    return normalize_space(text)


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?", text.lower())


def content_tokens(tokens: list[str]) -> list[str]:
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1 and not token.isdigit()]


def load_corpus() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    sources = pd.read_csv(SOURCE_FILE)
    for record in sources.to_dict("records"):
        raw_html = fetch_html(record["url"])
        clean_text = clean_statement(raw_html)
        tokens = tokenize(clean_text)
        filtered = content_tokens(tokens)
        rows.append(
            {
                "date": record["date"],
                "url": record["url"],
                "manual_label": record["manual_label"],
                "clean_text": clean_text,
                "total_tokens": len(tokens),
                "content_tokens": len(filtered),
                "tokens": filtered,
            }
        )
    return pd.DataFrame(rows)


def build_vocabulary(corpus: pd.DataFrame, min_total_count: int = 2) -> list[str]:
    total_counter: Counter[str] = Counter()
    for tokens in corpus["tokens"]:
        total_counter.update(tokens)
    return sorted(term for term, count in total_counter.items() if count >= min_total_count)


def build_count_matrix(corpus: pd.DataFrame, vocabulary: list[str]) -> pd.DataFrame:
    rows = []
    for record in corpus.to_dict("records"):
        counter = Counter(record["tokens"])
        row = {"date": record["date"], "manual_label": record["manual_label"], "content_tokens": len(record["tokens"])}
        for term in vocabulary:
            row[term] = counter[term]
        rows.append(row)
    return pd.DataFrame(rows)


def build_idf_table(count_matrix: pd.DataFrame, vocabulary: list[str]) -> pd.DataFrame:
    n_docs = len(count_matrix)
    rows = []
    for term in vocabulary:
        counts = count_matrix[term]
        df = int((counts > 0).sum())
        total_count = int(counts.sum())
        idf = math.log((1 + n_docs) / (1 + df)) + 1
        rows.append({"term": term, "total_count": total_count, "document_frequency": df, "idf": round(idf, 4)})
    return pd.DataFrame(rows).sort_values(["idf", "total_count", "term"], ascending=[False, False, True])


def build_tfidf(
    count_matrix: pd.DataFrame, idf_table: pd.DataFrame, vocabulary: list[str]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    idf = dict(zip(idf_table["term"], idf_table["idf"]))
    raw_rows = []
    norm_rows = []
    for record in count_matrix.to_dict("records"):
        raw_values = []
        raw_row = {"date": record["date"], "manual_label": record["manual_label"]}
        norm_row = {"date": record["date"], "manual_label": record["manual_label"]}
        for term in vocabulary:
            tf = record[term] / record["content_tokens"] if record["content_tokens"] else 0.0
            value = tf * idf[term]
            raw_row[term] = value
            raw_values.append(value)
        norm = math.sqrt(sum(value * value for value in raw_values))
        for term, value in zip(vocabulary, raw_values):
            norm_row[term] = value / norm if norm else 0.0
        raw_rows.append(raw_row)
        norm_rows.append(norm_row)
    raw_tfidf = pd.DataFrame(raw_rows)
    normalized_tfidf = pd.DataFrame(norm_rows)
    return raw_tfidf, normalized_tfidf


def build_top_terms(
    corpus: pd.DataFrame,
    count_matrix: pd.DataFrame,
    idf_table: pd.DataFrame,
    raw_tfidf: pd.DataFrame,
    vocabulary: list[str],
    *,
    only_distinctive: bool = False,
    top_n: int = 6,
) -> pd.DataFrame:
    idf = dict(zip(idf_table["term"], idf_table["idf"]))
    df_values = dict(zip(idf_table["term"], idf_table["document_frequency"]))
    rows = []
    for idx, record in enumerate(corpus.to_dict("records")):
        counter = Counter(record["tokens"])
        scored_terms = []
        for term in vocabulary:
            if counter[term] == 0:
                continue
            if only_distinctive and df_values[term] == len(corpus):
                continue
            tf = counter[term] / len(record["tokens"]) if record["tokens"] else 0.0
            scored_terms.append(
                {
                    "date": record["date"],
                    "manual_label": record["manual_label"],
                    "term": term,
                    "count": counter[term],
                    "tf": round(tf, 4),
                    "document_frequency": df_values[term],
                    "idf": idf[term],
                    "tfidf": round(raw_tfidf.loc[idx, term], 5),
                }
            )
        scored_terms = sorted(scored_terms, key=lambda row: (-row["tfidf"], row["term"]))[:top_n]
        for rank, row in enumerate(scored_terms, start=1):
            row["rank"] = rank
            rows.append(row)
    columns = ["date", "manual_label", "rank", "term", "count", "tf", "document_frequency", "idf", "tfidf"]
    return pd.DataFrame(rows)[columns]


def build_similarity(normalized_tfidf: pd.DataFrame, vocabulary: list[str]) -> pd.DataFrame:
    vectors = normalized_tfidf[vocabulary]
    dates = normalized_tfidf["date"].tolist()
    rows = []
    for i, left_date in enumerate(dates):
        row = {"date": left_date}
        for j, right_date in enumerate(dates):
            row[right_date] = round(float((vectors.iloc[i] * vectors.iloc[j]).sum()), 3)
        rows.append(row)
    return pd.DataFrame(rows)


def build_diagnostics(corpus: pd.DataFrame, count_matrix: pd.DataFrame, vocabulary: list[str]) -> pd.DataFrame:
    nonzero = int((count_matrix[vocabulary] > 0).sum().sum())
    cells = len(corpus) * len(vocabulary)
    density = nonzero / cells if cells else 0.0
    return pd.DataFrame(
        [
            {
                "documents": len(corpus),
                "vocabulary_size": len(vocabulary),
                "matrix_cells": cells,
                "nonzero_cells": nonzero,
                "density": round(density, 3),
                "min_content_tokens": int(corpus["content_tokens"].min()),
                "max_content_tokens": int(corpus["content_tokens"].max()),
            }
        ]
    )


def plot_tfidf_heatmap(top_terms: pd.DataFrame, normalized_tfidf: pd.DataFrame, vocabulary: list[str]) -> None:
    selected_terms = []
    for term in top_terms["term"]:
        if term not in selected_terms:
            selected_terms.append(term)
        if len(selected_terms) == 12:
            break
    heatmap = normalized_tfidf.set_index("date")[selected_terms]
    plt.figure(figsize=(9, 4.8))
    plt.imshow(heatmap.values, aspect="auto", cmap="YlGn")
    plt.colorbar(label="L2-normalized TF-IDF")
    plt.xticks(range(len(selected_terms)), selected_terms, rotation=35, ha="right")
    plt.yticks(range(len(heatmap.index)), heatmap.index)
    plt.title("TF-IDF feature weights in teaching FOMC statements")
    for row_idx in range(heatmap.shape[0]):
        for col_idx in range(heatmap.shape[1]):
            value = heatmap.iloc[row_idx, col_idx]
            plt.text(col_idx, row_idx, f"{value:.2f}", ha="center", va="center", fontsize=7, color="#1d2d24")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "tfidf_heatmap.png", dpi=180)
    plt.close()


def markdown_table(df: pd.DataFrame) -> str:
    headers = [str(column) for column in df.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in df.columns) + " |")
    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    corpus = load_corpus()
    vocabulary = build_vocabulary(corpus)
    count_matrix = build_count_matrix(corpus, vocabulary)
    idf_table = build_idf_table(count_matrix, vocabulary)
    raw_tfidf, normalized_tfidf = build_tfidf(count_matrix, idf_table, vocabulary)
    top_terms = build_top_terms(corpus, count_matrix, idf_table, raw_tfidf, vocabulary)
    distinctive_terms = build_top_terms(
        corpus, count_matrix, idf_table, raw_tfidf, vocabulary, only_distinctive=True, top_n=5
    )
    similarity = build_similarity(normalized_tfidf, vocabulary)
    diagnostics = build_diagnostics(corpus, count_matrix, vocabulary)

    corpus.drop(columns=["tokens"]).to_csv(OUTPUT_DIR / "clean_corpus_for_lesson04.csv", index=False, encoding="utf-8-sig")
    count_matrix.to_csv(OUTPUT_DIR / "count_feature_matrix.csv", index=False, encoding="utf-8-sig")
    idf_table.to_csv(OUTPUT_DIR / "idf_table.csv", index=False, encoding="utf-8-sig")
    raw_tfidf.to_csv(OUTPUT_DIR / "tfidf_raw_matrix.csv", index=False, encoding="utf-8-sig")
    normalized_tfidf.to_csv(OUTPUT_DIR / "tfidf_feature_matrix.csv", index=False, encoding="utf-8-sig")
    top_terms.to_csv(OUTPUT_DIR / "top_tfidf_terms_by_document.csv", index=False, encoding="utf-8-sig")
    distinctive_terms.to_csv(OUTPUT_DIR / "distinctive_tfidf_terms_by_document.csv", index=False, encoding="utf-8-sig")
    similarity.to_csv(OUTPUT_DIR / "cosine_similarity.csv", index=False, encoding="utf-8-sig")
    diagnostics.to_csv(OUTPUT_DIR / "matrix_diagnostics.csv", index=False, encoding="utf-8-sig")
    plot_tfidf_heatmap(distinctive_terms, normalized_tfidf, vocabulary)

    print("Wrote", OUTPUT_DIR / "clean_corpus_for_lesson04.csv")
    print("Wrote", OUTPUT_DIR / "count_feature_matrix.csv")
    print("Wrote", OUTPUT_DIR / "idf_table.csv")
    print("Wrote", OUTPUT_DIR / "tfidf_raw_matrix.csv")
    print("Wrote", OUTPUT_DIR / "tfidf_feature_matrix.csv")
    print("Wrote", OUTPUT_DIR / "top_tfidf_terms_by_document.csv")
    print("Wrote", OUTPUT_DIR / "distinctive_tfidf_terms_by_document.csv")
    print("Wrote", OUTPUT_DIR / "cosine_similarity.csv")
    print("Wrote", OUTPUT_DIR / "matrix_diagnostics.csv")
    print("Wrote", OUTPUT_DIR / "tfidf_heatmap.png")
    print("\nMATRIX DIAGNOSTICS")
    print(markdown_table(diagnostics))
    print("\nHIGHEST IDF TERMS")
    print(markdown_table(idf_table.head(10)))
    print("\nTOP TF-IDF TERMS")
    print(markdown_table(top_terms.groupby("date").head(4)))
    print("\nDISTINCTIVE TF-IDF TERMS")
    print(markdown_table(distinctive_terms.groupby("date").head(4)))
    print("\nCOSINE SIMILARITY")
    print(markdown_table(similarity))


if __name__ == "__main__":
    main()
