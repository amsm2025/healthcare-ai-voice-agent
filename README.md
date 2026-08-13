# Healthcare AI Voice Agent

A portfolio-ready full-stack AI healthcare appointment assistant built with **FastAPI, React, TypeScript, OpenAI-compatible LLM APIs, and Cal.com integration**.

> **Portfolio / demonstration project only.** This repository is not a medical device and must not be used for diagnosis, treatment, emergency triage, or storage of real protected health information (PHI) without an appropriate security, privacy, legal, and compliance review.

## What this project demonstrates

- Full-stack system design
- AI-assisted conversational workflows
- FastAPI REST APIs
- React + TypeScript frontend
- Appointment scheduling integration
- Clean service boundaries and configuration
- Dockerized local development
- Automated tests and GitHub Actions
- AWS ECS/Fargate-ready deployment structure

## Architecture

```text
Patient / User
      |
      v
React + TypeScript Web App
      |
      v
FastAPI Backend
  |        |          |
  |        |          +--> Cal.com Scheduling API
  |        |
  |        +--> LLM Provider
  |
  +--> In-memory / pluggable application services
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the detailed design.

## Core features

1. Conversational appointment-intake endpoint
2. Safe, non-diagnostic assistant behavior
3. Appointment availability abstraction
4. Booking abstraction for Cal.com
5. Health/status endpoint
6. React scheduling UI
7. Docker Compose development environment
8. Backend tests
9. CI workflow

## Technology stack

### Backend
- Python 3.12
- FastAPI
- Pydantic
- HTTPX
- Pytest

### Frontend
- React
- TypeScript
- Vite

### Infrastructure
- Docker
- Docker Compose
- AWS ECS / Fargate-ready container design
- GitHub Actions

## Quick start

### 1. Clone

```bash
git clone https://github.com/amsm2025/healthcare-ai-voice-agent.git
cd healthcare-ai-voice-agent
```

### 2. Configure environment

```bash
cp .env.example .env
```

Update the values in `.env`.

### 3. Start with Docker

```bash
docker compose up --build
```

Backend:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

Frontend:

```text
http://localhost:5173
```

## Run backend without Docker

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run frontend without Docker

```bash
cd frontend
npm install
npm run dev
```

## Example API request

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"I would like to schedule a general consultation next week.\"}"
```

## Safety principles

The assistant is deliberately designed to:

- avoid diagnosis;
- avoid prescribing medication;
- direct emergencies to local emergency services;
- collect only the minimum information needed for scheduling;
- avoid storing sensitive data by default.

## Suggested portfolio talking points

When presenting this project in an interview, explain:

- why the LLM is isolated behind a service interface;
- why scheduling is isolated from conversation logic;
- how you would add authentication, audit logs, encryption, and PHI controls;
- how ECS/Fargate provides stateless horizontal scaling;
- how you would move from a web chat demo to a voice channel using Twilio or a similar provider.

## Roadmap

- [ ] Real Cal.com API integration
- [ ] Voice provider integration
- [ ] PostgreSQL persistence
- [ ] Redis session cache
- [ ] OAuth / SSO
- [ ] RAG knowledge base for approved clinic FAQs
- [ ] Structured observability
- [ ] Terraform infrastructure
- [ ] Production-grade secrets management

## Author

**Angel Martin Manalansan**  
GitHub: [amsm2025](https://github.com/amsm2025)

Add your LinkedIn and portfolio URL here before publishing.
