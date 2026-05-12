# Setting this up in CodeSignal

Step-by-step for creating the live interview in Headway's CodeSignal workspace. Audience: the person running the interview, not the candidate.

## One-time: create the Advanced Assessment Question

1. In CodeSignal Interview, go to **Library → Questions → New Question** and pick **Advanced Assessment Question**. (Docs: <https://support.codesignal.com/hc/en-us/articles/7385597441943-Create-an-advanced-assessment-question>.)

2. **Environment**: choose an image with Python and Node available. The "Full-stack JavaScript + Python" template is fine; the universal devcontainer image also works.

3. **Pre-load the project files**. Upload everything in this repo *except* the `codesignal/` directory itself, plus skip:
   - `backend/.venv/`, `backend/__pycache__/`, `backend/mini-headway.db`
   - `frontend/node_modules/`, `frontend/dist/`
   - `.git/`
   - lockfiles are OK to include (`backend/uv.lock`, `frontend/package-lock.json`)

   Total source is ~224 KB across ~80 files — well under CodeSignal's 1 MB pre-upload cap.

4. **Bootstrap script**: paste the contents of `codesignal/setup.sh` into CodeSignal's "container init" / "session setup" field (the exact label depends on which CodeSignal template you start from). This installs `uv`, installs deps, seeds the DB, and starts both servers in the background.

5. **Preview port**: set the question's preview to **port 3000** — CodeSignal only exposes one preview port per question. The setup script binds Vite to 3000 (overriding its 5173 default) so the candidate's browser panel works.

6. **Task description**: paste the contents of the repo's `README.md` "Your task" section as the question prompt. Don't paste the layout section — let the candidate explore.

7. **Save the question** and run it yourself end-to-end as a fake candidate before going live. You want to confirm:
   - Setup script finishes in <60 seconds.
   - Preview panel loads the DayView with 5 appointments and the "Ready ✓" badges.
   - Maya Patel's appointment shows the contradiction (Ready ✓ in the badge, Confirm errors with the blockers).
   - A healthy appointment confirms cleanly.

## At interview time

1. Schedule the session and send the candidate the join link. Mention in the prep email:
   - "You'll have ~60–90 minutes."
   - "Use whatever AI tool you normally use — Copilot is pre-installed; for Claude Code or others, sign in via the terminal."
   - "The environment takes ~60 seconds to boot on session start."

2. When the candidate joins, give them ~5 minutes to read the README and click around the app, then start the timer.

3. The bug is in the data and the cross-module read pattern. The fix has multiple valid shapes. Care more about *how* they navigate with AI than about *which* fix they pick. Notes to look for:
   - Did they reproduce the symptom before reading code?
   - Did they trace both endpoints to their services before forming a hypothesis?
   - Did they ask AI a precise question, or a vague one?
   - Did they verify the fix end-to-end (UI, not just unit tests)?

4. When they finish the bug, hand them one of the three feature tasks sketched in `~/.claude/plans/serene-percolating-sutton.md` (or `~/Downloads/mini-headway-plan.md`):
   - **New readiness check — emergency contact** (default; touches all layers)
   - **Readiness drilldown page** (frontend-heavy)
   - **Bulk confirm** (backend-heavy)

   Pick based on what the candidate's role weights, or what they did well/poorly during the bug fix.
