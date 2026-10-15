# InsightIQ --- AI-Powered Data Analysis Agent

> Ask questions about a dataset in natural language and turn the results
> into structured, reproducible analysis.

InsightIQ is a work-in-progress data analysis agent built with **Python,
FastAPI, Pandas, Pydantic, and Google Gemini**. It is designed to
connect natural-language questions with controlled data-analysis
operations, rather than asking an LLM to execute arbitrary generated
code.

The project is being developed with an emphasis on clear architecture,
validated plans, testable components, and verifiable outputs.

> **Project status:** Core tabular-analysis workflow is under active
> development. The ingestion package is being reorganized before broader
> source support is added. Features marked *Planned* are not represented
> as completed functionality.

## Contents

-   [Why InsightIQ?](#why-insightiq)
-   [Current capabilities](#current-capabilities)
-   [How it works](#how-it-works)
-   [Architecture](#architecture)
-   [Project structure](#project-structure)
-   [Technology stack](#technology-stack)
-   [Getting started](#getting-started)
-   [Configuration](#configuration)
-   [API overview](#api-overview)
-   [Testing and code quality](#testing-and-code-quality)
-   [Engineering principles](#engineering-principles)
-   [Roadmap](#roadmap)
-   [Future ingestion design](#future-ingestion-design)
-   [Contributing](#contributing)

## Why InsightIQ?

Analyzing data often requires users to know the right code, libraries,
and sequence of operations. InsightIQ aims to make that workflow more
accessible:

1.  Provide a dataset.
2.  Ask a question in plain language.
3.  Convert the question into a structured analysis plan.
4.  Validate the plan against a known set of operations.
5.  Execute the approved operations using Python data tools.
6.  Return results in a structured response that can be inspected and
    tested.

The goal is not simply to generate an answer. It is to make the steps
behind that answer easier to inspect and verify.

## Current capabilities

The following reflects the project direction and known implementation
state; check the code and tests in the current branch for the exact
latest status.

-   **Natural-language analysis endpoint** for asking a question about
    an uploaded dataset.
-   **Structured-plan execution** through a defined analysis workflow.
-   **Plan validation** using Pydantic models and constraints before
    execution.
-   **Controlled analysis tools**, including dataset profiling,
    filtering, sorting, grouping and aggregation, statistics,
    correlation, and outlier detection.
-   **Tabular file ingestion** currently centered on CSV, Excel
    (`.xlsx`), and JSON.
-   **FastAPI backend** with health and analysis endpoints.
-   **Streamlit interface** for interacting with the analysis workflow.
-   **Automated tests and linting** using pytest and Ruff.

Support for additional file formats, web pages, documents, images,
audio, and video is part of the roadmap---not a claim about current
functionality.

## How it works

### Natural-language question flow

``` mermaid
flowchart TD
    A[User uploads a dataset] --> B[Streamlit interface]
    B --> C[FastAPI analysis endpoint]
    C --> D[Dataset ingestion]
    D --> E[Dataset and schema available]
    E --> F[Gemini planner creates structured plan]
    F --> G[Plan validation]
    G -->|Valid| H[Plan executor]
    G -->|Invalid| I[Return a validation error]
    H --> J[Registered analysis tools]
    J --> K[Normalize results]
    K --> L[Structured API response]
    L --> B
```

### Key design decision: plan first, execute through known tools

The language model helps interpret the user's question and propose a
structured plan. The application validates that plan before execution.
Approved steps are handled by registered application tools, rather than
treating model-generated Python as trusted code.

This separation makes it easier to test each layer, constrain what the
agent can do, and diagnose failures.

## Architecture

InsightIQ is organized into layers with distinct responsibilities:

-   **`app/api/`** --- HTTP routes, request parsing, and response
    schemas.
-   **`app/agent/`** --- language-model planning and the
    natural-language analysis workflow.
-   **`app/core/`** --- application configuration and shared core
    concerns.
-   **`app/services/`** --- orchestration of ingestion, plan execution,
    and output normalization.
-   **`app/tools/`** --- registered data-analysis operations and the
    tool registry.
-   **`tests/`** --- unit and API-level regression tests.
-   **`frontend/` or the current Streamlit entry point** --- user
    interface; the exact location depends on the current repository
    layout.

The ingestion layer is being moved into its own package. The target
structure below is the **planned organization**, and may not exactly
match the current branch yet.

## Project structure

``` text
InsightIQ/
├── app/
│   ├── agent/
│   │   └── gemini_planner.py
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── core/
│   │   └── config.py
│   ├── services/
│   │   └── analysis_service.py
│   ├── tools/
│   │   ├── profiler.py
│   │   ├── statistics.py
│   │   ├── transformation.py
│   │   └── registry.py
│   └── ingestion/                 # Planned dedicated ingestion package
│       ├── __init__.py
│       ├── base.py                # Shared adapter contract
│       ├── models.py              # Common ingestion result models
│       ├── detection.py           # Source/type detection
│       ├── exceptions.py          # Ingestion-specific errors
│       ├── service.py             # Ingestion orchestration
│       └── adapters/
│           ├── __init__.py
│           ├── tabular.py
│           ├── documents.py       # Planned
│           ├── web.py             # Planned
│           ├── images.py          # Planned
│           ├── audio.py           # Planned
│           └── video.py           # Planned
├── tests/
│   ├── unit/
│   └── api/
├── .env.example                  # Recommended configuration template
├── pyproject.toml
├── uv.lock
└── README.md
```

**Repository note:** Keep this diagram aligned with the actual files as
the refactor progresses. Do not create empty modules just to match the
diagram; introduce each module when its responsibility is implemented.

## Technology stack

  Technology                   Purpose
  ---------------------------- ----------------------------------------------
  Python                       Application and analysis logic
  FastAPI                      HTTP API
  Pandas                       Tabular data loading and transformation
  Pydantic                     Request models, plan schemas, and validation
  Google Gen AI SDK / Gemini   Natural-language planning
  Streamlit                    Lightweight user interface
  pytest                       Automated tests
  Ruff                         Linting and code-quality checks
  uv                           Dependency and environment management

## Getting started

### Prerequisites

-   Python version supported by `pyproject.toml` (currently Python 3.13
    or newer).
-   [`uv`](https://docs.astral.sh/uv/) installed.
-   A Google Gemini API key for model-powered analysis.

### 1. Clone the repository

``` bash
git clone https://github.com/<your-github-username>/InsightIQ.git
cd InsightIQ
```

Replace the placeholder URL with the actual repository URL after
publishing the project.

### 2. Install dependencies

``` bash
uv sync
```

If the repository does not yet contain a committed `uv.lock`, `uv sync`
will resolve dependencies from `pyproject.toml` and create a lock file.

### 3. Configure environment variables

Create a local `.env` file in the project root. Never commit the real
`.env` file or API keys.

``` dotenv
GEMINI_API_KEY=replace_with_your_key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TIMEOUT_SECONDS=60
MAX_FILE_SIZE_MB=50
ENVIRONMENT=development
```

Environment variable names must match the settings definitions in
`app/core/config.py`. If a setting uses a different alias in the current
branch, follow the code and update this example accordingly.

### 4. Run the API

Use the module path that exists in the current repository. For an
application exposing `app` from `app.main`:

``` bash
uv run uvicorn app.main:app --reload
```

Open the interactive API documentation at:

-   `http://127.0.0.1:8000/docs`
-   `http://127.0.0.1:8000/health` (if the health route is enabled)

If the FastAPI instance is defined in a different module, adjust the
Uvicorn import path to match it.

### 5. Run the Streamlit interface

Run the Streamlit entry-point file used by the current repository. For
example:

``` bash
uv run streamlit run frontend/streamlit_app.py
```

If the frontend file is located elsewhere, substitute its actual path.
Keep the backend running in a separate terminal.

## Configuration

Configuration is managed through the application's settings module and
environment variables.

  Setting                    Purpose
  -------------------------- ------------------------------------------
  `GEMINI_API_KEY`           Secret used to authenticate with Gemini
  `GEMINI_MODEL`             Model name used for planning
  `GEMINI_TIMEOUT_SECONDS`   Model request timeout
  `MAX_FILE_SIZE_MB`         Maximum accepted upload size
  `ENVIRONMENT`              Environment label, such as `development`

Keep credentials out of source code, logs, screenshots, commits, and
issue reports. Use a separate secret configuration for deployments.

## API overview

The API currently includes these main workflows:

  -----------------------------------------------------------------------
  Endpoint                            Purpose
  ----------------------------------- -----------------------------------
  `GET /health`                       Health check

  `POST /api/analyze`                 Analyze an uploaded file using a
                                      supplied structured plan

  `POST /api/analyze-question`        Create and execute an analysis plan
                                      from a natural-language question
  -----------------------------------------------------------------------

Inspect `/docs` for the exact request fields and response schemas in the
current branch. The structured-plan endpoint expects a plan in the
format defined by the application's Pydantic schema; use the API
documentation rather than guessing the payload.

Example workflow:

1.  Start the API.
2.  Open `/docs`.
3.  Select `POST /api/analyze-question`.
4.  Upload a supported dataset and provide a question.
5.  Inspect the response, including the plan and analysis result.

## Testing and code quality

Run the automated test suite:

``` bash
uv run pytest -q
```

Run Ruff:

``` bash
uv run ruff check app tests
```

Before opening a pull request, run both commands and review any changed
imports after moving modules. Add tests for new adapters, invalid
inputs, size limits, parsing failures, and API error responses.

## Engineering principles

InsightIQ is being designed around these principles:

-   **Validated plans:** validate model-produced structures before
    execution.
-   **Controlled capabilities:** execute registered tools instead of
    trusting arbitrary model-generated code.
-   **Separation of concerns:** keep API, planning, orchestration,
    tools, and ingestion responsibilities separate.
-   **Testability:** test components and failure cases independently.
-   **Reproducibility:** preserve the plan and structured outputs needed
    to understand how a result was produced.
-   **Defensive input handling:** enforce file-size limits, reject
    unsupported inputs, and return useful errors without exposing
    secrets.
-   **Evidence and provenance:** as source types expand, retain source
    identifiers and extraction metadata so results can be traced back to
    their inputs.

These are design goals; features should be described as implemented only
when backed by code and tests.

## Roadmap

The roadmap is staged to keep the system useful while its architecture
grows.

### Phase 1 --- Stabilize the tabular-analysis core

-   [ ] Complete the ingestion-package refactor without breaking
    existing imports.
-   [ ] Keep current CSV, Excel, and JSON behavior covered by tests.
-   [ ] Add clear validation and error messages for malformed or
    unsupported files.
-   [ ] Verify all API endpoints and the Streamlit workflow end to end.
-   [ ] Document actual response schemas and example requests.

### Phase 2 --- Build a unified ingestion interface

-   [ ] Define common ingestion result models and an adapter contract.
-   [ ] Add source/type detection and a central ingestion service.
-   [ ] Keep source-specific parsing isolated in adapters.
-   [ ] Return consistent metadata and clear errors across supported
    sources.

### Phase 3 --- Expand source support

-   [ ] More structured formats, such as TSV, JSON Lines, and Parquet,
    subject to dependency and security review.
-   [ ] Documents such as PDF, DOCX, and text files, with page/section
    provenance.
-   [ ] Web-page ingestion with URL validation, timeouts, and safe
    fetching.
-   [ ] Image extraction using OCR or vision models.
-   [ ] Audio transcription with timestamps where available.
-   [ ] Video processing using extracted audio and sampled frames.

### Phase 4 --- Improve evidence and reproducibility

-   [ ] Attach source references to extracted text and analysis
    findings.
-   [ ] Preserve extraction metadata, timestamps, and processing
    versions.
-   [ ] Record the validated analysis plan and tool outputs for each
    run.
-   [ ] Add deterministic test fixtures and regression cases.
-   [ ] Distinguish extracted evidence, computed results, and
    model-generated interpretation.

### Phase 5 --- Production readiness

-   [ ] Add request IDs and structured logs that do not expose secrets
    or uploaded content unnecessarily.
-   [ ] Apply upload limits, timeouts, and resource limits consistently.
-   [ ] Add authentication and rate limiting before public deployment.
-   [ ] Add CI checks for tests and linting.
-   [ ] Add deployment configuration, health checks, and operational
    documentation.
-   [ ] Evaluate caching, background jobs, and persistent run history if
    workload requires them.

## Future ingestion design

The proposed ingestion layer will normalize different input types into a
shared result contract while retaining source-specific metadata.

``` mermaid
flowchart TD
    A[Upload or URL] --> B[Input validation]
    B --> C[Source and type detection]
    C --> D[Adapter selection]
    D --> E1[Tabular adapter]
    D --> E2[Document adapter]
    D --> E3[Web adapter]
    D --> E4[Image adapter]
    D --> E5[Audio adapter]
    D --> E6[Video adapter]
    E1 --> F[Common ingestion result]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F
    E6 --> F
    F --> G[Metadata and provenance]
    G --> H[Analysis or retrieval workflow]
```

A common result should carry only fields that can be defined
consistently, such as:

-   Source type and safe source identifier.
-   Extracted content or a typed representation appropriate to the
    source.
-   Metadata such as filename, media type, page number, timestamp, or
    extraction method when applicable.
-   Warnings and extraction errors that can be surfaced to the caller.
-   Provenance needed to trace derived findings back to the original
    source.

Not every source should be forced into a Pandas DataFrame. Tabular data
can remain a DataFrame; documents and media may produce text segments,
timestamps, page references, or other typed artifacts. The shared
contract should describe these outputs without erasing their
differences.

### Security considerations for future adapters

-   Validate URL schemes and block private, loopback, and link-local
    destinations to reduce server-side request forgery (SSRF) risk.
-   Set connection/read timeouts and response-size limits for remote
    fetching.
-   Treat uploaded files and extracted text as untrusted input.
-   Do not execute macros, scripts, or code found in files.
-   Avoid logging raw user content or secrets.
-   Apply resource limits to OCR, transcription, video decoding, and
    other expensive processing.
-   Keep model instructions separate from untrusted document content and
    test prompt-injection scenarios.

## Contributing

Contributions and issue reports are welcome once the repository is
published.

1.  Create a focused branch.
2.  Make a small, testable change.
3.  Add or update tests.
4.  Run `uv run pytest -q` and `uv run ruff check app tests`.
5.  Update the README if behavior or setup changes.
6.  Open a pull request with the problem, approach, and verification
    steps.

## License

A license has not yet been selected. Add a `LICENSE` file before
describing the repository as open source. Until then, do not assume
others have permission to reuse the code.

------------------------------------------------------------------------

**For recruiters and reviewers:** the project is intended to demonstrate
API design, LLM integration, schema validation, controlled tool
execution, data processing, testing, and incremental architecture
design. The README distinguishes current capabilities from planned work
so that the repository can be evaluated against the actual
implementation.
