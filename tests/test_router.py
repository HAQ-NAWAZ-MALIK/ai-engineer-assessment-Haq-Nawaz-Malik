import pytest
from pydantic import ValidationError

from app.schemas import AskRequest, SourceKind
from app.services.dataset import DatasetService
from app.services.router import choose_sources, superhero_search_name


def test_routes_dataset_question():
    assert choose_sources("Why is Mars red?") == [SourceKind.dataset]


def test_routes_blended_question():
    assert choose_sources("Compare Mars and Batman") == [SourceKind.dataset, SourceKind.superhero_api]


def test_extracts_known_hero():
    assert superhero_search_name("Who is Iron Man?") == "Iron Man"


def test_dataset_returns_relevant_section():
    assert DatasetService().search("Where does Webb operate?", limit=1)[0].title == "James Webb Space Telescope"


def test_dataset_matches_singular_query_to_plural_heading():
    assert DatasetService().search("How does a rocket reach orbit?", limit=1)[0].title == "Rockets and Orbits"


def test_question_normalizes_spaces_and_rejects_blank_input():
    assert AskRequest(question="  What is Mars?  ").question == "What is Mars?"
    with pytest.raises(ValidationError):
        AskRequest(question="   ")
