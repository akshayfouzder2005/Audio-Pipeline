from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import upload, jobs, search

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Audio Transcription Pipeline", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(jobs.router)
app.include_router(search.router)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def serve_ui():
    return FileResponse("frontend/index.html")