# 🚀 backend-of-yt-ai-agent  
> Fast, stateless REST service that turns any YouTube video into a query-ready knowledge snippet in seconds.

---

## 🎯 Overview

**Problem**  
Learners waste hours scrubbing through videos to find the one insight they need.

**Target Users**  
Students, researchers, creators—anyone who wants instant, searchable understanding from YouTube content.

**Key Idea**  
Drop a YouTube URL → get back a clean transcript + AI-generated summary → ask questions → receive spoken answers.  
No sign-up, no waiting, no storage headaches.

---

## ✨ Features

* ⚡ Sub-5-second cold-start on Northflank serverless  
* 🎧 Downloads audio, transcribes with OpenAI Whisper  
* 🧠 Lightweight NLP enrichment (keywords, summary)  
* 💬 Single `/ask` endpoint for Q&A over the transcript  
* 🔊 Optional TTS response (MP3) for hands-free learning  
* 🪶 100 % stateless—scale to zero, scale to many  
* 🐳 Container-first: `docker build` → `docker run` → done  

---

## 🏗️ Architecture

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Client      │────▶│ FastAPI      │────▶│ YouTube      │
│  (web/cli)   │     │ monolith     │     │  audio       │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Whisper      │
                    │ (in-memory)  │
                    └──────────────┘
*No persistent database* – everything lives in RAM for the request lifetime.

---

## 🔑 Key Components

| Component        | Responsibility                          |
|------------------|-----------------------------------------|
| `main.py`        | FastAPI app, routing, validation         |
| `whisperizer.py` | Audio download + transcription         |
| `nlp.py`         | Keywords, summary, Q&A logic             |
| `tts.py`         | Optional text-to-speech (base64 MP3)   |

---

## 📡 Data Flow

1. Client `POST /transcribe` with `{ "url": "https://youtu.be/..." }`  
2. Server downloads audio stream → Whisper → text  
3. Text cached in-memory (key = video-id)  
4. Client `POST /ask` with `{ "video_id": "...", "question": "..." }`  
5. Server returns `{ "answer": "...", "audio_b64?": "..." }`

---

## 🧰 Tech Stack

* **Runtime**: Python 3.11  
* **Framework**: FastAPI + Uvicorn  
* **ASR**: OpenAI Whisper `base` model (≈ 75 MB)  
* **Deployment**: Northflank (K8s)  
* **CI/CD**: GitHub → Docker build → rolling update  
* **Package**: pip-tools (lockfile included)

---

## 📁 Project Structure

backend-of-yt-ai-agent/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── whisperizer.py
│   ├── nlp.py
│   └── tts.py
├── requirements.in
├── requirements.txt
├── Dockerfile
├── northflank.yaml
└── README.md   ← you are here
---

## ⚙️ Installation & Usage

### Local Development

bash
git clone https://github.com/abdul-0-muheed/backend-of-yt-ai-agent.git
cd backend-of-yt-ai-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
Visit: [http://localhost:8000/docs](http://localhost:8000/docs) 🎉

### Docker

bash
docker build -t yt-ai-backend .
docker run -p 8000:8000 yt-ai-backend
---

## 🔌 API / Integrations

| Method | Endpoint       | Description                     |
|--------|----------------|---------------------------------|
| POST   | `/transcribe`  | Accepts YouTube URL → returns transcript + summary |
| POST   | `/ask`         | Ask a question about a cached video |
| GET    | `/health`      | Liveness probe                  |

OpenAPI spec auto-generated at `/docs` and `/redoc`.

---

## 🔐 Environment Variables

| Var               | Default | Purpose                          |
|-------------------|---------|----------------------------------|
| `PORT`            | 8000    | Server port                      |
| `LOG_LEVEL`       | info    | Logging granularity              |
| `WHISPER_MODEL`   | base    | Whisper model size               |
| `MAX_AUDIO_MB`    | 25      | Download limit                   |
| `ENABLE_TTS`      | false   | Toggle TTS response              |

---

## 🧪 Testing & Build

bash
# lint
ruff app

# type check
mypy app

# unit tests (pytest)
pytest tests -q
Northflank auto-builds on every push to `main`; no manual steps needed.

---

## 📝 Notes

* No auth yet—rate-limit by IP if you expose publicly.  
* No persistent DB—if you need history, plug in any Postgres/S3 via env vars.  
* Whisper model is cached on first use; subsequent requests reuse it.

---

## 🤝 Contributing

1. Fork → feature branch → PR.  
2. Keep 100 % test coverage for new logic.  
3. Update `requirements.in` and run `pip-compile` if deps change.

---

## 📄 License

MIT © Abdul Muheed

---

## 📬 Contact

Open an issue or discussion on GitHub.  
[https://github.com/abdul-0-muheed/backend-of-yt-ai-agent](https://github.com/abdul-0-muheed/backend-of-yt-ai-agent)