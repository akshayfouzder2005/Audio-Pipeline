<div align="center">

# The Fluid Studio

### Audio Transcription Pipeline

**A production-style full-stack platform that transcribes audio, identifies speakers, and displays results in a Spotify-style live editor.**

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Redis](https://img.shields.io/badge/Redis_Streams-Upstash-DC382D?style=flat-square&logo=redis&logoColor=white)](https://upstash.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com)
[![Groq](https://img.shields.io/badge/Whisper_Large_v3-Groq-F55036?style=flat-square)](https://groq.com)
[![Cloudflare](https://img.shields.io/badge/Cloudflare_Pages-Frontend-F38020?style=flat-square&logo=cloudflare&logoColor=white)](https://pages.cloudflare.com)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

<br/>

**[▶ Live Demo](https://audio-pipeline.onrender.com/)** &nbsp;·&nbsp; **[API Docs](https://audio-pipeline.onrender.com/docs)**

</div>

---

## Overview

The Fluid Studio is a distributed audio transcription system. Upload an audio file and the pipeline queues it via Redis Streams, transcribes it using Groq Whisper Large v3, stores speaker-labeled segments in PostgreSQL, and renders them in a dark-themed SPA where the transcript highlights and scrolls in sync with audio playback — like Spotify.

Built to demonstrate distributed systems, async job queues, REST API design, JWT authentication, and real-time frontend engineering.

---

## System Architecture

```
┌──────────────────────┐        ┌─────────────────────────┐        ┌─────────────────┐
│                      │        │                         │        │                 │
│   Browser (SPA)      │──────▶ │   FastAPI  (Render)     │──────▶ │   PostgreSQL    │
│   Cloudflare Pages   │◀────── │   REST API + JWT Auth   │        │   (Supabase)    │
│                      │        │                         │        │                 │
└──────────────────────┘        └────────────┬────────────┘        └─────────────────┘
                                              │
                                              │  Redis Stream · audio:jobs
                                              ▼
                                 ┌────────────────────────┐        ┌─────────────────┐
                                 │                        │        │                 │
                                 │   Upstash Redis        │──────▶ │   Worker        │
                                 │   Job Queue            │        │   Groq Whisper  │
                                 │                        │        │   Large v3      │
                                 └────────────────────────┘        └─────────────────┘
```

**Request flow:**

```
User uploads audio
      │
      ▼
POST /api/upload → file saved → job created (status: pending)
      │
      ▼
Job ID pushed to Redis Stream  audio:jobs
      │
      ▼
Worker consumes → sends audio to Groq Whisper API
      │
      ▼
Segments saved to PostgreSQL  (speaker_label · start_time · end_time · text)
      │
      ▼
Frontend polls GET /api/jobs/{id} every 1s → status: completed
      │
      ▼
Transcript loads → Spotify-style sync activates
```

---

## Features

| | Feature | Details |
|---|---|---|
| 🔐 | **JWT Authentication** | Register / login with bcrypt hashing, 7-day token expiry |
| 🎙 | **Audio Upload** | Drag & drop WAV, MP3, FLAC, M4A up to 500MB |
| ⚡ | **Groq Whisper** | Whisper Large v3 on Groq LPUs with per-segment timestamps |
| 🔴 | **Redis Streams** | Async job queue with consumer groups, decoupled worker |
| 👥 | **Speaker Diarization** | Auto speaker separation with color-coded labels |
| 🎵 | **Spotify-style Sync** | Active segment highlights and auto-scrolls as audio plays |
| ✏️ | **Inline Editing** | Edit any transcript segment in-place via `PATCH` endpoint |
| 🔍 | **Live Search** | Full-text search across segments with real-time highlight |
| 📊 | **Insights Page** | Speaker talk-time bars, word count, segment analytics |
| 📤 | **Export** | Download transcript as TXT, JSON, or SRT |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vanilla JS · Tailwind CSS · Material Symbols · SPA |
| **API** | FastAPI · Uvicorn · SQLAlchemy · Pydantic |
| **Auth** | JWT HS256 · python-jose · passlib · bcrypt |
| **Queue** | Redis Streams · Upstash (TLS) |
| **Worker** | Python · Groq SDK · Whisper Large v3 |
| **Database** | PostgreSQL · Supabase |
| **Infra** | Render · Cloudflare Pages · Docker |

---

## Database Schema

```
users
  id               UUID  PK
  email            VARCHAR  UNIQUE
  username         VARCHAR  UNIQUE
  hashed_password  VARCHAR
  created_at       TIMESTAMPTZ

jobs
  id          UUID  PK
  user_id     UUID  FK → users
  filename    VARCHAR
  file_path   VARCHAR
  status      VARCHAR    pending → processing → completed | failed
  created_at  TIMESTAMPTZ

transcripts
  id               UUID  PK
  job_id           UUID  FK → jobs
  full_text        TEXT
  language         VARCHAR
  duration_seconds FLOAT
  created_at       TIMESTAMPTZ

segments
  id            UUID  PK
  transcript_id UUID  FK → transcripts
  speaker_label VARCHAR
  start_time    FLOAT
  end_time      FLOAT
  text          TEXT
```

---

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | — | Create account, returns JWT |
| `POST` | `/auth/login` | — | Login, returns JWT |
| `GET` | `/auth/me` | ✓ | Get current user |
| `GET` | `/health` | — | Health check |
| `POST` | `/api/upload` | ✓ | Upload audio file, returns job |
| `GET` | `/api/jobs` | ✓ | List last 20 jobs |
| `GET` | `/api/jobs/{id}` | ✓ | Get job status |
| `GET` | `/api/jobs/{id}/transcript` | ✓ | Full transcript with segments |
| `GET` | `/api/audio/{id}` | ✓ | Stream audio file |
| `DELETE` | `/api/jobs/{id}` | ✓ | Delete job + transcript + audio |
| `PATCH` | `/api/segments/{id}` | ✓ | Edit segment text |

---

## Project Structure

```
audio-pipeline/
│
├── app/
│   ├── main.py              # FastAPI app, CORS, router registration
│   ├── config.py            # Pydantic settings from .env
│   ├── database.py          # SQLAlchemy engine + session
│   ├── models.py            # ORM models — User, Job, Transcript, Segment
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── redis_client.py      # Redis connection pool (TLS)
│   └── routers/
│       ├── auth.py          # Register, login, JWT, /me
│       ├── upload.py        # POST /api/upload
│       ├── jobs.py          # Job status, transcript, audio stream
│       └── search.py        # Full-text segment search
│
├── worker/
│   ├── main.py              # Redis Stream consumer loop
│   └── groq_client.py       # Groq Whisper API — transcribe + parse segments
│
├── frontend/
│   └── index.html           # Single-page app — auth, upload, editor, insights
│
├── Dockerfile               # API container (~200MB, no ML libs)
├── requirements.txt
└── .env.example
```

---

## Local Setup

**Prerequisites:** Python 3.11+, FFmpeg, Supabase project, Upstash Redis, Groq API key

```bash
# Clone and install
git clone https://github.com/akshayfouzdar2005/audio-pipeline.git
cd audio-pipeline

python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
cp .env.example .env
```

**.env**

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require
REDIS_URL=rediss://default:password@host.upstash.io:6379
GROQ_API_KEY=your_groq_key
SECRET_KEY=your_secret_key
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=50
```

Generate `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Start:**

```bash
# Terminal 1 — API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Worker
python -m worker.main
```

Open `http://127.0.0.1:8000` → register → upload audio.

---

## Deployment

All free — $0/month.

| Component | Service |
|---|---|
| API | Render (Docker) |
| Frontend | Render |
| Worker | Huggingface Space |
| PostgreSQL | Supabase |
| Redis | Upstash |

**Render:** New Web Service → connect GitHub → Docker runtime → set env vars → deploy.

**Cloudflare Pages:** Upload `frontend/` folder → live instantly on global CDN.

---

## Production Bug Log

Real issues hit during development, documented for transparency.

| Issue | Root Cause | Fix |
|---|---|---|
| Redis TLS refused | Wrong URL scheme | Use `rediss://` not `redis://` |
| Docker image >4GB | torch + pyannote in container | API-only requirements, no ML libs |
| passlib bcrypt crash | Version incompatibility | Pin `bcrypt==4.0.1` |
| Supabase connection error | Special char in password | Encode `@` as `%40` in URL |
| CORS health check blocked | `allow_credentials=True` with wildcard origin | Set `allow_credentials=False` |
| Audio missing after transcription | Worker deleting file post-job | Remove `os.remove()` from worker |

---

<div align="center">

Built by **Akshay** — CS Student, Kolkata

`FastAPI` &nbsp;·&nbsp; `Redis Streams` &nbsp;·&nbsp; `Groq Whisper` &nbsp;·&nbsp; `PostgreSQL` &nbsp;·&nbsp; `JWT` &nbsp;·&nbsp; `Docker` &nbsp;·&nbsp; `Vanilla JS`

[![GitHub](https://img.shields.io/badge/GitHub-akshayfouzdar2005-181717?style=flat-square&logo=github)](https://github.com/akshayfouzdar2005)

</div>
