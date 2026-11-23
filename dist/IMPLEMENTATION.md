# Tool Atlas: implementation and working guide

[Live case study](https://tool-atlas-research.asura777.chatgpt.site) | [GitHub repository](https://github.com/ASURAA777/tool-atlas)

This guide explains the delivered project, how to run it, how its components work together, and which parts were actually verified. The research snapshot is dated **23 November 2026**; vendor access policies can change.

## 1. What the project does

Tool Atlas helps a product or integration team decide which of 100 apps can support a useful integration, what credentials are needed, and which access restrictions need investigation. It turns vendor documentation into a searchable case study with field-level evidence and downloadable data.

The project separates prototype access from production access. A free developer account does not necessarily permit a public, multi-customer integration. Similarly, a documented MCP server may cover only a small part of an app.

The delivered snapshot contains 100 apps across 10 categories: 58 marked ready, 40 conditional and 2 unknown. It records 57 apps with documented official MCP and 276 distinct evidence URLs. These are documentation-based findings, not successful authenticated integration tests.

## 2. Architecture and technology choices

```text
Assignment inventory: data/apps.json
           |
           v
Research and official documentation discovery
           |
           v
First-pass records ---> Verification and correction ledger
           |                         |
           +-------------------------+
                         |
                         v
              data/research.json
                         |
             validate + normalize + aggregate
                         |
                         v
        src/build.py + src/template.html
                         |
                         v
     dist/index.html + JSON + CSV + source.zip
                         |
                         v
          Static hosting / local browser
```

- **Python 3.11 or newer:** command-line research, validation, sampling, link checks and builds. Only the standard library is required.
- **HTML, CSS and JavaScript:** the report, filters, evidence dialogs and browser-local review notes. There is no frontend build dependency.
- **JSON:** source data, provenance and audit records.
- **CSV:** a spreadsheet-friendly export.
- **Static hosting:** serves generated files without a database or application server.
- **Optional OpenAI Responses API:** the standalone fresh-research command uses a model with web search. Replaying the delivered dataset requires neither credentials nor model calls.

This design makes the submitted findings inspectable and reproducible without installing a large application stack.

## 3. Repository map

```text
tool-atlas/
  README.md                    Quick start and submission overview
  IMPLEMENTATION.md            This guide
  research.py                  CLI and research pipeline
  data/
    apps.json                  Assignment inventory
    first-pass.json            Frozen pre-review research
    research.json              Current report records
    verification.json          Field judgments and corrections
    link-checks.json            HTTP retrieval results
    research-logs/             Available original research logs
  src/
    build.py                   Aggregation and output generation
    template.html              Report markup, styling and interactions
  tests/
    test_pipeline.py           Pipeline integrity tests
  dist/                        Generated, deployable outputs
  work/                        Local research runs and review worksheets
```

`work/`, environment files, Python caches and ZIP archives are excluded from Git. The generated source ZIP contains the code, documentation, data and tests needed to rebuild the report. The local Downloads project copy also includes generated report files.

## 4. Run the project locally

Open PowerShell in the project folder. For the Downloads copy:

```powershell
Set-Location "$env:USERPROFILE\Downloads\tool-atlas"
python --version
python research.py replay
python -m unittest discover -s tests -v
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000` in a browser. Stop the server with `Ctrl+C`. If Python is available through the Windows launcher instead, use `py` in place of `python`.

`replay` reads the checked-in research, validates it and regenerates the outputs. It does not perform fresh web research. The HTML can also be opened directly, but serving the entire `dist` folder is preferable for adjacent download files.

## 5. How the data is represented

Each app record contains:

| Field | Purpose |
| --- | --- |
| `id`, `name`, `category` | Stable inventory identity and grouping |
| `description` | One-line explanation of the app |
| `auth` | Documented authentication methods; multiple methods are allowed |
| `access.sandbox` | Prototype or development access |
| `access.production` | Production requirements and restrictions |
| `access.gate` | Access classification used for summary grouping |
| `api.style`, `api.breadth` | API interfaces and useful scope |
| `mcp` | Status, source URL and scope or uncertainty notes |
| `verdict`, `blocker` | Buildability decision and material condition |
| `confidence` | Qualitative researcher judgment |
| `claims` | Field, claim value, source URL and evidence explanation |
| `notes` | Additional caveats |

For example, the Salesforce record distinguishes a free Developer Edition from production edition and permission requirements. Its `conditional` verdict preserves that distinction. Inspect `data/research.json` for complete records and their actual source links.

Verdicts mean:

- `ready`: a documented free, trial or local path supports a useful prototype scope.
- `conditional`: a material paid, administrative, review or partner condition affects the intended scope.
- `unknown`: evidence or product identity remains unresolved.
- `blocked`: explicit evidence prevents the intended scope. Failed searches alone do not justify this label.

MCP `not_verified` means no supported finding was established in this pass; it does not mean a server does not exist. Confidence is not a measured probability.

## 6. Research workflow: delivered study versus fresh runs

### What actually produced the delivered study

Codex research agents searched and read primary vendor documentation for the assignment inventory. A first-pass dataset was frozen, a targeted sample was checked, and corrections were recorded with evidence. The Python pipeline then validated and built the case study. Link retrieval checks were also executed.

The standalone model API research command described below was implemented but **was not executed for this delivery**, because no research API credential was supplied. The delivered study should not be presented as output from a tested end-to-end run of that command. Composio SDK/MCP and authenticated vendor API probes were not used in the executed research pass.

### How the optional standalone runner works

1. Read the selected app identities from `data/apps.json`.
2. Ask a web-search-capable model to find official documentation and return a structured record.
3. Parse the model response and validate the record shape and identity.
4. Make a separate model request that challenges the first answer, including auth changes, vendor identity, access gates and MCP claims.
5. Validate the revised record and five field checks: auth, access, API, MCP and verdict.
6. Preserve raw responses, first-pass rows, verified rows and checks in a local run directory.
7. Leave promotion to the report dataset as an explicit review step.

In PowerShell, set credentials locally using your own values:

```powershell
$env:OPENAI_API_KEY = "YOUR_API_KEY"
$env:RESEARCH_MODEL = "YOUR_WEB_SEARCH_CAPABLE_MODEL"
python research.py research --ids 1 --run trial
```

Do not commit credentials. The CLI reads process environment variables; it does not automatically load a `.env` file. The model must support Responses API web search. Fresh research incurs model/search usage, so start with one app.

Additional commands:

```powershell
# Research selected apps
python research.py research --ids 1,2,3 --run selected-apps

# Research the inventory, or resume this named run
python research.py research --run full-study

# Start a fresh timestamped run without replacing the earlier run
python research.py research --run full-study --refresh
```

Run artifacts are organized as follows:

```text
work/<run>/
  raw/NNN-first.json
  raw/NNN-verify.json
  first-pass/NNN.json
  verified/NNN.json
  checks/NNN.json
```

Completed validated rows are skipped on resume. Existing first-pass results can be reused. Requests retry transient network failures and selected rate-limit/server errors, with up to four attempts and exponential delays. A verifier using another prompt is still an automated check, not human verification.

After reviewing a run, merge approved records into `data/research.json`, preserving the full 100-app inventory and updating audit evidence as appropriate. Then run `replay`. The runner does not automatically merge results, overwrite the baseline or publish a site.

## 7. Validation, normalization and report generation

`research.py replay` validates required fields, enum values, authentication lists, claim fields and HTTPS evidence URLs. It also requires the complete set of IDs from 1 through 100.

`src/build.py` then:

1. Loads current research and available verification/link-check data.
2. Normalizes auth strings into display groups, preserving OAuth 1 and OAuth 2 separately.
3. Maps access gates to groups such as self-serve/trial, paid/admin, review/approval, outreach and unresolved.
4. Counts verdicts, auth methods, gates, category results, official MCP and distinct source URLs.
5. Generates escaped HTML table rows and embeds JSON into the report template.
6. Writes the report, exports, README and reproducible source archive to `dist/`.

Auth counts are multi-label: one app can contribute to OAuth 2 and API-key totals. Those percentages should not be added together. Access grouping is string-based normalization, so inspect its mapping when introducing a new gate label.

Outputs include `index.html`, `research.json`, `research.csv`, `summary.json`, `verification.json` and `source.zip`. The exported `dist/research.json` wraps rows together with summary and audit metadata; it is not the same shape as the source row list in `data/research.json`.

The report date is currently set in the builder. Update it when publishing a new research snapshot. The human-reviewed total is currently zero; browser review notes do not automatically update that value.

## 8. How the interface works

The browser reads the embedded dataset and updates the table using search and category, authentication, MCP and verdict filters. Selecting an app opens a dialog with access details, API scope, blockers, caveats and field-level evidence links.

The report also provides category comparisons, computed summary metrics, audit corrections and machine-readable downloads. Its built-in dataset checks inspect structural properties such as IDs and evidence slots. They do not contact vendors or establish factual correctness.

Human review controls store reviewer names, judgments and notes in that browser's `localStorage` under `tool-atlas-human-v1`. Export JSON to retain or share the work. Clearing browser data can erase those local notes. Reviews do not synchronize across devices, change the hosted dataset or certify a score automatically.

## 9. Verification and honest interpretation

The targeted agent audit covered 15 apps and five fields each, giving 75 judgments. The ledger records 57 supported, 9 corrected and 9 unresolved judgments. Five corrections enrich MCP evidence; four correct access/verdict classifications.

The report's documented-support ratios are:

```text
Before review: 57 / 75 = 76%
After corrections: (57 + 9) / 75 = 88%
```

These are results for a targeted automated review sample. They are neither a human accuracy measurement nor an estimate of correctness across all 100 apps. Fourteen sampled apps had a different-agent review; GitHub is explicitly marked as a same-agent recheck.

For a separate human worksheet:

```powershell
python research.py sample
```

This writes `work/human-review-template.json`. Sampling uses seed `20261123`, stable ID ordering and two apps per category: 20 apps and 100 field judgments. A reviewer must inspect the primary sources and record supported, incorrect or unresolved outcomes. Human review remains pending in the delivered snapshot.

To refresh reachability results:

```powershell
python research.py check-links --workers 6
python research.py replay
```

The checker records HTTP status, retrieval time, final URL, a hash of sampled content and errors. It restricts retrieval to public HTTPS destinations, validates redirects, limits response reads to 1 MB and uses timeouts and bounded concurrency. A 200 response means a page was retrieved; a 403 may reflect anti-bot protection. Neither proves the app's API access policy.

## 10. Tests and reproduction

```powershell
python -m unittest discover -s tests -v
python research.py replay
```

The six tests cover the complete valid dataset, reproducible category sampling, auth normalization, invalid record rejection, Responses message parsing and URL shape validation. All six passed during delivery. A clean extraction of the source archive was also rebuilt and produced the same summary.

Browser checks exercised search, evidence dialogs, dataset checks and the 20-app human sample filter. No automated test proves the vendor claims true; no authenticated app endpoint smoke tests were performed. The optional live model runner still needs a credentialed execution test.

## 11. Updating and publishing

To change findings, edit `data/research.json` and preserve the corresponding claim evidence and audit trail. To change layout or interactions, edit `src/template.html`. To change aggregation or exports, edit `src/build.py`. Avoid editing generated HTML directly because the next build overwrites it.

After changes, run the tests and replay, inspect the local report, and publish the complete `dist/` folder to the static host. A GitHub push alone does not establish that the hosted site has been redeployed. The live site and GitHub source are separate delivery surfaces.

## 12. Troubleshooting

| Symptom | What to check |
| --- | --- |
| `python` is not recognized | Install Python 3.11+ or try the Windows `py` launcher. |
| Port 8000 is occupied | Serve on another port, for example `python -m http.server 8001 --directory dist`. |
| Fresh research cannot authenticate | Check the process environment and account/model access; replay does not need a key. |
| Model response fails validation | Inspect the saved run artifacts and source claims before retrying. Do not weaken checks just to accept a row. |
| Documentation retrieval returns 403 | Open the source in a browser and distinguish retrieval protection from actual API restrictions. |
| A data edit does not appear | Run replay and refresh the browser; republish for the hosted site. |
| Download links fail | Serve or publish the complete `dist` folder, not only `index.html`. |
| Human notes are missing on another device | Notes are browser-local; use the JSON export to preserve and share them. |

## 13. Interview explanation and next steps

Suggested explanation:

> I built an evidence-backed integration research system for 100 apps. It separates authentication, prototype access, production restrictions, API scope and MCP availability so that a team can make a practical build decision. The report is generated from structured records, and every material finding can be inspected through linked evidence. I preserved a first pass and a correction ledger, and I distinguish automated checks from pending human verification. The delivered report is reproducible without API keys; the optional fresh-research runner is implemented but still needs a credentialed end-to-end test.

The most useful next steps are completing the human audit, testing the standalone research runner, performing read-only authenticated probes for a small app set, and adding explicit vendor-domain allowlists and dated rechecks. If Composio is added for authenticated probes, document that implementation and its real results separately from this documentation-research phase.
