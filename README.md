# AI and human code security comparison

Research materials for a comparison of 30 AI-generated and 30 human-written implementations using SonarQube. Each implementation is one observation; the analysed files total 30 AI and 225 human files.

## Contents

| Directory | Contents |
|---|---|
| `prompts/` | The 30 generation prompts |
| `data/ai-original/` | Original AI outputs |
| `data/ai-scanned/` | AI files used for scanning |
| `data/human-sources.csv` | Thirty source repositories, commits, task scope and differences |
| `data/human-files.csv` | Exact upstream paths and hashes of the 225 scanned human files |
| `data/manual-review.csv` | Researcher-reported review classifications |
| `analysis/` | Reproduction script, source retrieval script and deduplication method |
| `scan/` | Recorded scanner settings, profiles, versions and raw output |
| `results/` | Recalculated counts, deduplicated issues and statistics |
| `reports/` | Results workbook and Word/Markdown summaries |
| `licences/` | Repository licence evidence and redistribution status |

## Results

| Measure | AI | Human |
|---|---:|---:|
| Raw Vulnerability findings | 16 | 9 |
| Issues after deduplication | 11 | 7 |
| Implementations with findings | 11 | 6 |
| Security Hotspots | 60 | 56 |
| Debug hotspots requiring deployment context | 16 | 6 |

The recorded raw-count comparison uses a two-sided Mann–Whitney test (p = 0.156). This does not establish equal security. Differences in code size, functionality and development history limit attribution to AI authorship. The statistical result here applies to raw scanner findings; it is not a paired or deduplicated test result.

## Reproduce the analysis

Use Python 3.10 or later. Run from this repository:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python analysis/reproduce.py
```

This recalculates the results directly from the archived scans, verifies them against the recorded statistics, and generates the six-sheet Excel workbook and Word/Markdown summaries. No Docker, network access or human-code download is needed after dependencies are installed. Confidence intervals use 20,000 independent within-group bootstrap resamples with seed 20261011. Deduplication is explained in `analysis/DEDUPLICATION.md` and traceable by finding ID in `results/deduplicated-issues.csv`.

For source retrieval and fresh scanning, see `scan/README.md`.

## Generation and scan preparation

Generation took place on 24 March 2026. Copilot Chat 0.35.2 was used in VS Code Agent mode; most recorded requests selected Auto, and sample 28 selected Gemini 3 Pro Preview. Multiple Copilot prompts shared a conversation. The researcher reported one run per prompt and no user-defined code-generation custom or memory instructions. ChatGPT was accessed through its web interface; the exact historical model and conversation setup are not asserted in this package.

Missing string delimiters were corrected on eleven lines across AI samples 6, 8, 14, 16, 22 and 29 so SonarQube could parse them. Original outputs remain in `data/ai-original/`; scanned copies are in `data/ai-scanned/`. The JSON correction record and patch show every edit. The paths in the patch refer to the original study workspace; use the JSON record and `data/ai-files.csv` to map to this package.

## Manual review

The researcher reported reviewing all findings and classifying the 22 debug-mode hotspots as needing deployment context, with all other findings classified as security concerns. `data/manual-review.csv` transcribes those statements; it is not a browser-exported review log or an independent second review. Optional notes remain empty where no finding-specific notes were supplied. Raw SonarQube statuses remain unchanged in the archived output.

## Source availability and licences

All human implementations are identified by repository, commit and file path. Human code is not bundled while redistribution questions remain open. `analysis/fetch_human.py` can retrieve the selected files locally and verify their hashes; retrieved files are excluded from Git. The repository licence audit is in `licences/Repository_Licences.csv`.

No blanket licence has been applied to this mixed research package. Select terms for the researcher's own materials before public release; third-party code retains its applicable terms. Example credentials in the AI samples are retained as research evidence. Actual scanner credentials and private local configuration are excluded.

This repository covers the code comparison, not the respondent survey, dissertation, unused candidates or earlier scans. GitHub publication and a Zenodo DOI are not yet configured.
