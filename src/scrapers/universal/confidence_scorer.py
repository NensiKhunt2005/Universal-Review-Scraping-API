from src.scrapers.universal.metadata_classifier import QNA_PATTERN


class ConfidenceScorer:
    """Calculates multi-signal confidence scores for review candidates."""

    @staticmethod
    def calculate_score(text: str, evidence_score: float = 0.5, is_structured: bool = False) -> float:
        if not text:
            return 0.0

        if is_structured:
            return 0.98

        score = 0.4 + (evidence_score * 0.4)

        # Sentence punctuation bonus
        if any(p in text for p in ['.', '!', '?']):
            score += 0.15

        # Word count bonus
        word_count = len(text.split())
        if word_count > 6:
            score += 0.1

        # Negative penalties
        if QNA_PATTERN.search(text) or text.endswith("?"):
            score -= 0.8

        if "seller" in text.lower() and "service" in text.lower() and len(text) < 40:
            score -= 0.5

        return max(0.0, min(1.0, score))

    @staticmethod
    def is_acceptable(score: float, threshold: float = 0.55) -> bool:
        return score >= threshold
