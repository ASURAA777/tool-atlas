# Tool Atlas

[Live case study](https://tool-atlas-research.asura777.chatgpt.site) · [Source repository](https://github.com/ASURAA777/tool-atlas)

The hosted case study is public and can be opened by reviewers.

For architecture, setup, pipeline behavior and verification details, read the [implementation and working guide](IMPLEMENTATION.md).

An evidence-first case study of 100 requested app integrations. The standalone HTML page explains the findings, lets a reviewer inspect field-level sources, and separates agent checks from pending human verification.

## Run locally in under a minute

Requires Python 3.11 or newer. No third-party packages or API keys are needed to reproduce the checked-in report.

```sh
python research.py replay
python research.py sample
python -m unittest discover -s tests -v
python -m http.server 8000 --directory dist
```

Open http://localhost:8000. `dist/index.html` is also self-contained and can be opened directly; separate download links require the adjacent files. Deploy `dist/` to any static host.

## Research a fresh app or all 100

Set `OPENAI_API_KEY` and `RESEARCH_MODEL` in your local environment. Choose a Responses API model supporting the `web_search` tool. Never put a key in source or the HTML.

```sh
python research.py research --ids 1 --run trial
python research.py research --run full-study
```

The runner performs two model requests per app: source discovery/extraction, then an independently prompted source verification. It preserves raw responses, first-pass rows, checks and revised rows in `work/<run>/`. The same command resumes completed work. `--refresh` creates a new timestamped run so earlier evidence remains intact. Costs depend on your model and search usage; begin with one app. The live API mode was implemented but not executed in this environment because no research API credential was supplied. This limitation is visible in the report.

Review fresh results before replacing `data/research.json`; run `replay` after promoting them. Live results are intentionally not auto-published.

Technical API reference: [OpenAI Responses](https://developers.openai.com/api/reference/resources/responses/methods/create) and [web search](https://developers.openai.com/api/docs/guides/tools-web-search?api-mode=responses).

## What actually ran for this study

- Codex research agents searched and read primary vendor documentation, resolved product identities, and produced structured claims for the 100-app set.
- Source-backed findings were saved in a frozen first-pass dataset before a separate agent checked a targeted sample.
- The audit ledger identifies supported, corrected and unresolved fields. The report derives its before/after support ratios from those actual judgments. They are **not** a human accuracy estimate.
- The Python pipeline validates records, computes aggregates, generates JSON/CSV and builds the single HTML page. URL checks record retrieval results separately from semantic checks.
- Human checks and authenticated app endpoint probes remain pending. No paid app subscriptions were purchased.
- Composio SDK/MCP was not used in the executed pass. Public documentation research did not require access to connected private app data. A future authenticated-probe phase could use Composio; that integration is not claimed here.

## Recheck documentation links

```sh
python research.py check-links --workers 6
python research.py replay
```

This checks public HTTPS URLs with bounded downloads, timeouts and redirect validation, then stores HTTP status, timestamp, sampled content hash and errors. An HTTP 200 does **not** establish factual correctness. A blocked URL does **not** establish that the vendor API is gated. Some docs need a browser, so review retrieval errors separately.

## Human verification

`python research.py sample` creates a reproducible worksheet of two apps per category (seed `20261123`). Check five fields per app: auth, access, API surface, MCP and verdict. Read the linked primary sources yourself; record supported, incorrect or unresolved judgments with the source URL, reviewer and note.

The HTML offers the same sample filter, local review controls inside each app and a JSON export. These controls store notes only in the reviewer's browser. They do not modify the deployed dataset or automatically certify a human score. A complete sample contains 100 field judgments. Count unresolved judgments in the denominator. Recompute and document metrics only after a real reviewer completes the work.

## Reading the data

Each app records category, one-line job, auth methods, prototype and production access separately, API style and breadth, MCP provenance, buildability, blocker, confidence and field-level evidence.

- `ready`: a documented free/trial/local prototype path exists for a useful scope; production can still have restrictions.
- `conditional`: a material paid/admin/review/partner gate, or unconfirmed eligibility, affects implementation or distribution.
- `unknown`: insufficient evidence or unresolved vendor identity.
- `blocked`: explicit evidence prevents the proposed scope; never inferred merely from a failed search.

MCP `not_verified` is not an absence claim. Confidence is an agent judgment, not a calibrated probability. Auth counts are multi-label and do not sum to 100. Basic refers to HTTP transport; a key may be carried in Basic or Bearer. GraphQL and REST can coexist.

## Files

- `data/apps.json`: exact assignment inventory.
- `data/first-pass.json`: frozen research before the sample review.
- `data/research.json`: current research with source URLs and caveats.
- `data/verification.json`: second-pass judgments and correction provenance.
- `data/link-checks.json`: HTTP reachability results, not factual verification.
- `data/research-logs/`: original research logs when available.
- `research.py`: CLI, research runner, source checks and human sampling.
- `src/build.py`, `src/template.html`: report generation and interface.
- `tests/test_pipeline.py`: integrity, sampling and parsing checks.
- `dist/`: deployable page plus machine-readable exports.

## Explain it in the interview

The core decision is whether an app has a usable credential path **for the intended scope**. Public documentation, a free sandbox, a personal token and public multi-tenant distribution are different facts. The pipeline preserves these differences instead of collapsing them into “API available.” Its strongest trust mechanism is a traceable claim plus a visible unresolved state—not an impressive but unsupported accuracy percentage.

The next improvements are human audits, authenticated read-only smoke tests for a small set, vendor-identity allowlists for the live runner, and scheduled rechecks of auth and access rules.
