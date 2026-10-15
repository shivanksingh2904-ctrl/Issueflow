# IssueFlow

Production-style project management and issue tracking REST API (Jira-style), built with
FastAPI, async SQLAlchemy 2.0 and PostgreSQL 16.

> Work in progress: Phase 1 (scaffold). Full documentation lands in Phase 9.

## Quick start

```bash
cp .env.example .env
uv sync                 # also writes uv.lock on first run; commit it
make dev                # http://localhost:8000/api/v1/docs
make test
make lint
```

Or with Docker: `make up`.
