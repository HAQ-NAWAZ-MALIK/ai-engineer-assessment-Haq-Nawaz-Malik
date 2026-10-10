import re

from app.schemas import SourceKind

SUPERHERO_TERMS = {
    "superhero", "superheroes", "hero", "heroes", "marvel", "dc", "avenger",
    "batman", "superman", "spider-man", "spiderman", "iron man", "hulk",
    "thor", "wonder woman", "flash", "joker", "wolverine", "deadpool",
}


def choose_sources(question: str) -> list[SourceKind]:
    """Route by explicit superhero vocabulary; dataset handles all other questions.

    Combining a superhero term with other content deliberately returns both sources.
    """
    normalized = re.sub(r"\s+", " ", question.lower()).strip()
    is_hero_question = any(term in normalized for term in SUPERHERO_TERMS)
    # Questions comparing a hero to another topic need both context sources.
    has_dataset_signal = any(word in normalized for word in ("mars", "moon", "space", "nasa", "telescope", "iss", "station"))
    if is_hero_question and has_dataset_signal:
        return [SourceKind.dataset, SourceKind.superhero_api]
    if is_hero_question:
        return [SourceKind.superhero_api]
    return [SourceKind.dataset]


def superhero_search_name(question: str) -> str:
    """Extract a likely character name without asking the model to invent one."""
    text = question.lower()
    for term in sorted(SUPERHERO_TERMS - {"superhero", "superheroes", "hero", "heroes", "marvel", "dc", "avenger"}, key=len, reverse=True):
        if term in text:
            return term.title().replace("Spiderman", "Spider-Man")
    # The API search is tolerant; use question as a fallback after removing common framing.
    return re.sub(r"\b(who|what|is|are|tell|me|about|the|a|an|superhero|hero)\b", "", question, flags=re.I).strip()[:80]
