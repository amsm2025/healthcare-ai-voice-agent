# AWS Deployment Architecture

This document describes a production-oriented AWS deployment path for the Healthcare AI Voice Agent. The current repository is a portfolio/demo implementation; the architecture below shows how the containerized backend and static frontend can evolve into a scalable cloud deployment.

> This is an architectural deployment guide, not a claim that the demonstration environment is currently operating as a production healthcare system. Handling real PHI would require formal security, privacy, compliance, operational, and legal review.

## Deployment goals

The AWS design aims to provide:

- repeatable container deployment;
- HTTPS at the public boundary;
- stateless horizontal scaling for the API;
- managed secret storage;
- centralized logging and metrics;
- separation of frontend and backend workloads;
- a path to managed persistence and caching;
- infrastructure suitable for automated CI/CD and future infrastructure as code.

## Target topology

```text
Users
  |
  v
Route 53
  |
  v
CloudFront + ACM
  |
  +------------------------------+
  |                              |
  v                              v
S3 static React SPA        Application Load Balancer
                                 |
                                 v
                         ECS Service / Fargate
                         +--------------------+
                         | FastAPI Task       |
                         | FastAPI Task       |
                         +--------------------+
                           |       |       |
                           |       |       +--> Cal.com
                           |       +----------> LLM provider
                           |
                           +--> RDS / PostgreSQL
                           +--> ElastiCache / Redis
                           +--> Secrets Manager
                           +--> CloudWatch
```

The frontend and backend are intentionally deployed differently: React is compiled into static assets and distributed through S3/CloudFront, while FastAPI runs as stateless containers on ECS/Fargate.

## AWS service responsibilities

| AWS service | Responsibility |
| --- | --- |
| Amazon ECR | Stores versioned backend container images |
| Amazon ECS | Orchestrates application tasks and services |
| AWS Fargate | Runs containers without managing EC2 hosts |
| Application Load Balancer | Routes HTTPS/API traffic and performs health checks |
| Amazon S3 | Hosts compiled React static assets |
| Amazon CloudFront | CDN and public frontend delivery layer |
| Amazon Route 53 | DNS management |
| AWS Certificate Manager | TLS certificates |
| AWS Secrets Manager | Stores API credentials and application secrets |
| Amazon CloudWatch | Application logs, metrics, alarms and operational visibility |
| Amazon RDS for PostgreSQL | Future durable relational persistence |
| Amazon ElastiCache for Redis | Future session/cache layer |

## Container build

Build the FastAPI backend from the repository root:

```bash
docker build -t healthcare-ai-voice-agent ./backend
```

For production releases, prefer immutable version tags rather than relying only on `latest`:

```bash
docker tag healthcare-ai-voice-agent:latest \
  ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/healthcare-ai-voice-agent:1.0.0
```

## Push to Amazon ECR

Create an ECR repository and authenticate Docker with the AWS CLI. A typical authentication flow is:

```bash
aws ecr get-login-password --region REGION | \
  docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com
```

Push the versioned image:

```bash
docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/healthcare-ai-voice-agent:1.0.0
```

In an automated pipeline, the image tag can use a release version or Git commit SHA to provide traceability between source and deployed artifacts.

## ECS cluster and service

Create an ECS cluster and a Fargate service for the FastAPI backend.

A reasonable demonstration starting point is:

| Setting | Starter value |
| --- | --- |
| Launch type | Fargate |
| CPU | 0.5 vCPU |
| Memory | 1 GB |
| Container port | 8000 |
| Desired task count | 1 for demonstration |
| Health endpoint | `/health` |

A production deployment should normally run multiple tasks across Availability Zones and configure service autoscaling.

## Task definition

The ECS task definition should define:

- the ECR image URI;
- container port `8000`;
- CPU and memory limits;
- CloudWatch log configuration;
- non-sensitive runtime configuration;
- Secrets Manager references for credentials;
- an IAM task role containing only permissions required by the application.

The container should remain stateless. Durable application data should live in managed external services rather than inside the task filesystem.

## Networking

A production-oriented VPC design should separate public and private responsibilities.

```text
Internet
   |
Public subnets
   |
Application Load Balancer
   |
Private subnets
   |
ECS Fargate tasks
   |
Private data services
```

The load balancer can be internet-facing while ECS tasks remain in private subnets. Security groups should permit only the minimum required traffic between components.

For outbound access to external LLM and scheduling APIs, private tasks require an appropriate controlled egress path such as a NAT gateway or another approved network design.

