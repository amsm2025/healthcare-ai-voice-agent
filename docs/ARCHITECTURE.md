# Healthcare AI Voice Agent — Architecture

## Purpose

This document describes the system design of a production-oriented AI-assisted healthcare appointment scheduling application. The goal is to keep the user experience, API boundary, AI behavior, safety controls, scheduling integration, persistence, and cloud infrastructure separated so each area can evolve independently.

The current repository is a portfolio / engineering demonstration. It is not a production clinical system and should not process real PHI without formal security, privacy, legal, and compliance review.

## Architecture principles

- Separate conversation, safety, scheduling, persistence, and transport concerns.
- Keep external providers behind replaceable service interfaces.
- Never expose provider credentials or infrastructure secrets to the frontend.
- Keep the LLM isolated from direct scheduling and database credentials.
- Prefer stateless application services so compute can scale horizontally.
- Make integrations mockable so core behavior can be tested without external services.
- Collect and retain only the minimum data required for the intended workflow.
- Treat safety, privacy, observability, and auditability as architectural concerns rather than afterthoughts.

## Current logical architecture

```text
Patient / User
      |
      v
+---------------------------+
| React + TypeScript SPA    |
| - conversation UI         |
| - scheduling UI           |
| - client-side validation  |
+-------------+-------------+
              |
              | HTTPS / JSON
              v
+---------------------------+
| FastAPI Application       |
| - API boundary            |
| - request validation      |
| - orchestration           |
| - response contracts      |
+------+------+-------------+
       |      |
       |      +-----------------------------+
       |                                    |
       v                                    v
+-------------------+              +-----------------------+
| Safety / AI Layer |              | Scheduling Service    |
| - guardrails      |              | - availability        |
| - intent          |              | - booking abstraction |
| - responses       |              | - provider isolation  |
+---------+---------+              +-----------+-----------+
          |                                    |
          v                                    v
 OpenAI Responses API                    Cal.com API
```

## Component responsibilities

### React frontend

Responsible for:

- presenting the conversational scheduling experience;
- collecting appointment-related user input;
- displaying assistant and scheduling responses;
- performing lightweight client-side validation;
- calling backend APIs over HTTPS;
- eventually hosting microphone / voice controls.

The browser should never contain LLM, scheduling-provider, database, or AWS credentials.

### FastAPI application

Responsible for:

- HTTP and REST API boundaries;
- Pydantic request / response validation;
- CORS policy;
- orchestration of AI and scheduling services;
- consistent error responses;
- health endpoints;
- future authentication and authorization enforcement.

API routes should remain thin. Provider-specific logic belongs in service classes rather than route handlers.

### Safety layer

The safety boundary runs before normal generative behavior for obvious emergency language and other disallowed flows.

The portfolio implementation is intentionally limited. A production healthcare implementation would require clinically reviewed escalation rules, approved messaging, testing against realistic scenarios, and formal governance.

### LLM service

Responsible for:

- conversation intent handling;
- controlled natural-language response generation;
- prompting and model configuration;
- high-level safety-aware behavior;
- future retrieval-augmented FAQ responses.

The current implementation supports a deterministic demo mode and an optional live OpenAI Responses API path when configured with credentials. The LLM service must not receive infrastructure secrets, direct database credentials, or unrestricted scheduling credentials.

### Scheduling service

Cal.com is isolated behind a scheduling service abstraction.

The current implementation supports both deterministic demo bookings and an optional live Cal.com booking path. This boundary enables:

- provider replacement without changing API routes;
- local mocks and deterministic automated tests;
- controlled handling of external API failures;
- centralized mapping between internal models and provider payloads;
- future retry, timeout, and circuit-breaker policies.

## Request flow

A typical scheduling interaction follows this sequence:

```text
1. User submits a scheduling request in the React UI
2. Frontend validates basic input and calls FastAPI
3. FastAPI validates the request contract
4. Safety checks run before general AI behavior
5. AI service interprets the request / prepares an approved response
6. Scheduling service creates or coordinates a booking when required
7. Provider response is normalized into an internal application model
8. FastAPI returns a stable response contract to the frontend
9. Frontend renders the result to the user
```

This sequence intentionally prevents the frontend or LLM from directly controlling scheduling infrastructure.

## Production AWS topology

A production-oriented evolution can use the following deployment model:

```text
                         Internet
                            |
                            v
                  +-------------------+
                  | CloudFront / CDN  |
                  +---------+---------+
                            |
                +-----------+-----------+
                |                       |
                v                       v
       Static React assets      Application Load Balancer
                                        |
                                        v
                              +---------------------+
                              | ECS / Fargate Tasks |
                              | FastAPI containers  |
                              +----+------+---------+
                                   |      |
                     +-------------+      +----------------+
                     |                                     |
                     v                                     v
                LLM Provider                         Scheduling API
                     |
                     |
          +----------+-----------+
          |                      |
          v                      v
 PostgreSQL / RDS        Redis / ElastiCache
          |
          v
   encrypted storage

Supporting services:
- AWS Secrets Manager
- CloudWatch Logs / Metrics
- IAM roles
- ECR container registry
- optional WAF
```

