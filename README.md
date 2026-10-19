# AI Resume Matcher API 🚀

An asynchronous, production-grade microservice built with **FastAPI**, **SQLModel**, and **PostgreSQL** that evaluates candidate resumes against job descriptions. It leverages a **Hybrid Scoring Engine** combining high-dimensional dense vector semantics via OpenAI embeddings with deterministic regex skill extraction.

---

## 🌟 Engineering Highlights & Optimizations

* **Zero-Latency In-Memory Matching:** Outbound OpenAI API latency is completely decoupled from the scoring pipeline. 1536-dimensional embeddings (`text-embedding-3-small`) are generated once during document ingestion (`/resumes/upload` and `/jobs/`) and cached as structured JSON in PostgreSQL. Runtime matching executes pure in-memory NumPy linear algebra, reducing match latency from **~2.5s down to <20ms**.
* **60/40 Hybrid Scoring Algorithm:**
  $$\text{Score} = (0.60 \times \text{Semantic Vector Similarity}) + (0.40 \times \text{Keyword Overlap Ratio})$$
* **Multi-Tenant Security & Isolation:** Full OAuth2 password bearer authentication with bcrypt password hashing. Users can only access, query, and evaluate their own uploaded resumes and audit histories.
* **Auto-Migrating Database Lifecycle:** Automatically executes idempotent startup schema migrations on deployment environments (such as Render) to ensure structural synchronization across database tables.
* **Modern High-Performance Containerization:** Multi-stage build leveraging Astral's standalone `uv` binary on `python:3.12-slim-bookworm` with pre-compiled bytecode for lightning-fast container startups and minimal image footprints.

---

## 📊 System Architecture

```mermaid
flowchart TD
    subgraph Ingestion_Stage [1. Ingestion Stage]
        A[User Uploads PDF Resume] -->|POST /resumes/upload| B[PDF Parsing & Text Extraction]
        B --> C[Compute 1536d Vector via OpenAI]
        C --> D[(PostgreSQL: Cached Embedding)]
        
        E[HR / Admin Submits Job] -->|POST /jobs/| F[Compute 1536d Vector via OpenAI]
        F --> G[(PostgreSQL: Cached Embedding)]
    end

    subgraph Runtime_Stage [2. Runtime Match Stage: <20ms]
        H[Trigger Match: POST /match/] --> I[Fetch Cached Embeddings from DB]
        I --> J[NumPy Cosine Similarity 60%]
        I --> K[Regex Skill Extraction & Gap Analysis 40%]
        J --> L[Composite Score & Summary Generation]
        K --> L
        L --> M[(Save to Match History)]
        L --> N[Return Instant 200 OK Response]
    end
```

---

## 🛠️ Tech Stack

* **Framework:** FastAPI, Uvicorn (ASGI)
* **Language & Runtime:** Python 3.12 (`python:3.12-slim-bookworm`)
* **Database & ORM:** PostgreSQL, SQLModel (SQLAlchemy 2.0 Core), Psycopg2
* **Package & Dependency Management:** `uv`, `pyproject.toml`, `uv.lock`
* **Vector Math & Science:** NumPy
* **Async Network Client:** HTTPX
* **Security & Auth:** PyJWT, Passlib (Bcrypt)
* **Document Processing:** PyPDF / PDFPlumber
* **Containerization & Deployment:** Docker, Render PaaS

---

## 📂 Project Structure

```text
AI-Resume-Matcher/
├── app/
│   ├── routers/
│   │   ├── auth.py          # User registration, login & JWT auth dependency
│   │   ├── jobs.py          # Job description ingestion & embedding generation
│   │   ├── match.py         # Sub-20ms hybrid matching & history lookup
│   │   └── resumes.py       # PDF parsing, text extraction & embedding caching
│   ├── services/
│   │   ├── matcher.py       # Hybrid scoring engine & NumPy cosine similarity
│   │   └── security.py      # Bcrypt password hashing & JWT token encoding
│   ├── config.py            # Pydantic base settings & environment loader
│   ├── database.py          # PostgreSQL engine, session dependency & auto-migrations
│   ├── main.py              # FastAPI application factory & router mounting
│   └── models.py            # SQLModel schema declarations
├── tests/                   # Pytest test suite
├── Dockerfile               # Production container using astral-sh/uv binary
├── .dockerignore            # Build context exclusions
├── pyproject.toml           # Project metadata & declared dependencies
├── uv.lock                  # Deterministic dependency lockfile
├── .python-version          # Python 3.12 environment pin
├── .env.example             # Template environment variables
└── README.md                # Project documentation & architecture guide
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.12+ and `uv` installed:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or via pip
pip install uv
```

### 2. Clone the Repository
```bash
git clone https://github.com/subesh-cse/ai-resume-matcher-api.git
cd ai-resume-matcher-api
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/resume_matcher
SECRET_KEY=your_super_secret_jwt_key
OPENAI_API_KEY=your_openai_api_key
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 4. Install Dependencies
Synchronize your virtual environment using `uv`:
```bash
uv sync
```

Alternatively, manually activate your virtual environment:
```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

### 5. Run the Server
Launch the local Uvicorn development server:
```bash
uvicorn app.main:app --reload
```

Interactive documentation will be available at:
* **Interactive Swagger UI:** `http://127.0.0.1:8000/docs`
* **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`

---

## 🐳 Docker Container Deployment

The application includes an optimized, standalone Docker image using `uv` for fast dependency installation and bytecode compilation.

### 1. Build the Docker Image
```bash
docker build -t ai-resume-matcher-api .
```

### 2. Run the Container
Pass your environment variables and bind port `10000`:
```bash
docker run -d \
  -p 10000:10000 \
  --env-file .env \
  --name resume-matcher-service \
  ai-resume-matcher-api
```

Access the containerized API at `http://localhost:10000/docs`.

---

## 📡 API Overview

| Router | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/auth/register` | Register a new user |
| **Auth** | `POST` | `/auth/token` | Log in and receive JWT bearer token |
| **Auth** | `GET` | `/auth/me` | Fetch authenticated user details |
| **Resumes** | `POST` | `/resumes/upload` | Upload PDF resume, extract text & cache vector |
| **Resumes** | `GET` | `/resumes/` | Retrieve all resumes uploaded by the current user |
| **Jobs** | `POST` | `/jobs/` | Create a job description & cache vector |
| **Jobs** | `GET` | `/jobs/` | List all job descriptions |
| **Match** | `POST` | `/match/` | Execute hybrid match scoring in <20ms |
| **Match** | `GET` | `/match/history` | List previous match outcomes and skill analyses |

---

## 🧪 Testing

Run automated tests using Pytest:
```bash
pytest -v
```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).


