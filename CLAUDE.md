# PatentIQ

**Project:** PatentIQ (Patent Analysis SaaS)
**SDK Focus:** Patent search and intelligence platform
**Tech Stack:** Astro 5 + Flask + AWS ECS

## MANDATORY WORKFLOW

1. Superpowers → Brainstorm → Plan → TDD
2. ECC → /plan → /tdd → /code-review → /security-scan
3. UI/UX Pro Max → Apply design system
4. Claude-Tips → /dx:handoff before end of session

## AGENTS TO USE

- /architect for system design
- /tdd-guide for test-first implementation
- /security-reviewer before API key usage

## CURRENT SPRINT: Week 1

- [x] Scaffold Astro 5 frontend
- [x] Scaffold Flask backend
- [x] Create Docker containers
- [x] Setup CI/CD pipeline
- [ ] Deploy to AWS ECS

## Deployment Target

AWS ECS with Application Load Balancer

### AWS ECS Deployment Steps

1. **Create ECR Repositories:**
   ```bash
   aws ecr create-repository --repository-name patentiq-frontend
   aws ecr create-repository --repository-name patentiq-backend
   ```

2. **Build and Push Images:**
   ```bash
   # Get login token
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

   # Build images
   docker build -t patentiq-frontend ./frontend
   docker build -t patentiq-backend ./backend

   # Tag and push
   docker tag patentiq-frontend:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/patentiq-frontend:latest
   docker tag patentiq-backend:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/patentiq-backend:latest
   docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/patentiq-frontend:latest
   docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/patentiq-backend:latest
   ```

3. **Create ECS Cluster:**
   ```bash
   aws ecs create-cluster --cluster-name patentiq-cluster
   ```

4. **Create Task Definitions** (see `infrastructure/ecs/task-definition-frontend.json` and `task-definition-backend.json`)

5. **Create Application Load Balancer** with target groups for frontend (port 4321) and backend (port 5000)

6. **Create ECS Services** using Fargate launch type

## API Keys (Doppler)

None required for basic setup
