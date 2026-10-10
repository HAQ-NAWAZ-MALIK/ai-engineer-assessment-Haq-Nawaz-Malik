from enum import Enum

from pydantic import BaseModel, Field, field_validator


class SourceKind(str, Enum):
    dataset = "dataset"
    superhero_api = "superhero_api"


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500, description="Natural-language question")

    @field_validator("question")
    @classmethod
    def question_must_contain_text(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 3:
            raise ValueError("Please enter a question with at least 3 characters.")
        return cleaned


class Citation(BaseModel):
    source: SourceKind
    label: str
    reference: str


class AskResponse(BaseModel):
    answer: str
    sources: list[Citation]
    route: list[SourceKind]
