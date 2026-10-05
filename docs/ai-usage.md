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
