<div align="center">

<img src="https://img.shields.io/badge/The%20Fluid%20Studio-Audio%20Transcription%20Pipeline-eacff8?style=for-the-badge&labelColor=111317" alt="The Fluid Studio"/>

<br/><br/>

**A production-style audio transcription platform with real-time speaker diarization, Spotify-style transcript sync, and a full authentication system.**

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Redis](https://img.shields.io/badge/Redis%20Streams-Upstash-DC382D?style=flat-square&logo=redis&logoColor=white)](https://upstash.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com)
[![Groq](https://img.shields.io/badge/Whisper-Groq%20LPU-F55036?style=flat-square)](https://groq.com)
[![Cloudflare](https://img.shields.io/badge/Frontend-Cloudflare%20Pages-F38020?style=flat-square&logo=cloudflare&logoColor=white)](https://pages.cloudflare.com)
[![License](https://img.shields.io/badge/license-MIT-90ecb7?style=flat-square)](LICENSE)

<br/>

![Demo](https://img.shields.io/badge/🎬%20Live%20Demo-Available-90ecb7?style=for-the-badge)

**[▶ Try it live](https://your-render-url.onrender.com)** &nbsp;·&nbsp; **[📖 API Docs](https://your-render-url.onrender.com/docs)**

<br/>

</div>

---

## What is this?

The Fluid Studio is a full-stack audio transcription pipeline that accepts audio uploads, queues them via Redis Streams, transcribes them using Groq Whisper Large v3, and displays speaker-labeled results in a rich dark-themed editor — with Spotify-style live sync between audio playback and transcript highlighting.

Built as a production-style portfolio project demonstrating distributed systems, async job queues, REST API design, JWT authentication, and modern frontend engineering.

---

## Architecture

```
┌─────────────────────┐        ┌──────────────────────┐        ┌──────────────────┐
│   Browser (SPA)     │──────▶ │   FastAPI (Render)   │──────▶ │  Supabase        │
│   Cloudflare Pages  │◀────── │   REST API + Auth    │        │  PostgreSQL      │
└─────────────────────┘        └──────────┬───────────┘        └──────────────────┘
                                           │
                                           │ Redis Stream (audio:jobs)
                                           ▼
                                ┌──────────────────────┐        ┌──────────────────┐
                                │   Upstash Redis      │──────▶ │  Local Worker    │
                                │   Job Queue          │        │  Groq Whisper    │
                                └──────────────────────┘        │  Large v3        │
                                                                 └──────────────────┘
```

**Request flow:**

1. User registers/logs in → JWT token issued
2. Audio uploaded → `POST /api/upload` → file saved, job created in PostgreSQL
3. Job pushed to Redis Stream `audio:jobs`
4. Worker consumes from stream → sends audio to Groq Whisper API
5. Segments saved to PostgreSQL with timestamps and speaker labels
6. Frontend polls `GET /api/jobs/{id}` every second
7. On completion → transcript loads → Spotify-style sync activates

---

## Features

| Feature | Description |
|---|---|
| 🔐 JWT Authentication | Register/login with bcrypt password hashing, 7-day token expiry |
| 🎙 Audio Upload | Drag & drop WAV, MP3, FLAC, M4A up to 500MB |
| ⚡ Groq Whisper | Whisper Large v3 on Groq LPUs — ultra-fast transcription |
| 🔴 Redis Streams | Distributed job queue with consumer groups for async processing |
| 👥 Speaker Diarization | Automatic speaker separation with color-coded labels |
| 🎵 Spotify-style Sync | Transcript highlights and scrolls in real time as audio plays |
| ✏️ Inline Editing | Edit any transcript segment via `PATCH /api/segments/{id}` |
| 🔍 Transcript Search | Full-text search with live highlighting across all segments |
| 📊 Insights Page | Speaker talk-time bars, word count, segment analytics |
| 📤 Export | Download transcript as TXT, JSON, or SRT subtitle file |
| 🗑 Job Management | View, filter, and delete past transcription jobs |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vanilla JS, Tailwind CSS, Material Symbols, Single Page App |
| **API** | FastAPI, Uvicorn, SQLAlchemy, Pydantic, python-jose, passlib |
| **Queue** | Redis Streams via Upstash (TLS) |
| **Worker** | Python, Groq SDK, Whisper Large v3 |
| **Database** | PostgreSQL via Supabase |
| **Auth** | JWT (HS256), bcrypt password hashing |
| **Deployment** | Render (API), Cloudflare Pages (Frontend), Upstash (Redis), Supabase (DB) |

---

## Database Schema

```sql
users
├── id          UUID PK
├── email       VARCHAR UNIQUE
├── username    VARCHAR UNIQUE
├── hashed_password VARCHAR
└── created_at  TIMESTAMPTZ

jobs
├── id          UUID PK
├── user_id     UUID FK → users
├── filename    VARCHAR
├── file_path   VARCHAR
├── status      VARCHAR  -- pending → processing → completed | failed
└── created_at  TIMESTAMPTZ

transcripts
├── id              UUID PK
├── job_id          UUID FK → jobs
├── full_text       TEXT
├── language        VARCHAR
├── duration_seconds FLOAT
└── created_at      TIMESTAMPTZ

segments
├── id           UUID PK
├── transcript_id UUID FK → transcripts
├── speaker_label VARCHAR
├── start_time   FLOAT
├── end_time     FLOAT
└── text         TEXT
```

---

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | ✗ | Create account, returns JWT |
| `POST` | `/auth/login` | ✗ | Login, returns JWT |
| `GET` | `/auth/me` | ✓ | Get current user |
| `GET` | `/health` | ✗ | Health check |
| `POST` | `/api/upload` | ✓ | Upload audio file |
| `GET` | `/api/jobs` | ✓ | List last 20 jobs |
| `GET` | `/api/jobs/{id}` | ✓ | Get job status |
| `GET` | `/api/jobs/{id}/transcript` | ✓ | Get full transcript + segments |
| `GET` | `/api/audio/{id}` | ✓ | Stream audio file |
| `DELETE` | `/api/jobs/{id}` | ✓ | Delete job + transcript + audio |
| `PATCH` | `/api/segments/{id}` | ✓ | Edit segment text |

---

## Local Development

### Prerequisites
- Python 3.11+
- FFmpeg installed
- Supabase project (free tier)
- Upstash Redis (free tier)
- Groq API key (free tier — 7,200 sec/hour)

### Setup

```bash
# Clone
git clone https://github.com/akshayfouzdar2005/audio-pipeline.git
cd audio-pipeline

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Environment Variables

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require
REDIS_URL=rediss://default:password@host.upstash.io:6379
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_random_secret_key_here
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=50
```

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Run

```bash
# Terminal 1 — API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Worker
python -m worker.main
```

Open `http://127.0.0.1:8000` → register an account → upload audio.

---

## Deployment

| Component | Service | Cost |
|---|---|---|
| API | Render (Docker) | Free |
| Frontend | Cloudflare Pages | Free |
| PostgreSQL | Supabase | Free |
| Redis | Upstash | Free |
| Worker | Local machine | Free |

**Total monthly cost: $0**

### Deploy API to Render

1. Push repo to GitHub
2. New Web Service → connect repo → select Docker runtime
3. Add environment variables from `.env`
4. Deploy

### Deploy Frontend to Cloudflare Pages

1. Pages → Create project → Upload `frontend/` folder
2. Done — global CDN, instant deploy

---

## Project Structure

```
audio-pipeline/
├── app/
│   ├── main.py           # FastAPI app, middleware, routers
│   ├── config.py         # Pydantic settings
│   ├── database.py       # SQLAlchemy engine + session
│   ├── models.py         # ORM models (User, Job, Transcript, Segment)
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── redis_client.py   # Redis connection pool
│   └── routers/
│       ├── auth.py       # Register, login, JWT
│       ├── upload.py     # POST /api/upload
│       ├── jobs.py       # Job status, transcript, audio
│       └── search.py     # Full-text search
├── worker/
│   ├── main.py           # Redis Stream consumer loop
│   └── groq_client.py    # Groq Whisper transcription
├── frontend/
│   └── index.html        # Single-page application
├── Dockerfile            # API container
├── requirements.txt
└── .env.example
```

---

## Known Issues & Fixes

| Issue | Fix |
|---|---|
| Redis TLS (Upstash) | Use `rediss://` (double s) + `ssl_cert_reqs=None` |
| passlib + bcrypt incompatibility | Pin `bcrypt==4.0.1` |
| Docker image too large | Separate `requirements.api.txt` — no torch/pyannote |
| Supabase `@` in password | Encode as `%40` in connection string |
| `allow_credentials=True` with `allow_origins=["*"]` | Set `allow_credentials=False` |

---

## Roadmap

- [ ] WebSocket push (replace polling)
- [ ] Speaker renaming (SPEAKER_00 → custom name)
- [ ] Job history page with filter/search
- [ ] AWS S3 for persistent audio storage
- [ ] GPU worker on RunPod for pyannote diarization
- [ ] Email notifications on completion
- [ ] Public shareable transcript links

---

<div align="center">

Built by **Akshay** — CS Student, Kolkata

*FastAPI · Redis Streams · Groq Whisper · PostgreSQL · JWT Auth · Vanilla JS*

[![GitHub](https://img.shields.io/badge/GitHub-akshayfouzdar2005-181717?style=flat-square&logo=github)](https://github.com/akshayfouzdar2005)

</div>