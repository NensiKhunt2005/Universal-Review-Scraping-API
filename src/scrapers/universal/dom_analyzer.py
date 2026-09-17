from typing import Dict, List, Optional, Set
from bs4 import BeautifulSoup, Tag


class DOMAnalyzer:
    """Analyzes DOM structure, repeated fingerprints, and card container boundaries."""

    @staticmethod
    def get_element_fingerprint(tag: Tag) -> Dict[str, str]:
        """Generates a structural fingerprint for repeated container matching."""
        direct_children = [c for c in tag.children if isinstance(c, Tag)]
        p_count = len(tag.find_all("p", recursive=False))
        span_count = len(tag.find_all("span", recursive=False))
        div_count = len(tag.find_all("div", recursive=False))

        return {
            "tag": tag.name,
            "child_count": str(len(direct_children)),
            "p_count": str(p_count),
            "span_count": str(span_count),
            "div_count": str(div_count)
        }

    @staticmethod
    def find_card_boundary(anchor_tag: Tag, max_depth: int = 8) -> Tag:
        """
        Traverses upward from an anchor tag until text expansion ratio or sibling card
        repetition indicates the individual review card boundary has been reached.
        """
        curr = anchor_tag
        last_len = len(curr.get_text(strip=True))

        for _ in range(max_depth):
            # If current element is an explicit article or role=article, return it immediately
            if curr.name == "article" or curr.get("role") == "article":
                return curr

            parent = curr.parent
            if not parent or not isinstance(parent, Tag) or parent.name in ["body", "html", "main"]:
                break

            parent_text_len = len(parent.get_text(strip=True))

            # Check if current container actually encloses review body text
            has_review_text = False
            for child in curr.find_all(["p", "div", "span"], recursive=True):
                t = child.get_text(strip=True)
                from src.scrapers.universal.metadata_classifier import MetadataClassifier
                if MetadataClassifier.classify(t) == "REVIEW":
                    has_review_text = True
                    break

            if has_review_text:
                # If parent contains multiple sibling elements of the same tag as curr,
                # then curr is an individual card in a list of cards!
                siblings = [c for c in parent.children if isinstance(c, Tag) and c.name == curr.name]
                if len(siblings) > 1:
                    return curr

                # Text Expansion Ratio Check: If parent text suddenly expands by > 1000 chars,
                # we crossed the individual review card boundary into the list container.
                if parent_text_len - last_len > 1000:
                    return curr

            curr = parent
            last_len = parent_text_len

        return curr

    @staticmethod
    def find_lca(tags: List[Tag]) -> Optional[Tag]:
        """Finds the lowest common ancestor of a list of tags."""
        if not tags:
            return None
        if len(tags) == 1:
            return tags[0]

        # Get parent lineage for first tag
        ancestors: List[Tag] = []
        curr = tags[0]
        while curr and isinstance(curr, Tag):
            ancestors.append(curr)
            curr = curr.parent

        # Find first ancestor shared by all other tags
        for ancestor in ancestors:
            if all(ancestor in t.parents for t in tags[1:] if isinstance(t, Tag)):
                return ancestor

        return None
