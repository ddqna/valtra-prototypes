# Valtra Adaptive Operator Companion — Skill Tree prototype

Aalto University Product Development Project (sponsor: Valtra / AGCO).
A clickable research prototype for usability testing. **Help** is where an operator discovers what a control does; the **Skill Tree** picks up from there with a task-based learning path: understand it, practise it safely while stationary, then apply it during real work.

> Research prototype only. All machine data, help texts, training content and the QR code are **simulated or placeholders**. This is **not official Valtra functionality** and is not connected to any machine.

## View it

- **Online (current version, v2):** https://ddqna.github.io/valtra-prototypes/
- **Online (v1, Skill Tree + Explain & Recover):** https://ddqna.github.io/valtra-prototypes/v1/
- **Locally:** download the repo and open `docs/index.html` (or `docs/v1/index.html`) in any browser. No install needed; without internet the text falls back to a system font.

Screens are 1280 × 800 and scale to fit the window. Every page starts fresh, like a new screen on the tractor display.

## Versions

| Version | What it is | Where |
|---|---|---|
| **v2** (current) | Skill Tree only, entered from Help mode on the tractor screen | `main` branch · tag `v2-skill-tree-help` · site root |
| **v1** | Two separate prototypes: Skill Tree, and Explain & Recover | tag `v1-two-prototypes` (full source as it was) · `archive/v1-two-prototypes/` · site `/v1/` |

To see v1's source on GitHub, switch the branch/tag menu to `v1-two-prototypes`.

## The demo flow (v2)

1. **Tractor screen → Help.** The screen stays visible and its controls pause (dashed outlines).
2. **Tap a control.** A help card shows a short description, **More info**, a **QR code**, and **Learn**. Nothing activates.
3. **Learn** opens that control's **learning path** in the Skill Tree (only *Headland* has one in this prototype; other controls open the Skill Tree overview).
4. **Understand → Practise (stationary simulation) → Apply at work.**

A pulsing blue outline marks the next tap, for demos. Turn it off for operator tests so it doesn't steer participants: in the canvas, select an artboard → Tweaks → Demo → `showHints`; in the source, set `showHints` default to `false` in each file's `data-props`.

## Files

| Path | What it is |
|---|---|
| `prototypes/Main.dc.html` | Launcher |
| `prototypes/A0-Home.dc.html` | Tractor screen with Help mode |
| `prototypes/Path-Headland.dc.html` | Learning path (opened from Help → Learn) |
| `prototypes/A2-Learn.dc.html` | Step 1 · Understand |
| `prototypes/A3-Practice.dc.html` | Step 2 · Practise (stationary simulation) |
| `prototypes/A4-Complete.dc.html` | Step 3 · Apply at work |
| `prototypes/A1-Explore.dc.html` | Skill Tree overview (browse all skills) |
| `prototypes/assets/` | Images (tractor image from the team's SmartTouch screenshot, help card removed) |
| `prototypes/canvas.json` | Canvas layout and design notes |
| `archive/v1-two-prototypes/` | Frozen, built v1 site |
| `docs/` | Generated site served by GitHub Pages — don't edit by hand |
| `tools/dc-standalone.js` | Small runtime that renders the sources in a plain browser |
| `tools/build_standalone.py` | Rebuilds `docs/` from `prototypes/` and `archive/` |
| `tools/test_flows.py` | Clicks through the demo flow in a headless browser (29 checks) |

The `.dc.html` files are the editable sources (Claude Design canvas format).

## Editing

- Headlines and labels are plain markup in each file.
- Help-card names, texts and positions: the `scenario()` block at the top of the script in `A0-Home`. `h1`–`h10` are the controls in the tractor image.
- Practice questions and feedback: `scenario()` in `A3-Practice`.
- Screens link to each other with plain `<a href="…dc.html">` links.

After editing:

```bash
python3 tools/build_standalone.py      # regenerate docs/
python3 tools/test_flows.py            # optional: check the flow still works (needs Playwright)
```

## Marking conventions

- Yellow dashed chip: simulated data.
- Grey dashed chip or box, or text in [brackets]: placeholder awaiting verified Valtra documentation.

## Verify before operator testing

- Real names and Help texts for every control in the tractor image (shown as "Control A–H [name to verify]").
- Which SmartTouch control opens headland management ("Headland" is an added prototype control).
- Headland-sequence behaviour, setup and terminology (Valtra documentation).
- Where the QR code should lead.
- Wording of practice feedback, with a domain expert.
- Turn `showHints` off for unbiased tests.
