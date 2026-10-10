import re
from dataclasses import dataclass
from pathlib import Path


STOP_WORDS = {
    "a", "about", "an", "and", "are", "as", "at", "by", "can", "do", "does", "for",
    "from", "how", "i", "in", "is", "it", "of", "on", "or", "the", "to", "what",
    "where", "which", "who", "why", "with",
}


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {word.rstrip("s") for word in words if word not in STOP_WORDS and len(word) > 2}


@dataclass(frozen=True)
class DatasetResult:
    title: str
    text: str


class DatasetService:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(__file__).parents[2] / "data" / "space_facts.txt"
        self.sections = self._load()

    def _load(self) -> list[DatasetResult]:
        raw = self.path.read_text(encoding="utf-8")
        parts = re.split(r"^## ", raw, flags=re.MULTILINE)[1:]
        return [DatasetResult(title=p.split("\n", 1)[0], text=p.split("\n", 1)[1].strip()) for p in parts]

    def search(self, question: str, limit: int = 2) -> list[DatasetResult]:
        query_words = _keywords(question)
        ranked = sorted(
            self.sections,
            key=lambda section: (
                3 * len(query_words & _keywords(section.title))
                + len(query_words & _keywords(section.text))
            ),
            reverse=True,
        )
        return [section for section in ranked[:limit] if section]
