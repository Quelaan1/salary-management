# Salary management

A web tool for ACME's HR manager: keep salaries current for 10,000 employees and see how the company pays people. Built for the Incubyte engineering assessment.

## What it does

- Find people by name or email. Filter by country, department, job title or status.
- Add a person, edit their details, mark them as left.
- Change a salary with a date and a reason. Each person keeps a salary timeline.
- See headcount, total pay, and the lowest, median, average and highest salary, for the company or by country, department or job title.

## Run it

### In Docker

```bash
docker build -t salary-management .
docker run --rm -p 8000:8000 \
  -e HR_PASSWORD=pick-a-password \
  -e SESSION_SECRET=any-long-random-text \
  -e COOKIE_SECURE=false \
  -v salary-data:/data \
  salary-management
```

Open http://localhost:8000 and sign in with the password you picked. The first start seeds 10,000 employees.

`COOKIE_SECURE=false` is for plain HTTP on localhost. Leave it out behind HTTPS.

### For development

Needs [uv](https://docs.astral.sh/uv/) and Node 24.

```bash
cd backend
cp .env.example .env
uv run --env-file .env uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite passes `/api` calls to the backend on port 8000. The password is in `backend/.env`.

## Test it

```bash
cd backend && uv run pytest
cd frontend && npm test
```

Lint with `uv run ruff check .` and `npm run lint`. CI runs all of these, then builds the Docker image and starts it.

## Seed data

```bash
cd backend
uv run --env-file .env python -m app.seed --reset
```

The seed starts its random generators from fixed numbers, so each run creates the same 10,000 people.

## Documents

- [Requirements](docs/requirements.md): the goal, the scope, and what I left out and why.
- [Architecture](docs/architecture.md): shape, data, API, trade-offs and performance.
- [AI usage](docs/ai-usage.md): how I worked with Claude Code.
- [Demo script](docs/demo-script.md): the walkthrough for the video.
