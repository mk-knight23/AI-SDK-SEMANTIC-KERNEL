# AI-SDK-SEMANTIC-KERNEL

Plugin-first enterprise copilot runtime with structured orchestration.

## Current Features

- Shared mission routing and skill registry.
- FastAPI service and CLI runner.
- Semantic Kernel initialization path.
- Environment-safe dependency handling.
- Docker, CI, pytest contract tests, and skill documentation.

## Existing Runtime Flow

1. A user sends a mission through the CLI or `POST /run`.
2. The shared Agents Army router scores the mission against agent skills.
3. The adapter selects a primary agent and support agents.
4. The Microsoft Semantic Kernel integration validates the framework-specific execution path.
5. The response returns routing, support agents, result text, and verification notes.

## SDK-Specific Implementation

Initializes a Semantic Kernel instance and returns rendered mission instructions.

## Repository Structure

- `app.py`: framework adapter and mission execution entrypoint.
- `api.py`: FastAPI health and run endpoints.
- `runner.py`: local CLI demo runner.
- `core/agents_army_core/`: shared routing, mission models, registry, and instruction rendering.
- `tests/`: contract tests for routing and verification behavior.
- `.github/workflows/ci.yml`: automated pytest checks.
- `Dockerfile`: container packaging for API deployment.
- `SKILLSET.md`: skills represented by this SDK adapter.

## Run Locally

```bash
python3 -m pip install -r requirements.txt
python3 runner.py --mission "build secure api, add tests, and deploy"
```

## Run As An API

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/run \
  -H "content-type: application/json" \
  -d '{"mission":"secure audit and deploy an AI workflow"}'
```

## Test

```bash
python3 -m pytest
```

## Required Skill Set

See `SKILLSET.md` for the full skill matrix. At a high level this repository demonstrates:

- Microsoft Semantic Kernel integration.
- Agent routing and mission planning.
- API design with clear input/output contracts.
- CI-backed verification.
- Secure environment-based configuration.

## Upgrade Roadmap

- Add plugins for search, deployment, and repository operations.
- Wire planner/service connectors through environment configuration.
- Add enterprise copilot scenarios with approval and audit trails.

## Clean Repository Policy

Generated files such as `__pycache__/`, `.pytest_cache/`, local `.env` files, and dependency folders are ignored. Source, docs, tests, and deployment assets are intentionally kept in the repository.
