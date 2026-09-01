import os
from contextlib import asynccontextmanager
from typing import Generator

import requests
from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Note

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Personal Intelligence Server",
    version="0.1.0",
    lifespan=lifespan,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10000)


class NoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=50000)
    title: str | None = Field(default=None, max_length=300)


@app.get("/")
def root():
    return {"message": "Personal Intelligence Server is running"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "api": "healthy",
        "postgres": "healthy",
        "redis": "configured",
        "ollama_model": OLLAMA_MODEL,
    }


@app.post("/ask")
def ask_ai(payload: AskRequest):
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": payload.question,
                "stream": False,
            },
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "question": payload.question,
            "answer": data.get("response", ""),
            "model": OLLAMA_MODEL,
        }
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Local Ollama service is unavailable: {exc}",
        ) from exc


@app.post("/notes", status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@app.get("/notes")
def list_notes(limit: int = 50, db: Session = Depends(get_db)):
    limit = min(max(limit, 1), 200)
    notes = db.scalars(
        select(Note).order_by(Note.created_at.desc()).limit(limit)
    ).all()
    return notes


@app.get("/notes/search")
def search_notes(q: str, db: Session = Depends(get_db)):
    q = q.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    pattern = f"%{q}%"
    notes = db.scalars(
        select(Note)
        .where(or_(Note.title.ilike(pattern), Note.content.ilike(pattern)))
        .order_by(Note.created_at.desc())
        .limit(100)
    ).all()
    return {"query": q, "results": notes}

app.mount("/", StaticFiles(directory="app/static"),html=True, name="static")