## Application Load Balancer

The ALB provides the public API entry point and distributes requests across healthy Fargate tasks.

Recommended configuration includes:

- HTTPS listener on port 443;
- ACM-managed certificate;
- target group forwarding to container port 8000;
- `/health` target health check;
- HTTP-to-HTTPS redirection;
- appropriate idle timeout and connection settings based on application behavior.

## Frontend deployment

The React/Vite frontend should be compiled for production rather than running the development server in ECS.

```bash
cd frontend
npm ci
npm run build
```

Deploy the generated static assets to S3 and serve them through CloudFront. Benefits include low operational overhead, CDN caching, TLS support, and independent frontend/backend deployments.

The frontend should receive the backend API base URL through build/runtime configuration rather than hard-coded local addresses.

## Secrets and configuration

Do not commit secrets to Git and do not place sensitive credentials directly into container images.

Examples of secrets include:

- `OPENAI_API_KEY` or another approved LLM-provider credential;
- `CALCOM_API_KEY`;
- future database credentials;
- authentication signing secrets.

Store sensitive values in AWS Secrets Manager and inject them into the ECS task at runtime. Use IAM roles and least-privilege policies to restrict access.

## Persistence and session state

The demonstration can operate without durable healthcare records. If persistence is introduced later, separate data responsibilities explicitly:

- **RDS/PostgreSQL** — durable relational application data;
- **Redis/ElastiCache** — ephemeral session state, caching, rate-limit counters or short-lived workflow state;
- **S3** — approved object storage where appropriate.

Do not use the Fargate task filesystem as durable storage.

## Scaling and availability

Because API tasks are intended to remain stateless, the ECS service can scale horizontally.

A production design can use:

- multiple Fargate tasks;
- deployment across multiple Availability Zones;
- ECS service autoscaling;
- ALB request distribution;
- CPU, memory or request-based scaling signals;
- managed database backups and Multi-AZ options where required.

Scaling decisions should be based on measured traffic, latency, external-provider quotas and cost rather than arbitrary task counts.

## Observability

CloudWatch should provide a minimum operational baseline:

- structured application logs;
- ECS CPU and memory metrics;
- ALB request count and latency;
- target health;
- HTTP 4xx/5xx rates;
- deployment failures;
- alarms for meaningful service degradation.

Production systems should also use correlation/request IDs and avoid logging secrets or unnecessary sensitive healthcare information.

## CI/CD direction

A future GitHub Actions deployment workflow can:

```text
Push / merge to main
       |
       v
Run automated tests
       |
       v
Build backend container
       |
       v
Push versioned image to ECR
       |
       v
Register new ECS task revision
       |
       v
Update ECS service
       |
       v
Wait for health checks
```

Production pipelines should use short-lived AWS credentials through an approved identity mechanism rather than long-lived AWS access keys stored in the repository.

## Deployment safety and rollback

A reliable deployment process should preserve the previous known-good task definition revision. If a new revision fails health checks or introduces unacceptable errors, the ECS service can be returned to the previous revision.

Additional production options include rolling deployment controls, deployment circuit breakers, alarms, and blue/green deployment strategies when justified by service criticality.

## Security considerations

Before handling real healthcare data, the AWS environment would require a dedicated security and compliance design. Areas to address include:

- formal HIPAA and applicable local privacy/compliance review;
- confirmation that every service/provider used for PHI is appropriate for the intended compliance scope;
- BAAs/DPAs where required;
- least-privilege IAM;
- encryption in transit and at rest;
- private networking for backend/data services where appropriate;
- managed secrets and credential rotation;
- authentication and authorization;
- audit logging;
- data classification and minimum-necessary collection;
- retention and deletion controls;
- backup and recovery requirements;
- vulnerability management;
- threat modeling and penetration testing;
- incident response procedures.

The portfolio project intentionally does not claim that these controls are fully implemented.

## Infrastructure as code roadmap

The current document describes the AWS design conceptually. A future Terraform implementation can define:

- VPC, subnets and routing;
- security groups;
- ECR repository;
- ECS cluster, task definition and service;
- ALB, target groups and listeners;
- S3 and CloudFront;
- IAM roles and policies;
- Secrets Manager resources;
- CloudWatch log groups and alarms;
- RDS and ElastiCache when persistence is introduced.

This would make the environment reproducible, reviewable and easier to promote between development, staging and production environments.
