# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A **literature review agent**（文献综述 Agent）for the 中文信息处理 course. User enters a research topic →
the system runs a fixed pipeline: **retrieve → extract → cluster → generate review → visualize**, served
through a Flask web UI. The project is fully implemented (not a plan).

All user-facing strings, comments, and docs are in **Chinese** — the deliverable is graded in Chinese.
Keep new code's comments and UI text Chinese to match.

## Grading leverage (where to spend effort)

The **Chinese information extraction** module (`src/extraction/`) is the grading core; it carries the most
scoring weight. The two extraction paths (rule-based vs LLM) must stay **runnable side-by-side with
identical output fields** — that field alignment is what makes `eval/compare.py` able to compute a P/R/F1
comparison, which is itself a scoring point. Never delete the rule-based path once the LLM path works.

Do **not** add: CNKI/知网 or other Chinese-DB scrapers (excluded for anti-scraping/compliance), citation
graphs, or autonomous agent planning. The "agent" here is the deterministic `run_full_pipeline`, not a planner.

## Commands

```bash
# Run the web app (http://127.0.0.1:5000)
python app.py

# Quantitative extraction eval — rule-based only (no token cost, runs in seconds)
python eval/compare.py
# ...with LLM path too (needs DEEPSEEK_API_KEY; prints ΔF1 of LLM vs rule)
python eval/compare.py --llm

# Topic-relevance accuracy eval (the ≥85% 论文主题准确率 grading requirement)
python eval/topic_eval.py             # rule-based keyword-overlap judge (no key)
python eval/topic_eval.py --llm --rank # report-grade: LLM judge + product-side ranking

# Debug / network scripts
python scripts/check_net.py        # diagnose arXiv / S2 reachability + proxy state
python scripts/test_retrieval.py   # full translate + retrieve chain
python scripts/show_pipeline.py    # pretty-print a /api/pipeline JSON response
```

There is no test runner, linter, or build step — dependencies are intentionally minimal
(`requirements.txt`: no torch / sentence-transformers / pandas / openai SDK). Install with
`pip install -r requirements.txt`.

To extend the eval set, append entries to `eval/labeled.json` following the existing 12-item schema
(`{paper_id, title, year, abstract, gold:{methods,datasets,metrics,conclusion_keywords}}`).

## Configuration

`config.py` loads `.env` (copy from `.env.example`; never edit `.env.example` directly). The LLM is
**DeepSeek** (OpenAI-compatible HTTP, called via a ~50-line `requests` wrapper in `src/llm/deepseek_client.py`,
not the openai SDK). `config.llm_available()` gates every LLM path. **Without a key the app still runs** —
extraction, translation, and review all fall back to rule-based/template versions, and the UI shows an
orange warning. Preserve this graceful degradation in any LLM-touching change.

## Architecture

Two dataclasses in `src/models.py` flow through the whole pipeline: `Paper` (retrieval output) →
`StructuredRecord` (extraction output). Both extractors emit the *same* `StructuredRecord` fields — keep
them aligned if you add a field (update both extractors, `eval/labeled.json`, `eval/compare.py`, and the
frontend table together).

`src/pipeline.py` is the orchestration layer and the single source of truth for the flow:

- `retrieve()` — if the topic contains Chinese, translate to English first (arXiv is ~all English).
  arXiv uses the English query only; Semantic Scholar runs both EN and ZH queries. Cross-source dedup is
  by normalized title (`src/retrieval/dedup.py`), done here, not in the clients. Recent papers (<2yr) are
  exempt from the citation-count floor so frontier work isn't filtered out.
- `run_full_pipeline()` — **over-fetches `max_results * 3`** candidates, enriches them concurrently with
  GitHub repo/star data, **sorts by `github_stars` descending**, then truncates to `max_results`. So the
  papers shown are the most-starred of a larger pool, not the raw search order. `deep_read=True` adds a
  full-text fetch stage before extraction.

Stage-by-stage:

- **Retrieval** (`src/retrieval/`) — `arxiv_client.py` (Atom XML via feedparser; year filtering is
  client-side because the API lacks it), `semantic_scholar_client.py` (sorts by `influentialCitationCount`,
  silently returns `[]` on 429). **Both clients bypass HTTP(S)_PROXY by default** (`proxies={"http":"","https":""}`)
  because local V2ray/Clash proxies block these public academic APIs; set `USE_PROXY_FOR_RETRIEVAL=1` to opt in.
  `enricher.py` is the over-scope extra: concurrent (`ThreadPoolExecutor`) scraping of HuggingFace Papers /
  PapersWithCode for code repos + GitHub stars (with a browser-UA HTML-regex fallback when GitHub 403-rate-limits),
  arXiv figure extraction for posters, and full-text fetch (arXiv HTML, falling back to `PyPDF2` on the PDF).
- **Extraction** (`src/extraction/`) — `BaseExtractor` abstract swap. `rule_based.py` (the grading core):
  jieba + the three dictionaries in `data/dict/` (loaded via `jieba.add_word` at startup so terms like
  「自注意力」aren't split) + regex for metric values. `llm_based.py`: DeepSeek structured JSON; forces
  methods/datasets/metrics into normalized English for aggregation, but `conclusion` in Chinese; on failure
  returns an empty-field record (keeping `paper_id`) so the pipeline never crashes. The LLM path runs
  concurrently (5 workers) in `extract_all`; the rule path is sequential.
- **Clustering** (`src/clustering/topic_cluster.py`) — TF-IDF + KMeans with k auto-chosen by paper count
  (<4 no clustering, up to 5). Labels each cluster from top cluster-center terms + frequent record methods.
  `year_trend()` is a simple Counter. (TF-IDF deliberately chosen over sentence-transformers to avoid a 2GB+ torch dep.)
- **Review** (`src/review/generator.py`) — DeepSeek consumes numbered records; the prompt hard-requires
  every `[n]` citation to come from the given numbers. After generation, regex `\[(\d+)\]` scans output and
  flags out-of-range numbers as `hallucinated_citations` — citation traceability is explicitly graded, so
  keep this validation. Also extracts a Mermaid evolution diagram. `_fallback_review` produces a 5-section
  template draft when the LLM is unavailable. Two LLM-only companions sit beside the generator:
  `optimizer.py` (`/api/optimize_review`) is a multi-agent refine loop — a「找茬专家」auditor checks the
  draft against the RAG source records for hallucinated numbers/citations, then a reviser rewrites; and
  `assistant.py` (`/api/chat_assistant`) is the「选题小助手」that reverse-questions the user to converge
  on a search query (emits its final keywords inside 【…】). Both no-op gracefully without an LLM key.
- **Frontend** — **Flask + native HTML/JS** (`app.py`, `templates/index.html`, `static/`), *not*
  Streamlit/Gradio. CDN libs (chart.js, wordcloud2.js, marked, mermaid) — no npm/build. `POST /api/pipeline`
  is the one-shot endpoint; `/api/retrieve|extract|cluster|review` are per-stage; `/api/deep_read_paper`
  drives the per-paper 精读 modal; `/api/optimize_review` and `/api/chat_assistant` back the two LLM
  companions above. Hallucinated `[n]` citations are rendered with a red `warn` class.

## Reference docs

`README.md` (Chinese usage guide, FAQ) and `docs/DESIGN.md` (per-file walkthrough, timing breakdown,
grading-point mapping) are kept current and detailed — consult `docs/DESIGN.md` before deep changes.
Original brief: `作业思路.md`.
