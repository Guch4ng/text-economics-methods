from __future__ import annotations

import html
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests


SEED = 20260721
BASE_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = REPO_DIR / "outputs" / "lesson_03"
SOURCE_FILE = DATA_DIR / "source_urls.csv"
DICTIONARY_FILE = DATA_DIR / "domain_dictionary.csv"

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
    response = requests.get(url, timeout=30, headers={"User-Agent": "text-economics-methods/0.3"})
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


def build_top_terms(corpus: pd.DataFrame) -> pd.DataFrame:
    total_counter: Counter[str] = Counter()
    doc_frequency: Counter[str] = Counter()
    for tokens in corpus["tokens"]:
        total_counter.update(tokens)
        doc_frequency.update(set(tokens))
    total_content_tokens = sum(len(tokens) for tokens in corpus["tokens"])
    rows = []
    for rank, (term, count) in enumerate(total_counter.most_common(20), start=1):
        rows.append(
            {
                "rank": rank,
                "term": term,
                "count": count,
                "doc_frequency": doc_frequency[term],
                "per_1000_tokens": round(1000 * count / total_content_tokens, 1),
            }
        )
    return pd.DataFrame(rows)


def build_document_term_matrix(corpus: pd.DataFrame, vocabulary: list[str]) -> pd.DataFrame:
    rows = []
    for record in corpus.to_dict("records"):
        counter = Counter(record["tokens"])
        row = {"date": record["date"], "manual_label": record["manual_label"]}
        for term in vocabulary:
            row[term] = counter[term]
        rows.append(row)
    return pd.DataFrame(rows)


def log_odds_keywords(target_tokens: list[str], reference_tokens: list[str], alpha: float = 0.5) -> pd.DataFrame:
    target_counter = Counter(target_tokens)
    reference_counter = Counter(reference_tokens)
    vocab = sorted(set(target_counter) | set(reference_counter))
    target_total = sum(target_counter.values())
    reference_total = sum(reference_counter.values())
    vocab_size = len(vocab)
    rows = []
    for term in vocab:
        a = target_counter[term] + alpha
        b = reference_counter[term] + alpha
        target_rest = target_total - target_counter[term] + alpha * vocab_size
        reference_rest = reference_total - reference_counter[term] + alpha * vocab_size
        log_odds = math.log(a / target_rest) - math.log(b / reference_rest)
        variance = 1 / a + 1 / b
        z_score = log_odds / math.sqrt(variance)
        rows.append(
            {
                "term": term,
                "target_count": target_counter[term],
                "reference_count": reference_counter[term],
                "log_odds": round(log_odds, 3),
                "z_score": round(z_score, 3),
            }
        )
    result = pd.DataFrame(rows)
    return result.sort_values(["z_score", "term"], ascending=[False, True]).reset_index(drop=True)


def build_keyword_table(corpus: pd.DataFrame) -> pd.DataFrame:
    keyword_blocks = []
    labels = sorted(corpus["manual_label"].unique())
    for label in labels:
        target_tokens = [token for tokens in corpus.loc[corpus["manual_label"] == label, "tokens"] for token in tokens]
        reference_tokens = [
            token for tokens in corpus.loc[corpus["manual_label"] != label, "tokens"] for token in tokens
        ]
        keywords = log_odds_keywords(target_tokens, reference_tokens).head(8).copy()
        keywords.insert(0, "target_label", label)
        keywords.insert(1, "rank", range(1, len(keywords) + 1))
        keyword_blocks.append(keywords)
    return pd.concat(keyword_blocks, ignore_index=True)


