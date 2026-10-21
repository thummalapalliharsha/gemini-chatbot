# Gemini Chatbot

A small Streamlit chatbot that sends user conversations to Google's Gemini API and instruments Google GenAI calls for Langfuse observability.

## Purpose

This project is a minimal example of connecting a browser-based chat interface to a hosted language model while tracing model calls with Langfuse. It is a starting point for experimenting with Gemini and LLM observability, not a persistent or multi-user chat service.

## Features

### Implemented

- Chat interface built with Streamlit.
- User and assistant messages kept in Streamlit session state for the current browser session.
- Responses requested through the Google GenAI Python SDK.
- Google GenAI calls instrumented with OpenInference and Langfuse.
- Gemini and Langfuse credentials loaded from environment variables or a local `.env` file.
- A Promptfoo configuration containing one Gemini prompt evaluation case.

### Not implemented

- Persistent conversations, user accounts, or conversation management.
- Automated unit or integration tests for the Gemini conversation flow.
- A deployment configuration or public demo.
- Configurable model selection, response streaming, or explicit error handling for Gemini failures.

## Technology stack

| Component | Technology |
| --- | --- |
| Language | Python |
| Web app | Streamlit |
| Model API | Google GenAI SDK (Gemini) |
| Observability | Langfuse and OpenInference instrumentation |
| Configuration | `python-dotenv` and environment variables |
| LLM evaluation configuration | Promptfoo (`promptfooconfig.yaml`) |

The dependencies in [`requirements.txt`](requirements.txt) are pinned. The existing local environment was verified with Python 3.12.10 and the package versions listed there.

## How it works

1. Streamlit renders the conversation stored in the current browser session.
2. On submission, the app appends the user's message to session state and combines the conversation into role-labelled text.
3. The Google GenAI client requests a response using the `gemini-3.5-flash` model identifier in `app.py`.
4. The response is rendered and appended to the conversation.
5. OpenInference instruments the Google GenAI call, and the app flushes Langfuse traces.

Langfuse authentication is checked when the app starts. A failed check stops startup and displays an error.

## Project structure

```text
.
├── app.py                 # Streamlit application entry point
├── promptfooconfig.yaml   # One-case Promptfoo evaluation config
├── requirements.txt       # Pinned Python dependencies
├── .env.example           # Placeholder environment variables
├── .gitignore             # Ignores local secrets and generated files
└── README.md
```

The local `.env` file and `.venv` environment are not part of the project files intended for publication.

## Prerequisites

- Python 3.12 (the locally verified version).
- A Gemini API key with access to the configured model.
- A Langfuse project and its public key, secret key, and host URL.
- Optional: the Promptfoo CLI to run the configured evaluation.

## Setup

From the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` locally and replace the placeholders with credentials for your own services. Do not commit the populated `.env` file.

On macOS or Linux, activate the virtual environment with:

```bash
source .venv/bin/activate
```

## Configuration

| Variable | Purpose |
| --- | --- |
| `GEMINI_API_KEY` | Authenticates requests to the Gemini API. |
| `LANGFUSE_PUBLIC_KEY` | Langfuse project public key. |
| `LANGFUSE_SECRET_KEY` | Langfuse project secret key. |
| `LANGFUSE_HOST` | URL of the Langfuse Cloud or self-hosted instance. |

The `.env.example` file contains placeholders only. Keep actual credentials in `.env` or a secure secret manager.

## Run the app

With the virtual environment activated:

```powershell
python -m streamlit run app.py
```

Then open the local URL printed by Streamlit. The app does not use a database; conversation history is temporary and scoped to the current Streamlit session.

## Tests, evaluation, and build

There is no configured unit-test suite or production build step. The following local checks are available:

```powershell
python -m pip check
python -m py_compile app.py
```

The Promptfoo configuration can be run with the Promptfoo CLI:

```powershell
promptfoo eval -c promptfooconfig.yaml --env-file .env
```

That evaluation calls the configured Gemini provider and may incur API usage charges. It is separate from the Streamlit app and was not run as part of the audit.

## Current status and limitations

**Core status: working; observability delivery is not fully verified.** The installed dependencies pass `pip check`, the Python source compiles, the app renders its chat UI, and the configured Langfuse authentication check succeeds. During the audit, a minimal prompt submitted through the Streamlit chat flow returned a non-empty Gemini response. The app flushes Langfuse after generation, but delivery of that specific trace was not independently checked.

Other known limitations:

- Messages are lost when the Streamlit session ends.
- The model identifier is hard-coded in `app.py`.
- The app has no explicit handling for Gemini request errors or empty response text.
- Re-running the app in the audit test process logged a non-fatal warning that Google GenAI instrumentation was already active.
- Automated tests, a deployment configuration, and a public demo are not present.
