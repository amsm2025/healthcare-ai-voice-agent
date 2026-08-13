# AWS ECS Fargate Deployment Guide

This repository is structured so the backend can run as a container on ECS/Fargate.

## Recommended AWS services

- ECR — Docker image registry
- ECS — container orchestration
- Fargate — serverless container compute
- Application Load Balancer — HTTPS/API traffic
- Route 53 — DNS
- ACM — TLS certificate
- Secrets Manager — API keys
- CloudWatch — logs and metrics

## High-level flow

1. Build the backend image.
2. Push the image to Amazon ECR.
3. Create an ECS cluster.
4. Create a Fargate task definition.
5. Create an ECS service.
6. Attach an Application Load Balancer.
7. Add secrets through Secrets Manager.
8. Configure HTTPS with ACM.
9. Point your domain through Route 53.

## Build image

```bash
docker build -t healthcare-ai-voice-agent ./backend
```

## Tag for ECR

```bash
docker tag healthcare-ai-voice-agent:latest \
  ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/healthcare-ai-voice-agent:latest
```

## Push

Authenticate Docker to ECR using the AWS CLI, then:

```bash
docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/healthcare-ai-voice-agent:latest
```

## ECS task settings

Typical starter configuration:

- Launch type: Fargate
- CPU: 0.5 vCPU
- Memory: 1 GB
- Container port: 8000
- Desired task count: 1 for demo / portfolio
- Health check path: `/health`

For production, use multiple tasks across Availability Zones and autoscaling.

## Secrets

Do not place API keys in the task definition as plaintext environment variables.

Use AWS Secrets Manager for:
- `OPENAI_API_KEY`
- `CALCOM_API_KEY`

## Frontend

For a production portfolio deployment, the React frontend is better built as static files and hosted on:

- Amazon S3
- CloudFront

rather than running the Vite development server in ECS.
