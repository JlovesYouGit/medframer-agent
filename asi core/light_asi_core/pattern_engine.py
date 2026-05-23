from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Dict, List

from .types import MedDocument, PatternReport
from .utils import tokenize


class RecursivePatternEngine:
    STOPWORDS = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "are",
        "was",
        "were",
        "not",
        "have",
        "has",
        "had",
        "into",
        "else",
        "elif",
        "true",
        "false",
        "none",
        "return",
        "class",
        "def",
        "import",
        "self",
    }

    def _clean_tokens(self, text: str) -> List[str]:
        return [t for t in tokenize(text) if t not in self.STOPWORDS]

    def build(self, documents: List[MedDocument]) -> PatternReport:
        term_freq: Counter[str] = Counter()
        doc_presence: Counter[str] = Counter()
        pair_freq: Counter[tuple[str, str]] = Counter()

        for doc in documents:
            tokens = self._clean_tokens(doc.text)
            if not tokens:
                continue
            term_freq.update(tokens)

            per_doc_top = [term for term, _ in Counter(tokens).most_common(30)]
            unique_terms = sorted(set(per_doc_top))
            doc_presence.update(unique_terms)

            for a, b in combinations(unique_terms, 2):
                pair_freq[(a, b)] += 1

        top_terms = [
            {
                "term": term,
                "frequency": freq,
                "documents": int(doc_presence.get(term, 0)),
            }
            for term, freq in term_freq.most_common(80)
        ]
        co_occurrence = [
            {"a": a, "b": b, "weight": weight}
            for (a, b), weight in pair_freq.most_common(120)
            if weight >= 2
        ]
        recursive_signals = [
            {"term": term, "documents": docs, "frequency": int(term_freq[term])}
            for term, docs in doc_presence.items()
            if docs >= 3 and term_freq[term] >= 8
        ]
        recursive_signals.sort(key=lambda item: (item["documents"], item["frequency"]), reverse=True)

        return PatternReport(
            top_terms=top_terms,
            co_occurrence=co_occurrence,
            recursive_signals=recursive_signals[:60],
            document_count=len(documents),
        )
