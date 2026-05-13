# Mini-Headway

A small clone of how a patient/provider/insurance/scheduling system can fit together. Two layers:

- **Backend** — FastAPI + SQLAlchemy + SQLite, organized into four modules: `patient`, `provider`, `insurance`, `scheduling`.
- **Frontend** — Vite + React + Tailwind. Provider sees their day, can navigate prev/next day, can schedule new appointments (gated on readiness), and confirm scheduled sessions (gated on confirmability).

## Setup

```bash
make dev
```

That installs both packages, seeds the SQLite database, and boots the backend on `:8000` and the frontend on `:5173` in parallel.

Other targets:

- `make install` — install deps only
- `make seed` — drop the DB and reseed
- `make test` — backend smoke tests
- `make typecheck` — `mypy` + `tsc --noEmit`
- `make clean` — wipe DB, venv, node_modules

Open <http://localhost:5173> to see the app.

## Your task

You're picking up a bug report from a Headway provider, Dr. Adams.

> "Something's off with **Maya Patel**. The day view says she's 'Ready ✓', I can schedule her without any complaint, but every appointment I book with her fails to confirm with the same insurance error. I checked yesterday's calendar and her appointment from yesterday never got confirmed either. What's going on?"

**Step 1 — Reproduce.** Open the app, find Maya in today's day view, click in, hit Confirm. Try also using **+ Schedule appointment** to book a new session with Maya — note what happens. Check yesterday too.

**Step 2 — Investigate.** Use your AI tools however you'd normally use them. The bug is real and the fix isn't a one-liner.

**Step 3 — Fix it.** Commit your fix on a branch with a short message explaining what you did and why.

**Step 4 — When you're done with the bug, ask the interviewer for the feature task.**

You can use any AI tool you want (Claude Code, Cursor, Copilot, etc.). We're interested in how you work with them, not whether you used one.

## Layout (just for orientation)

```
backend/
├── app/
│   ├── main.py             # FastAPI app, registers routers, runs seed on first boot
│   ├── db.py               # SQLAlchemy engine, sessionmaker, Base
│   ├── deps.py             # X-User-Id dev shim
│   ├── seed.py             # Idempotent seed; `python -m app.seed --reset` to reseed
│   └── modules/
│       ├── patient/        # Patient model, readiness service
│       ├── provider/       # Provider model, session confirmability service
│       ├── insurance/      # UserInsurance, EligibilityLookup, eligibility service
│       └── scheduling/     # Appointment model, scheduling endpoints

frontend/
├── src/
│   ├── api/                # Typed fetch client
│   ├── pages/              # DayView, AppointmentDetail, PatientDetail, SchedulePage
│   └── components/         # ReadyBadge, BlockerList, ConfirmButton
```

Auth is a dev shim — every request is treated as coming from the seeded provider `Dr. Adams`. No login.
