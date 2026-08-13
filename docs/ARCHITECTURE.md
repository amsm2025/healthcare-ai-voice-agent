# Architecture

## Goal

Demonstrate how a production-oriented AI scheduling assistant can be separated into clear layers.

## Components

### 1. React frontend
Responsible for:
- user interaction;
- displaying assistant responses;
- sending requests to the backend;
- eventually hosting voice controls.

### 2. FastAPI application
Responsible for:
- HTTP/API boundary;
- validation;
- CORS;
- orchestration of AI and scheduling services.

### 3. LLM service
Responsible for:
- conversation intent;
- approved response generation;
- enforcing high-level safety behavior.

The LLM layer should never have direct database or scheduling credentials.

### 4. Safety layer
Runs before general AI behavior for obvious emergency terms.

A production healthcare implementation should use a much stronger, clinically reviewed safety design.

### 5. Scheduling service
Cal.com is abstracted behind `CalComService`.

This allows:
- vendor replacement;
- local testing;
- mock booking creation;
- external API failures to be handled independently.

## Production expansion

```text
CloudFront / CDN
       |
       v
React SPA
       |
       v
Application Load Balancer
       |
       v
ECS Fargate Tasks
  |       |       |
  |       |       +--> Cal.com
  |       +----------> LLM provider
  +------------------> PostgreSQL / RDS
              |
              +-------> Redis / ElastiCache
```

## Security considerations

Before handling real healthcare data:

- perform HIPAA / local privacy compliance review;
- execute appropriate BAAs / DPAs;
- encrypt data at rest and in transit;
- use least-privilege IAM;
- store secrets in AWS Secrets Manager;
- implement authentication and authorization;
- maintain audit logs;
- define retention and deletion policies;
- avoid sending unnecessary PHI to model providers;
- complete threat modeling and penetration testing.
