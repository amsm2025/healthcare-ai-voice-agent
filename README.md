# Healthcare AI Voice Agent

![Healthcare AI Voice Agent](docs/assets/healthcare-ai-voice-agent.png)

A full-stack AI-assisted healthcare appointment scheduling application demonstrating **FastAPI, React, TypeScript, service-oriented AI integration, automated testing, containerized development, and an AWS ECS/Fargate-ready deployment design**.

> **Portfolio / demonstration project only.** This repository is not a medical device and must not be used for diagnosis, treatment, emergency triage, or storage of real protected health information (PHI) without appropriate security, privacy, legal, and compliance review.

## Engineering objectives

This project demonstrates the design of an AI-enabled application across frontend, backend, integration, testing, and infrastructure boundaries.

- Clear separation between UI, API, AI, safety, and scheduling concerns
- Provider-independent service boundaries for LLM and scheduling integrations
- Typed frontend development with React and TypeScript
- Validated REST APIs with FastAPI and Pydantic
- Containerized, repeatable local development
- Automated backend testing and CI
- Cloud-ready architecture designed for stateless deployment and horizontal scaling

## Architecture

```text
Patient / User
      |
      v
React + TypeScript SPA
      |
      v
FastAPI Application
      |
      +-------------------+
      |                   |
      v                   v
Safety / AI Layer     Scheduling Service
      |                   |
      v                   v
 LLM Provider           Cal.com

Production direction:

CloudFront / CDN
      |
      v
React SPA
      |
      v
Application Load Balancer
      |
      v
AWS ECS / Fargate
      |
      +--> LLM Provider
      +--> Scheduling Provider
      +--> PostgreSQL / RDS
      +--> Redis / ElastiCache
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the detailed design and [`docs/AWS_DEPLOYMENT.md`](docs/AWS_DEPLOYMENT.md) for the deployment design.

## Core capabilities

- Conversational appointment-intake API
- Safe, non-diagnostic assistant behavior
- Emergency-language guardrail boundary
- Appointment availability service abstraction
- Booking abstraction for Cal.com
- Health/status endpoint
- React scheduling interface
- Docker Compose development environment
- Automated backend tests
- GitHub Actions CI workflow
- AWS ECS/Fargate-ready container architecture

## Technology stack

| Layer | Technologies |
| --- | --- |
| Frontend | React, TypeScript, Vite |
| Backend | Python 3.12, FastAPI, Pydantic, HTTPX |
| AI | Provider-isolated LLM service boundary |
| Scheduling | Cal.com service abstraction |
| Testing | Pytest |
| Containers | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Cloud architecture | AWS ECS / Fargate |

## Design decisions

### Isolated AI integration

AI interaction is kept behind a service boundary so providers, models, prompting strategies, and safety controls can evolve without tightly coupling them to API routes or scheduling logic.

### Scheduling abstraction

Scheduling is separated from conversation logic. This makes the booking provider replaceable, allows integrations to be mocked during testing, and isolates external API failures from the rest of the application.

### Safety-conscious boundaries

The current implementation is intentionally non-diagnostic. A production healthcare implementation would require clinically reviewed safety controls, formal privacy/compliance review, access control, audit logging, encryption, retention policies, and approved data-processing agreements.

### Cloud-ready deployment

The backend is structured for stateless container deployment. A production evolution can place containers behind an Application Load Balancer on ECS/Fargate and introduce managed persistence, caching, secrets management, centralized logging, monitoring, and infrastructure as code.

## Quick start

```bash
git clone https://github.com/amsm2025/healthcare-ai-voice-agent.git
cd healthcare-ai-voice-agent
cp .env.example .env
docker compose up --build
```

| Service | Local address |
| --- | --- |
| Backend API | `http://localhost:8000` |
| OpenAPI / Swagger | `http://localhost:8000/docs` |
| Frontend | `http://localhost:5173` |

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

## Testing

```bash
cd backend
pytest
```

The repository also includes a GitHub Actions workflow for automated validation in CI.

## Security and healthcare considerations

Before this architecture handles real healthcare data, a production implementation should include authentication and authorization, least-privilege access, encryption, managed secrets, audit logging, minimum-necessary data collection, retention policies, approved providers, applicable privacy/compliance review, appropriate BAAs/DPAs, threat modeling, and security testing.

No real PHI is required for this portfolio demonstration.

## Project status

This repository represents a working engineering demonstration and extensible architecture rather than a production clinical system.

### Roadmap

- [ ] Complete real Cal.com API wiring
- [ ] Add voice-provider integration
- [ ] Add PostgreSQL persistence
- [ ] Add Redis-backed session state
- [ ] Add OAuth / OIDC authentication
- [ ] Add RAG for approved clinic FAQs
- [ ] Add structured observability and tracing
- [ ] Add Terraform infrastructure
- [ ] Add production-grade secrets management
- [ ] Add production PHI controls following formal compliance review

## Documentation

- [`Architecture`](docs/ARCHITECTURE.md)
- [`AWS deployment`](docs/AWS_DEPLOYMENT.md)

## Author

**Angel Martin Manalansan**  
Senior Full Stack Engineer | AI-enabled Applications | Enterprise Systems

GitHub: [amsm2025](https://github.com/amsm2025)