## Data and state strategy

The current demonstration avoids requiring persistent sensitive patient data.

A production design could introduce:

- PostgreSQL / RDS for durable application records;
- Redis / ElastiCache for short-lived conversation or scheduling state;
- explicit retention and deletion rules;
- encrypted backups where required;
- data minimization so only workflow-essential fields are stored.

Session state should not be held only in ECS container memory because tasks may restart or scale independently.

## Security model

Before handling real healthcare information, the platform should implement:

- TLS for all external and internal service communication where applicable;
- encryption at rest for persistent stores and backups;
- OAuth / OIDC authentication;
- role-based authorization where needed;
- least-privilege IAM roles for ECS tasks and deployment automation;
- secrets stored in AWS Secrets Manager or an equivalent managed secret store;
- audit logging for security-sensitive actions;
- centralized application and infrastructure logging;
- rate limiting and abuse protection;
- dependency and container vulnerability scanning;
- retention and deletion policies;
- approved model and scheduling providers;
- PHI minimization before data is sent to model providers;
- HIPAA and applicable local privacy/compliance review;
- appropriate BAAs / DPAs;
- threat modeling and penetration testing.

## Reliability and failure handling

External AI and scheduling providers should be treated as unreliable network dependencies.

Production hardening should include:

- explicit connection and request timeouts;
- bounded retries only for safe idempotent operations;
- graceful user-facing fallback messages;
- correlation IDs for distributed troubleshooting;
- structured error logging;
- health and readiness checks;
- circuit-breaker or backoff policies where useful;
- idempotency controls for booking operations to avoid duplicate appointments.

## Scalability

The architecture favors stateless FastAPI containers so ECS can run multiple tasks behind an Application Load Balancer.

Scaling considerations include:

- horizontal API task scaling based on CPU, memory, request rate, or latency;
- external Redis-backed session state rather than process-local state;
- database connection pooling;
- caching only where consistency requirements permit it;
- asynchronous processing for non-interactive workloads;
- independent scaling of future background workers or integration services.

The project intentionally starts as a cohesive application rather than prematurely splitting into microservices. Service extraction should be driven by real scaling, ownership, isolation, or deployment requirements.

## Observability

A production system should expose enough telemetry to understand both technical and workflow health.

Recommended signals include:

- request counts and latency;
- error rates by endpoint and provider;
- scheduling-provider latency / failures;
- LLM latency and model errors;
- container CPU and memory;
- availability and booking success rates;
- structured application logs;
- distributed correlation IDs;
- alerts for sustained failure thresholds.

Sensitive healthcare information should not be written indiscriminately to logs.

## Testing strategy

The architecture supports layered testing:

- unit tests for safety, AI orchestration, validation, and scheduling logic;
- mocked provider tests for deterministic external integration behavior;
- API tests for FastAPI request / response contracts;
- frontend component and interaction tests;
- Docker-based integration testing;
- CI validation through GitHub Actions;
- future end-to-end tests against non-production provider environments.

Critical scheduling operations should be tested for duplicate requests, provider timeouts, malformed responses, and partial failures.

## Deployment path

A practical production evolution is:

```text
Local development
      |
      v
Docker Compose
      |
      v
GitHub Actions CI
      |
      v
ECR container image
      |
      v
ECS / Fargate
      |
      +--> ALB / HTTPS
      +--> Secrets Manager
      +--> CloudWatch
      +--> RDS / Redis when persistence is introduced
```

See [`AWS_DEPLOYMENT.md`](AWS_DEPLOYMENT.md) for deployment-specific guidance.

## Current boundaries and roadmap

The current project demonstrates working provider integration paths while deliberately identifying the remaining production gaps rather than presenting them as complete.

Implemented in the current repository:

- deterministic demo and live OpenAI Responses API paths;
- deterministic demo and live Cal.com booking paths;
- mocked provider integration tests for external HTTP behavior;
- automated backend tests and frontend production-build validation in CI.

Planned production-oriented capabilities include:

- voice-provider integration;
- PostgreSQL persistence;
- Redis-backed session state;
- OAuth / OIDC;
- RAG for approved clinic FAQs;
- structured observability and tracing;
- Terraform infrastructure;
- managed production secrets;
- formal healthcare privacy and compliance controls.

## Summary

The central architectural decision is to keep the AI model as one replaceable capability inside a larger application rather than letting it become the application architecture itself. FastAPI owns the system boundary, service abstractions isolate external providers, the frontend remains credential-free, and the cloud design supports incremental growth toward a secure and scalable production deployment.