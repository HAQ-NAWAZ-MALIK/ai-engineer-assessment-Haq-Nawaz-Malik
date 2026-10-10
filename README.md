# Applab Chatbot

A source-aware FastAPI chatbot for space exploration and superhero questions. It searches a local Markdown knowledge base and the live Superhero API, then uses NVIDIA NIM (`z-ai/glm-5.3`) to write a grounded response with visible source references.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set these values in `.env`:

```env
NVIDIA_API_KEY=your-nvidia-key
NVIDIA_MODEL=z-ai/glm-5.3
SUPERHERO_API_TOKEN=your-superhero-token
SUPERHERO_BASE_URL=https://www.superheroapi.com/api
```

## Run

```powershell
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. Run tests with `python -m pytest tests -q -p no:cacheprovider`.

## Superhero API note

The `www.superheroapi.com` host can return an HTTP 302 redirect. Configure the client to follow redirects (`follow_redirects=True`) or Superhero requests may appear unavailable even with a valid token. Some networks and proxies also block the public API; allow outbound HTTPS access to `www.superheroapi.com` or use a network that permits it.
