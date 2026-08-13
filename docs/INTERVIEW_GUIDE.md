# Interview Guide

## 30-second project explanation

"I built a full-stack AI appointment assistant using FastAPI and React. I separated conversation, safety and scheduling into independent services so the system is testable and vendor-agnostic. The demo includes emergency guardrails, a Cal.com integration boundary, Docker, automated tests and an AWS ECS/Fargate deployment design."

## System-design questions you should be ready to answer

### Why FastAPI?
- strong Python ecosystem for AI;
- async API support;
- automatic OpenAPI documentation;
- Pydantic validation.

### Why isolate the LLM?
AI vendors and models change quickly. A service boundary prevents business logic from becoming tightly coupled to one provider.

### How would you handle PHI?
Use minimum-necessary data collection, encryption, access controls, audit logging, approved vendors, secrets management, retention policies, and legal/compliance review.

### How would you scale?
Deploy stateless FastAPI containers on ECS/Fargate behind an ALB, use RDS for durable data, Redis for short-lived sessions, and autoscaling based on request/CPU metrics.
