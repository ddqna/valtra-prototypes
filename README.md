# Valtra Adaptive Operator Companion — Interactive Prototype Concepts

Aalto University Product Development Project (sponsor: Valtra / AGCO).
Two exploratory, clickable research prototypes for usability testing:

- **Prototype A — Skill Tree: Learn by Doing** (A0 → A4): discover a function by task, learn it, practise it in a safe simulation, return to work.
- **Prototype B — Explain & Recover** (B1 → B4): request help in task context, confirm or correct the issue, see what to check, resume or get further help.

> Research prototype only. All machine data, training content and checks are **simulated or placeholders**. This is **not official Valtra functionality** and is not connected to any machine.

## View the clickable prototype

- **Online:** GitHub Pages link (added once Pages is enabled).
- **Locally:** download the repo and open `docs/index.html` in any browser. No install or internet needed (without internet the text falls back to a system font).

The screens are 1280 × 800 and scale to fit the window. Every page starts fresh, like a new screen on the tractor display.

## Files

| File | Screen |
|---|---|
| `prototypes/Main.dc.html` | Prototype launcher |
| `prototypes/A0-Home.dc.html` | A0 · Tractor screen (entry / return) |
| `prototypes/A1-Explore.dc.html` | A1 · Explore your skills |
| `prototypes/A2-Learn.dc.html` | A2 · Learn a capability |
| `prototypes/A3-Practice.dc.html` | A3 · Guided practice |
| `prototypes/A4-Complete.dc.html` | A4 · Practice completed |
| `prototypes/B1-Task.dc.html` | B1 · Request help (task screen) |
| `prototypes/B2-Confirm.dc.html` | B2 · Confirm the issue |
| `prototypes/B3-Checks.dc.html` | B3 · What to check |
| `prototypes/B4-Resolve.dc.html` | B4 · Resolved / further help |
| `prototypes/canvas.json` | Canvas layout and design notes |

The `.dc.html` files in `prototypes/` are the editable sources (Claude Design canvas format, 1280 × 800 landscape).

| Folder | What it is |
|---|---|
| `prototypes/` | Editable screen sources — change things here |
| `docs/` | Generated standalone site (served by GitHub Pages) — don't edit by hand |
| `tools/dc-standalone.js` | Small runtime that renders the sources in a plain browser |
| `tools/build_standalone.py` | Rebuilds `docs/` from `prototypes/` |
| `tools/test_flows.py` | Clicks through both flows in a headless browser (42 checks) |

After editing a source file:

```bash
python3 tools/build_standalone.py      # regenerate docs/
python3 tools/test_flows.py            # optional: check both flows still work (needs Playwright)
```

## Editing

- Headlines and labels are plain markup in each file.
- Lists that change with the scenario (practice questions, feedback, issue choices, checks, support options) live in the `scenario()` block at the top of the script in `A3-Practice`, `B2-Confirm`, `B3-Checks` and `B4-Resolve`.
- Screens link to each other with plain `<a href="…dc.html">` links.
- Shared styles (colours, buttons, chips) are repeated in the `<style>` block of every file.

## Marking conventions

- Yellow dashed chip: simulated data.
- Grey dashed chip or box: placeholder awaiting verified Valtra documentation.

## Verify before operator testing

- Real headland-sequence behaviour, setup and terminology (Valtra documentation).
- The three checks in B3 and their reasons.
- Where the function actually lives in SmartTouch (A3, step 3).
- The correct support route for B4 (no contacts are included).
- Replace the illustrative headland scenario with the verified field incident.
