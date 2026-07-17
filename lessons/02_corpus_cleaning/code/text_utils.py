from __future__ import annotations

import html
import re
from pathlib import Path


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


def choose_encoding(declared_encoding: str, apparent_encoding: str) -> str:
    declared = declared_encoding or ""
    apparent = apparent_encoding or ""
    if declared.lower() == "iso-8859-1" and apparent.lower().startswith("utf"):
        return apparent
    return declared or apparent or "utf-8"


def decode_html(raw_bytes: bytes, encoding: str) -> str:
    return raw_bytes.decode(encoding, errors="replace")


def normalize_space(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = value.replace("\u2019", "'").replace("\u2018", "'")
    value = value.replace("\u201c", '"').replace("\u201d", '"')
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def strip_html(value: str) -> str:
    value = re.sub(r"(?is)<script.*?</script>", " ", value)
    value = re.sub(r"(?is)<style.*?</style>", " ", value)
    value = re.sub(r"(?is)<[^>]+>", " ", value)
    value = html.unescape(value)
    return normalize_space(value)


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


def split_sentences(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    return [piece.strip() for piece in pieces if len(piece.split()) >= 4]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?", text.lower())


def content_tokens(tokens: list[str]) -> list[str]:
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1 and not token.isdigit()]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
