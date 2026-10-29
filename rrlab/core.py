"""Validation, offset-preserving chunks, lexical scoring and evidence metrics."""

from collections import Counter
import math
import re
import unicodedata

WORD = re.compile(r"\w+", re.UNICODE)


def tokens(text):
    """Unicode words, NFKC-normalized and case-folded; no stemming."""
    return [unicodedata.normalize("NFKC", m.group()).casefold()
            for m in WORD.finditer(text)]


def _text(value, context):
    if not isinstance(value, str) or not tokens(value):
        raise ValueError(f"{context}: expected nonempty word-bearing string")


def validate_dataset(data):
    """Reject malformed data before any split is evaluated."""
    if not isinstance(data, dict):
        raise ValueError("dataset: expected object")
    documents = data.get("documents")
    questions = data.get("questions")
    for records, name in ((documents, "documents"), (questions, "questions")):
        if not isinstance(records, list) or not records:
            raise ValueError(f"{name}: expected nonempty list")
        ids = set()
        for record in records:
            if not isinstance(record, dict):
                raise ValueError(f"{name}: expected record object")
            identifier = record.get("id")
            if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", identifier):
                raise ValueError(f"{name}: IDs must use ASCII letters, digits, _ or -")
            if identifier in ids:
                raise ValueError(f"{name}: duplicate id {identifier}")
            ids.add(identifier)
            _text(record.get("text"), f"{name}/{identifier}/text")
    by_id = {doc["id"]: doc for doc in documents}
    bodies = set()
    for doc in documents:
        body = tuple(tokens(doc["text"]))
        if body in bodies:
            raise ValueError(f"duplicate normalized document body: {doc['id']}")
        bodies.add(body)
    for question in questions:
        context = question["id"]
        if question.get("split") not in ("dev", "test"):
            raise ValueError(f"{context}: split must be dev or test")
        evidence = question.get("evidence")
        if not isinstance(evidence, list):
            raise ValueError(f"{context}: evidence must be a list (empty means unsupported)")
        seen = set()
        for item in evidence:
            if not isinstance(item, dict):
                raise ValueError(f"{context}: evidence must be an object")
            doc_id, quote = item.get("doc_id"), item.get("quote")
            if not isinstance(doc_id, str) or doc_id not in by_id:
                raise ValueError(f"{context}: evidence references missing document")
            _text(quote, f"{context}/quote")
            text = by_id[doc_id]["text"]
            # Find overlapping matches too: str.count would miss 'aaa' in 'aaaa'.
            starts = [m.start() for m in re.finditer(f"(?={re.escape(quote)})", text)]
            if len(starts) != 1:
                raise ValueError(f"{context}: evidence quote must occur exactly once")
            if (doc_id, quote) in seen:
                raise ValueError(f"{context}: duplicate evidence")
            seen.add((doc_id, quote))


def chunk_documents(documents, size, overlap):
    """Word windows retaining original character offsets and intervening text."""
    if type(size) is not int or type(overlap) is not int or size < 1 or not 0 <= overlap < size:
        raise ValueError("chunk size must be positive; 0 <= overlap < size; integers only")
    chunks = []
    for doc in sorted(documents, key=lambda d: d["id"]):
        matches = list(WORD.finditer(doc["text"]))
        for first in range(0, len(matches), size - overlap):
            last = min(first + size, len(matches))
            start = matches[first].start()
            end = matches[last - 1].end()
            chunks.append({"id": f"{doc['id']}:{start:08d}:{end:08d}",
                           "doc_id": doc["id"], "start": start, "end": end,
                           "text": doc["text"][start:end]})
            if last == len(matches):
                break
    return chunks


def rank(chunks, query, method, k):
    """Return positive-score chunks; ascending chunk ID breaks exact ties.

    TF-IDF: raw TF * (1 + log((N+1)/(df+1))), cosine normalization.
    BM25: k1=1.5, b=.75, log(1+(N-df+.5)/(df+.5)); unique query terms.
    """
    if type(k) is not int or k < 1:
        raise ValueError("k must be a positive integer")
    if method not in ("tfidf", "bm25"):
        raise ValueError("method must be tfidf or bm25")
    if not chunks:
        return []
    counts = [Counter(tokens(c["text"])) for c in chunks]
    df = Counter(term for count in counts for term in count)
    n = len(chunks)
    query_counts = Counter(tokens(query))
    query_terms = sorted(set(query_counts) & set(df))
    if not query_terms:
        return []
    idf = {term: 1 + math.log((n + 1) / (freq + 1)) for term, freq in df.items()}
    # OOV terms are discarded from the query vector (fixed corpus vocabulary).
    qnorm = math.sqrt(sum((query_counts[t] * idf[t]) ** 2 for t in query_terms))
    average_length = sum(sum(c.values()) for c in counts) / n
    hits = []
    for chunk, count in zip(chunks, counts):
        if method == "tfidf":
            norm = math.sqrt(sum((tf * idf[t]) ** 2 for t, tf in sorted(count.items())))
            score = sum(query_counts[t] * idf[t] * count[t] * idf[t]
                        for t in query_terms) / (qnorm * norm) if norm else 0.0
        else:
            length = sum(count.values())
            score = sum(math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5)) *
                        count[t] * 2.5 / (count[t] + 1.5 * (0.25 + 0.75 * length / average_length))
                        for t in query_terms)
        if score > 0:
            hits.append({**chunk, "score": score})
    return sorted(hits, key=lambda hit: (-hit["score"], hit["id"]))[:k]


def evaluate_query(hits, evidence):
    """Evidence recall and first relevant rank; unsupported labels yield null."""
    covered = set()
    first_rank = None
    for position, hit in enumerate(hits, 1):
        found = {i for i, item in enumerate(evidence)
                 if hit["doc_id"] == item["doc_id"] and item["quote"] in hit["text"]}
        if found and first_rank is None:
            first_rank = position
        covered.update(found)
    return {"recall": len(covered) / len(evidence) if evidence else None,
            "rr": (1 / first_rank if first_rank else 0.0) if evidence else None,
            "covered_evidence": sorted(covered), "empty_result": not hits}
