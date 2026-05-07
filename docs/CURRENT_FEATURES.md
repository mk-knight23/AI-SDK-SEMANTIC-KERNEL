# Current Feature Inventory

## Repository

- Name: `AI-SDK-SEMANTIC-KERNEL`
- SDK: Microsoft Semantic Kernel
- Positioning: Plugin-first enterprise copilot runtime with structured orchestration.

## Implemented Today

- Shared mission routing and skill registry.
- FastAPI service and CLI runner.
- Semantic Kernel initialization path.
- Environment-safe dependency handling.
- Docker, CI, pytest contract tests, and skill documentation.

## Not Yet Implemented

- Add plugins for search, deployment, and repository operations.
- Wire planner/service connectors through environment configuration.
- Add enterprise copilot scenarios with approval and audit trails.

## Verification Contract

- The local runner must complete without crashing when optional SDK credentials are missing.
- The API contract must return routing and verification fields.
- Tests must prove mission routing and a security-focused SENTINEL route.
