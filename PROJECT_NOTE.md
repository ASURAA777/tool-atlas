# Tool Atlas — Project Note

**Live case study:** https://tool-atlas-research.asura777.chatgpt.site
**Source repository:** https://github.com/ASURAA777/tool-atlas

## What this is

Tool Atlas researches all 100 assigned apps and answers, for each one: what auth it
uses, whether a developer can self-serve credentials or needs a paid/admin/partner
gate, what its API surface looks like, whether it has an existing MCP, and whether
it could become an agent toolkit today. Every finding links to the primary vendor
documentation that supports it.

## The headline patterns

- **58 of 100 apps** are build-now ready (a free, trial or local credential path
  exists); **40** carry a material access condition (paid plan, admin approval,
  app review or partner gate); **2** remain unresolved.
- **OAuth2** is the most common auth method (67 apps), but it rarely travels alone;
  most apps mix OAuth2 with API keys or tokens for service-to-service use.
- **57 apps** already have official MCP documentation. Checking for an existing MCP
  before building a custom integration is the single highest-leverage step.
- The most common blocker isn't "no API," it's a **distribution or admin gate**
  (app review, workspace admin consent, paid-plan requirement) that sits on top of
  an otherwise-working API.

## How it was built

A Python research pipeline (standard library only, no paid dependencies) drives
two agent passes per app: a discovery/extraction pass that searches official docs,
and an independent verification pass that re-challenges the first answer, checking
auth deprecations, vendor identity, and free-vs-paid eligibility rather than
assuming the first pass was right. A frozen first-pass dataset and a correction
ledger are both kept in the repo, so every correction is traceable.

## Verification, honestly

A targeted 15-app / 75-field agent audit found support moved from **76% (57/75)**
before the second-look pass to **88% (66/75)** after it, a measured before/after
on a checked sample, not a claim about the full 100 apps. Human review is explicitly
marked pending in the report itself: a reproducible 20-app worksheet is included
and no fabricated human score is shown anywhere.

## How to run it

Requires Python 3.11+. No packages, accounts or API keys needed to reproduce the
checked-in report.

```
python research.py replay
python -m unittest discover -s tests -v
python -m http.server 8000 --directory dist
```

Then open `http://localhost:8000`. `dist/index.html` is also self-contained and can
be opened directly in a browser with no server at all; the separate CSV/JSON
download links just need the rest of `dist/` alongside it.

Fresh research against live docs (optional, needs `OPENAI_API_KEY` and
`RESEARCH_MODEL`, not required to review this submission):

```
python research.py research --ids 1 --run trial
```

## What's in this folder

- `dist/` — the deployable static site (open `dist/index.html` directly, or serve
  the folder). No build step, no API keys needed to reproduce it.
- `data/` — the research dataset, first-pass snapshot, and verification ledger.
- `research.py`, `src/` — the pipeline: validation, the agent research/verify
  runner, link-checking, and the report builder.
- `tests/` — automated pipeline tests (`python -m unittest discover -s tests`).
- `README.md` / `IMPLEMENTATION.md` — full run instructions and the complete
  write-up of architecture, methodology and limitations.
