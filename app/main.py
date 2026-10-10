from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.config import get_settings
from app.schemas import AskRequest, AskResponse, Citation, SourceKind
from app.services.dataset import DatasetService
from app.services.llm import LLMService
from app.services.router import choose_sources, superhero_search_name
from app.services.superhero import SuperheroService

app = FastAPI(title="Applab Chatbot", version="1.1.0")
dataset = DatasetService()


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    route = choose_sources(request.question)
    context_blocks: list[str] = []
    citations: list[Citation] = []

    if SourceKind.dataset in route:
        for item in dataset.search(request.question):
            context_blocks.append(f"[Dataset: {item.title}]\n{item.text}")
            citations.append(Citation(source=SourceKind.dataset, label=f"Space Exploration Primer — {item.title}", reference="data/space_facts.txt"))

    if SourceKind.superhero_api in route:
        try:
            heroes = await SuperheroService(get_settings()).search(superhero_search_name(request.question))
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Superhero data provider is unavailable") from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        if not heroes:
            raise HTTPException(status_code=404, detail="No superhero matched that question")
        for hero in heroes:
            name, biography, appearance = hero.get("name", "Unknown"), hero.get("biography", {}), hero.get("appearance", {})
            context_blocks.append(f"[Superhero API: {name}]\nFull name: {biography.get('full-name', 'Unknown')}; Publisher: {biography.get('publisher', 'Unknown')}; Alignment: {biography.get('alignment', 'Unknown')}; Race: {appearance.get('race', 'Unknown')}")
            citations.append(Citation(source=SourceKind.superhero_api, label=f"Superhero API — {name}", reference=f"https://superheroapi.com/api/{{token}}/search/{name}"))

    try:
        answer = await LLMService(get_settings()).answer(request.question, "\n\n".join(context_blocks))
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="NVIDIA NIM is unavailable") from exc
    except (RuntimeError, KeyError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return AskResponse(answer=answer, sources=citations, route=route)
