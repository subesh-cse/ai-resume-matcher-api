# AI Resume Matcher API

A high-performance, asynchronous REST API engineered to parse, index, and semantically rank resumes against structured job descriptions. Built with FastAPI, SQLModel, and SentenceTransformers.

---

## Architecture Overview

```text
[ Client / Swagger UI ]
          │
          ▼
   [ FastAPI Router ] ◄── OAuth2 Bearer Token (JWT)
          │
     ┌────┴──────────────────────────┐
     ▼                               ▼
[ Resume Upload ]             [ Match Endpoint ]
  - Multipart stream            - Fetch Resume & Job (SQLModel)
  - In-memory PDF parsing       - Hybrid Scoring Engine
  - pypdf extraction               * Cosine Semantic Similarity (60%)
  - Persistent storage             * Boundary Regex Keyword Match (40%)
```

---

## Core Features

- **Stateless Authentication:** Implements OAuth2 password flow with signed JSON Web Tokens (PyJWT) and bcrypt-hashed password persistence.
- **In-Memory Stream Processing:** Uses `io.BytesIO` to extract text from PDF uploads on-the-fly, eliminating temporary filesystem writes.
- **Hybrid Scoring Engine:** Combines dense semantic vector embeddings (`all-MiniLM-L6-v2`) via cosine similarity (60% weight) with isolated boundary regex keyword extraction (40% weight).
- **Singleton Lazy Loading:** Defers transformer model initialization to runtime via an encapsulated singleton pattern, preventing startup latency spikes.
- **Layer-Decoupled Schemas:** Decouples SQLModel database persistence entities from Pydantic request/response DTOs to enforce strict validation and prevent credential leakage.
- **Isolated Pytest Suite:** 100% test coverage using an in-memory SQLite engine (`StaticPool`), dependency overrides, and per-test table teardown fixtures.
- **Container-Ready:** Includes a multi-stage `Dockerfile` leveraging Astral `uv` for reproducible, isolated deployments.

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Framework** | FastAPI (Python 3.12+) |
| **Package & Env Manager** | Astral `uv` |
| **ORM / Data Modeling** | SQLModel (SQLAlchemy Core + Pydantic) |
| **Database** | SQLite (Local/Testing) / PostgreSQL (Engine-ready) |
| **Security** | PyJWT, Passlib (Bcrypt) |
| **NLP & Scoring** | SentenceTransformers (`all-MiniLM-L6-v2`), PyPDF, Regex |
| **Testing** | Pytest, HTTPX (`TestClient`) |
| **Containerization** | Docker |

---

## Project Structure

```text
├── app/
│   ├── routers/
│   │   ├── auth.py          # Registration, token issuance, get_current_user
│   │   ├── jobs.py          # Job description CRUD operations
│   │   ├── match.py         # Orchestration endpoint for scoring
│   │   └── resumes.py       # Multipart PDF parsing and persistence
│   ├── services/
│   │   ├── matcher.py       # Singleton ML inference & scoring logic
│   │   └── security.py      # Password hashing and JWT encoding/decoding
│   ├── config.py            # Pydantic-Settings environment validation
│   ├── database.py          # Session lifecycles & engine configuration
│   ├── main.py              # Application entrypoint & CORS setup
│   └── models.py            # Persistence tables & request/response schemas
├── tests/
│   ├── conftest.py          # StaticPool SQLite fixtures & dependency mocks
│   ├── test_api.py          # End-to-end endpoint integration tests
│   └── test_matcher.py      # Unit tests for scoring math and regex boundaries
├── Dockerfile               # Multi-layer uv production build
├── .dockerignore
└── pyproject.toml
```

---

## Getting Started

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/subesh-cse/ai-resume-matcher-api
cd ai-resume-matcher-api
uv sync
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
DATABASE_URL=sqlite:///./database.db
SECRET_KEY=your_secure_random_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Run the Development Server
```bash
uv run uvicorn app.main:app --reload
```
Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs`.

---

## Automated Test Suite

Run the isolated test suite:
```bash
uv run pytest -v
```

---

## Containerization

Build the Docker image:
```bash
docker build -t ai-resume-matcher .
```

Run the container:
```bash
docker run -p 8000:8000 ai-resume-matcher
```

---

## Engineering Trade-offs & Decisions

- **In-Memory vs. Filesystem Extraction:** PDF uploads are ingested as byte streams into `io.BytesIO` buffers. This eliminates local disk I/O bottlenecks and avoids orphaned temporary files in st[...]
- **Singleton ML Inference:** The `SentenceTransformer` model is initialized lazily and cached on the `HybridScoringEngine` instance, ensuring model weights are loaded into memory exactly once pe[...]
- **Synchronous Database Operations:** Standard SQLModel session transactions are executed inside standard `def` routes, allowing FastAPI to delegate blocking database I/O to an internal threadpo[...]

---

## Roadmap (v2)

- [ ] Row-level access control (`user_id` foreign key association on resumes).
- [ ] Database migration to managed PostgreSQL using Alembic.
- [ ] Redis-backed token revocation denylist.

---

## Quick demo using the bundled Python script (no frontend required)

If you don't want a frontend or don't know curl, you can use the included Python demo script to run the full flow: register, login, create a job, upload a PDF resume, and request a match.

1) Start the API (same terminal):

```bash
uv run uvicorn app.main:app --reload
```

2) Install the runtime dependency for the demo script (only httpx is required):

```bash
python -m pip install --user httpx
```

3) Run the demo script (replace the `--pdf-path` with a local PDF resume you have):

```bash
python scripts/demo.py \
  --base-url http://127.0.0.1:8000 \
  --email demo@example.com \
  --password demo-password \
  --pdf-path ./sample_resume.pdf \
  --job-title "Software Engineer" \
  --job-desc "3+ years Python, FastAPI, SQL" 
```

The script will print out the created user, tokens, resume id, job id, and the match response JSON.

---

## Manual API examples (for reference)

If you later want to try curl or HTTPie, here are the main calls (these are optional — the Python script above automates everything):

1) Register (JSON):

```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo-password"}'
```

2) Obtain token (form data):

```bash
curl -X POST "http://127.0.0.1:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@example.com&password=demo-password"
```

3) Create job (authenticated):

```bash
curl -X POST "http://127.0.0.1:8000/jobs" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Software Engineer","description":"Python, FastAPI"}'
```

4) Upload resume (authenticated, multipart):

```bash
curl -X POST "http://127.0.0.1:8000/resumes/upload" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@./sample_resume.pdf;type=application/pdf"
```

5) Match (authenticated):

```bash
curl -X POST "http://127.0.0.1:8000/match" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"resume_id": 1, "job_id": 1}'
```

---

If you want, I can also add a Postman collection or an exported Insomnia file so you (or an interviewer) can import and run the requests with a GUI — say the word and I’ll add it.
