# Personal Intelligence Server

A local-first personal intelligence server that runs on a spare laptop.

## Stack
- FastAPI
- PostgreSQL
- Redis
- Ollama
- Docker Compose

## Quick start
1. Copy `.env.example` to `.env`
2. Run `docker compose up -d --build`
3. Pull the model: `docker exec -it personal-intelligence-ollama ollama pull llama3.2`
4. Open `http://localhost:8000/docs`

## Health check
`GET /health`

## Ask local AI
`POST /ask` with JSON:
```json
{"question":"Help me think through a product idea"}
```

## Capture a note
`POST /notes` with JSON:
```json
{"content":"My idea or thought","title":"Optional title"}
```

## List notes
`GET /notes`

## Search notes
`GET /notes/search?q=your+query`

## CI/CD
This repo includes `.github/workflows/deploy.yml`, designed for a self-hosted GitHub Actions runner on the Mi laptop.
