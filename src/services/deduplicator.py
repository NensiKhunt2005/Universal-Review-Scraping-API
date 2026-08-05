from typing import List


class Deduplicator:
    @staticmethod
    def remove_exact_duplicates(reviews: List[str]) -> List[str]:
        """Removes purely identical strings while preserving order."""
        seen = set()
        unique_reviews = []
        for review in reviews:
            if review not in seen:
                seen.add(review)
                unique_reviews.append(review)
        return unique_reviews

    @staticmethod
    def remove_normalized_duplicates(reviews: List[str]) -> List[str]:
        """Removes duplicates based on case-insensitive matches."""
        seen = set()
        unique_reviews = []
        for review in reviews:
            normalized = review.lower().strip()
            if normalized not in seen:
                seen.add(normalized)
                unique_reviews.append(review)
        return unique_reviews