def build_dictionary_scores(corpus: pd.DataFrame, dictionary: pd.DataFrame) -> pd.DataFrame:
    term_to_categories: dict[str, list[str]] = defaultdict(list)
    for record in dictionary.to_dict("records"):
        term_to_categories[record["term"]].append(record["category"])
    categories = sorted(dictionary["category"].unique())
    rows = []
    for record in corpus.to_dict("records"):
        counter = Counter(record["tokens"])
        row: dict[str, object] = {
            "date": record["date"],
            "manual_label": record["manual_label"],
            "content_tokens": len(record["tokens"]),
        }
        category_counts = {category: 0 for category in categories}
        for term, count in counter.items():
            for category in term_to_categories.get(term, []):
                category_counts[category] += count
        for category in categories:
            count = category_counts[category]
            row[f"{category}_count"] = count
            row[f"{category}_per_1000"] = round(1000 * count / len(record["tokens"]), 1) if record["tokens"] else 0.0
        rows.append(row)
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame) -> str:
    headers = [str(column) for column in df.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in df.columns) + " |")
    return "\n".join(lines)


def plot_dictionary_scores(scores: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 4.6))
    x_labels = scores["date"].tolist()
    for category, color in [
        ("inflation", "#e57e25"),
        ("labor", "#2f6b57"),
        ("tightening", "#6b4f8a"),
        ("easing", "#4d79a8"),
        ("uncertainty", "#8a5a3b"),
    ]:
        plt.plot(x_labels, scores[f"{category}_per_1000"], marker="o", linewidth=2, label=category, color=color)
    plt.ylabel("Dictionary hits per 1,000 content tokens")
    plt.xlabel("FOMC statement date")
    plt.title("Teaching dictionary scores in cleaned FOMC statements")
    plt.xticks(rotation=20)
    plt.legend(ncol=3, fontsize=8)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "dictionary_scores.png", dpi=180)
    plt.close()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    corpus = load_corpus()
    dictionary = pd.read_csv(DICTIONARY_FILE)

    top_terms = build_top_terms(corpus)
    vocabulary = top_terms["term"].head(15).tolist()
    doc_term_matrix = build_document_term_matrix(corpus, vocabulary)
    keywords = build_keyword_table(corpus)
    dictionary_scores = build_dictionary_scores(corpus, dictionary)

    serializable_corpus = corpus.drop(columns=["tokens"])
    serializable_corpus.to_csv(OUTPUT_DIR / "clean_corpus_for_lesson03.csv", index=False, encoding="utf-8-sig")
    top_terms.to_csv(OUTPUT_DIR / "top_terms.csv", index=False, encoding="utf-8-sig")
    doc_term_matrix.to_csv(OUTPUT_DIR / "document_term_matrix.csv", index=False, encoding="utf-8-sig")
    keywords.to_csv(OUTPUT_DIR / "keywords_by_policy_label.csv", index=False, encoding="utf-8-sig")
    dictionary_scores.to_csv(OUTPUT_DIR / "dictionary_scores.csv", index=False, encoding="utf-8-sig")
    plot_dictionary_scores(dictionary_scores)

    print("Wrote", OUTPUT_DIR / "clean_corpus_for_lesson03.csv")
    print("Wrote", OUTPUT_DIR / "top_terms.csv")
    print("Wrote", OUTPUT_DIR / "document_term_matrix.csv")
    print("Wrote", OUTPUT_DIR / "keywords_by_policy_label.csv")
    print("Wrote", OUTPUT_DIR / "dictionary_scores.csv")
    print("Wrote", OUTPUT_DIR / "dictionary_scores.png")
    print("\nTOP TERMS")
    print(markdown_table(top_terms.head(10)))
    print("\nKEYWORDS")
    print(markdown_table(keywords.groupby("target_label").head(5)))
    print("\nDICTIONARY SCORES")
    compact_scores = dictionary_scores[
        [
            "date",
            "manual_label",
            "content_tokens",
            "inflation_per_1000",
            "labor_per_1000",
            "tightening_per_1000",
            "easing_per_1000",
            "uncertainty_per_1000",
        ]
    ]
    print(markdown_table(compact_scores))


if __name__ == "__main__":
    main()
