# AI usage

I am building this with Claude Code. This file records how I direct it and where I overrule it. I add to it in each pull request.

## How I work with it

- Claude proposes and I decide. For each open choice it gives options with their cost and a recommendation.
- It changes nothing until I say so. Reading and planning are free. Files, commits and pushes need my go-ahead.
- It checks facts before it states them: installed versions, library behaviour, the text of the brief.
- Each phase is one branch and one pull request. I review and merge them myself.
- Docs, commits and pull requests stay short and plain.

## Decisions so far

| Question | Claude recommended | I chose |
| --- | --- | --- |
| Backend | FastAPI with SQLite | Same |
| Hosting | My own server with Dokploy | Same |
| Login | No login, listed as a cut | One shared HR login |
| Currencies | Fixed rates to USD | Same |
| Salary history | Keep each change | Same |
| Pull requests | Four, one per phase | Same |
| Commit footers naming Claude | Leave them out and keep this log | Same |

## Checks Claude ran

- Read the whole brief before planning.
- Read SQLite's docs before relying on `median()`. The function needs a build option that is off by default, so the plan uses window functions.
- Listed the Python versions uv offers and took the newest stable one.
- Fetched the ECB rates for 2026-10-05 for the fixed rate table. The source is named in the code.
- Replaced httpx with httpx2 after the first test run printed a Starlette deprecation warning.
- Timed the API against the 10,000 seeded employees. The numbers are in the architecture notes.

## Calls Claude made while building

These fell inside the agreed plan, so Claude decided them and recorded them here.

- The API sits under `/api` so its paths do not clash with page addresses.
- Insights show USD only. Local-currency figures per country are left out.
- Country and hire date stay fixed after a person is added.
- The seed uses eight countries whose currencies all have two decimal places.
- A salary change cannot be dated in the future or before the previous change.
- The app creates its tables at startup. There is no migration tool yet.
