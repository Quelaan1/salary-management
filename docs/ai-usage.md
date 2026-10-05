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
- Opened the app against the seeded data and saw four people named Aarav Almeida. The seed now takes names from Faker, with a locale per country.
- Accented names exposed a search gap: SQLite lowercases ASCII letters only. The connection now uses Python's lower().
- Generated the current Vite template in a scratch folder to copy its config, and read the MUI 9 and React Router 8 upgrade notes before writing components.
- Type-checked, linted and ran the tests at each UI commit.
- Opened each screen in a browser against the seeded data and saved a salary change.
- Served the built UI from FastAPI on my machine and opened a page address to confirm a reload works.
- Docker was not running on my machine, so CI builds the image, starts a container and checks the API and the UI.
- Checked the live app after the deploy: sign-in, the 10,000 employees, insights, a page address and the HTTPS certificate.

## Calls Claude made while building

These fell inside the agreed plan, so Claude decided them and recorded them here.

- The API sits under `/api` so its paths do not clash with page addresses.
- Insights show USD only. Local-currency figures per country are left out.
- Country and hire date stay fixed after a person is added.
- The seed uses eight countries whose currencies all have two decimal places.
- A salary change cannot be dated in the future or before the previous change.
- The app creates its tables at startup. There is no migration tool yet.
- Filters, sort and page live in the URL under the API's own parameter names.
- Dropdowns are native selects and suggestions use a native datalist. There is no date picker or autocomplete library.
- Insights draw a bar per group inside the table. There is no chart library.
- The container runs as a non-root user and has a health check.
- The live address is a generated sslip.io name. It needed no DNS change and is easy to replace.
