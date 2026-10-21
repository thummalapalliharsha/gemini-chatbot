# Gemini Chatbot --- Project Documentation

> **Document purpose:** Technical reference for understanding, running,
> testing, and maintaining the Gemini Chatbot project.
>
> **Source of truth:** This document is based on the supplied project
> archive's source files (`app.py`, `requirements.txt`, `.env.example`,
> `.gitignore`, `promptfooconfig.yaml`, and `README.md`). Runtime
> findings are included only where they were recorded in the supplied
> audit report. No credentials are included.

## 1. Project Summary

**Gemini Chatbot** is a small Python web application that provides a
chat interface through Streamlit, obtains responses from Google's Gemini
model through the Google GenAI Python SDK, and instruments Google GenAI
calls for observability using OpenInference and Langfuse.

The project demonstrates how to connect a simple browser-based chat
interface to a hosted large language model (LLM) and configure tracing
for model calls.

### Main capabilities

-   Accepts a user's message through a Streamlit chat input.
-   Displays user and assistant messages in a chat-style interface.
-   Keeps the conversation in Streamlit session state for the active
    session.
-   Sends the role-labelled conversation text to the Gemini model.
-   Instruments Google GenAI calls using OpenInference.
-   Flushes buffered Langfuse traces after a response.
-   Loads API credentials and service configuration from environment
    variables or a local `.env` file.
-   Includes one Promptfoo evaluation case for a basic Machine Learning
    question.

### What the project is not

The current source does **not** implement persistent chat storage, user
authentication, multiple conversation management, a database, a
deployment setup, response streaming, or a configurable model selector.
These should not be described as existing features.

## 2. Technology Stack

  -----------------------------------------------------------------------
  Technology              Pinned version /        Role in this project
                          identifier              
  ----------------------- ----------------------- -----------------------
  Python                  Locally audited with    Main programming
                          Python 3.12.10          language and runtime

  Streamlit               `1.61.1`                Web UI, chat
                                                  components, session
                                                  state

  Google GenAI Python SDK `2.17.0`                Calls Google's Gemini
                                                  API

  Gemini model identifier `gemini-3.5-flash`      Model identifier used
                                                  in `app.py` and
                                                  Promptfoo config

  Langfuse                `4.14.3`                Observability client
                                                  and trace flushing

  OpenInference Google    `1.4.0`                 Instruments Google
  GenAI instrumentation                           GenAI SDK calls

  python-dotenv           `1.2.2`                 Loads values from a
                                                  local `.env` file

  Promptfoo               CLI not pinned in       Optional
                          `requirements.txt`      prompt-evaluation
                                                  configuration

  Git / GitHub            Publication not         Version control and
                          completed in the audit  remote hosting, once
                                                  configured
  -----------------------------------------------------------------------

**Version note:** Package versions above are taken from
`requirements.txt`; Python 3.12.10 is the version reported in the audit.
Promptfoo is configured in the project but is not listed in the Python
requirements file.

## 3. Repository / File Structure

The supplied archive contains the following project-level files,
excluding the local virtual environment:

``` text
Chatbot/
├── app.py
├── requirements.txt
├── promptfooconfig.yaml
├── README.md
├── .env.example
└── .gitignore
```

The archive also contains a local `.venv/`, `.env`, and Python cache
artifacts. These are local environment/runtime items, not files that
should be published to GitHub. The `.env` file may contain secrets and
should remain private.

### `app.py` --- application entry point

Contains the Streamlit interface and the main Gemini request flow. It
loads environment variables, initializes and checks Langfuse, enables
OpenInference instrumentation, creates the Gemini client, displays chat
history, builds conversation text, requests a model response, displays
it, saves it in session state, and flushes Langfuse traces.

### `requirements.txt` --- Python dependencies

Pins the Python package versions needed by the application:

``` text
streamlit==1.61.1
python-dotenv==1.2.2
google-genai==2.17.0
langfuse==4.14.3
openinference-instrumentation-google-genai==1.4.0
```

Pinning versions helps make installations more reproducible, although
availability and compatibility can still vary by platform and future
package registry changes.

### `.env.example` --- safe configuration template

Lists the environment variable names the app expects, with placeholder
values only. Copy it to `.env` and replace the placeholders locally.

### `.gitignore` --- files excluded from Git

Excludes `.env`, other `.env.*` files except `.env.example`, virtual
environments, Python bytecode/cache, pytest cache, Streamlit secrets,
logs, and build outputs.

### `promptfooconfig.yaml` --- prompt evaluation setup

Defines one prompt template, a Google Gemini provider, and a test
asking: "What is Machine Learning?" This is an evaluation configuration,
not part of the Streamlit chat UI's normal execution flow.

### `README.md` --- project overview

Contains the quick project description, features, stack, workflow,
setup, configuration, run instructions, checks, and known limitations.
This document expands on that README with source-level detail.

## 4. Application Architecture

The current application is a single-file Streamlit app. Its logical flow
is:

``` text
User opens Streamlit app
        |
        v
Load environment variables from .env
        |
        v
Create Langfuse client and check authentication
        |
        +---- authentication fails ---> Display error and stop
        |
        v
Enable Google GenAI OpenInference instrumentation
        |
        v
Create Google GenAI client using GEMINI_API_KEY
        |
        v
Render title and existing session messages
        |
        v
User submits a message
        |
        v
Display and append the user message to session state
        |
        v
Combine session messages into role-labelled text
        |
        v
Call Gemini model through Google GenAI SDK
        |
        v
Display and append the assistant response
        |
        v
Flush Langfuse trace buffer
```

The diagram represents the order of operations in the source code. The
source flushes Langfuse after generation; the audit did not
independently verify that the corresponding trace appeared in the
Langfuse dashboard.

## 5. Detailed `app.py` Walkthrough

### 5.1 Imports

The application imports:

-   `os` to read environment variables.
-   `streamlit` as `st` for the UI and session state.
-   `load_dotenv` from `python-dotenv` to load local configuration.
-   `genai` from `google` to create the Google GenAI client.
-   `get_client` from `langfuse` to initialize the Langfuse client.
-   `GoogleGenAIInstrumentor` to instrument Google GenAI SDK calls.

### 5.2 Environment loading

``` python
load_dotenv()
```

Loads values from a local `.env` file into the process environment when
such a file exists. The application source does not hard-code the Gemini
or Langfuse credentials.

### 5.3 Langfuse initialization and authentication

``` python
langfuse = get_client()

if not langfuse.auth_check():
    st.error("Langfuse authentication failed. Check your .env keys.")
    st.stop()

GoogleGenAIInstrumentor().instrument()
```

The code creates a Langfuse client and checks its authentication. If
authentication fails, Streamlit displays an error and stops executing
the app. If it succeeds, the Google GenAI instrumentation is enabled.

This makes Langfuse authentication a startup dependency: even if the
Gemini key is valid, the app will stop at startup when Langfuse
authentication fails.

The audit reported that the Langfuse authentication check succeeded. It
also reported a non-fatal warning during a rerun test indicating that
instrumentation was already active. The source does not contain an
explicit guard against repeated instrumentation.

### 5.4 Gemini client initialization

``` python
gemini = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
```

Creates the Google GenAI client using the `GEMINI_API_KEY` environment
variable. The code does not explicitly validate that the variable is
present before constructing the client; missing or invalid credentials
may therefore cause a request-time or initialization error depending on
SDK behavior.

### 5.5 Streamlit page setup

``` python
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖"
)

st.title("🤖 Gemini Chatbot")
st.caption("Gemini + Langfuse")
```

Sets the browser tab title and icon, then displays the application title
and a caption identifying the Gemini and Langfuse integration.

### 5.6 Session-based chat history

``` python
if "messages" not in st.session_state:
    st.session_state.messages = []
```

Initializes a `messages` list the first time the Streamlit session runs.
The app uses this list to retain the current conversation between
Streamlit reruns.

Each stored message is a dictionary with:

-   `role`: either `"user"` or `"assistant"`.
-   `content`: the message text.

This is temporary session state, not persistent database storage. It
should not be presented as a durable chat-history feature.

### 5.7 Rendering previous messages

The app iterates through `st.session_state.messages` and uses
`st.chat_message(message["role"])` to render each stored message.
`st.markdown(message["content"])` displays the text inside the
appropriate user or assistant chat bubble.

### 5.8 Reading user input

``` python
if prompt := st.chat_input("Ask me anything..."):
```

Displays the chat input. When a non-empty submission is returned, the
app displays the user message and appends it to session state.

The assignment expression (`:=`) both tests whether the input is truthy
and assigns the submitted text to `prompt`.

### 5.9 Building the conversation payload

The code creates a string called `conversation` and adds every stored
message in order, using the format:

``` text
user: <message text>
assistant: <message text>
```

Each message ends with a newline. The resulting role-labelled string is
sent as the `contents` argument to Gemini.

**Implementation detail:** The application passes a plain text
transcript, not a structured list of role/content objects. The source
does not configure a formal system instruction or use the SDK's
multi-turn chat-session abstraction.

### 5.10 Requesting a Gemini response

``` python
response = gemini.models.generate_content(
    model="gemini-3.5-flash",
    contents=conversation
)

answer = response.text
```

The app makes a synchronous generation request through the Google GenAI
SDK. The model identifier is hard-coded in `app.py`. It then reads the
response's `.text` field into `answer`.

The current source has no explicit `try/except` around this request and
no explicit handling for an empty or missing response text. Network
errors, rate limits, invalid credentials, unavailable models, or
provider-side errors may interrupt a rerun instead of being displayed
through a tailored error message.

### 5.11 Rendering and storing the answer

The response is displayed using `st.chat_message("assistant")` and
`st.markdown(answer)`. Then an assistant message dictionary is appended
to `st.session_state.messages`.

Because the history is stored only in session state, it is not saved to
a database or file by this code.

### 5.12 Flushing Langfuse traces

``` python
langfuse.flush()
```

Requests that buffered Langfuse events be flushed after the Gemini
response is handled. OpenInference instrumentation is intended to
capture the Google GenAI call.

Calling `flush()` does not by itself prove that a trace was successfully
delivered and is visible in Langfuse. That requires checking the
relevant trace in the configured Langfuse project.

## 6. Environment Variables and Secrets

The project uses the following variables from `.env.example`:

  -----------------------------------------------------------------------
  Variable                Purpose                 Required for current
                                                  flow?
  ----------------------- ----------------------- -----------------------
  `GEMINI_API_KEY`        Credentials for Gemini  Yes, for generation
                          API requests            

  `LANGFUSE_PUBLIC_KEY`   Identifies the Langfuse Yes, for configured
                          project/client          Langfuse authentication

  `LANGFUSE_SECRET_KEY`   Secret used for         Yes, for configured
                          Langfuse authentication Langfuse authentication

  `LANGFUSE_HOST`         Base URL for the        Yes, must point to the
                          Langfuse service        intended Langfuse
                                                  instance
  -----------------------------------------------------------------------

The supplied example uses placeholders, not real values. Keep actual
values in a local `.env` file or a secure secret manager. Do not place
credentials in source code, screenshots, public documentation, Git
commits, or issue reports.

### Create the local environment file

PowerShell:

``` powershell
Copy-Item .env.example .env
```

Then edit `.env` locally and replace the placeholder values. Do not copy
real credential values into this documentation.

## 7. Installation and Running the App

### Prerequisites

-   Python 3.12 is the version reported in the audit.
-   A Gemini API key with access to the configured model.
-   A Langfuse project and its public key, secret key, and host.
-   Network access to the configured external services.
-   Optional: Promptfoo CLI if running the evaluation configuration.

### Windows PowerShell setup

Run from the project root:

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` to add your own credentials.

### macOS / Linux setup

``` bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your own credentials.

### Start Streamlit

With the environment activated:

``` bash
python -m streamlit run app.py
```

Streamlit prints a local URL in the terminal. Open that URL in a browser
to use the chat interface.

## 8. Promptfoo Evaluation Configuration

The file `promptfooconfig.yaml` contains a prompt template:

``` text
You are a helpful AI assistant. Answer the user's question clearly and accurately in simple language.

User: {{question}}
```

It selects the provider identifier:

``` text
google:gemini-3.5-flash
```

It defines one test variable:

``` text
question: "What is Machine Learning?"
```

The evaluation is intended to send that question through the configured
Gemini provider and evaluate the resulting output using Promptfoo. The
YAML does not define a custom assertion or scoring rubric, so the
existence of the test case should not be interpreted as proof of
semantic correctness.

The project README documents this command:

``` powershell
promptfoo eval -c promptfooconfig.yaml --env-file .env
```

Promptfoo is not pinned in `requirements.txt`; install and configure its
CLI separately according to its own installation instructions if you
want to run this evaluation. A live evaluation makes external API
requests and may incur charges. The supplied audit did not report
running Promptfoo evaluation.

## 9. Testing and Validation

### Checks reported in the supplied audit

  -----------------------------------------------------------------------
  Check                   Reported result         What it establishes
  ----------------------- ----------------------- -----------------------
  Python syntax           Passed                  Source compiles
  compilation                                     syntactically
  (`py_compile app.py`)                           

  `pip check`             Passed                  Installed Python
                                                  packages had no
                                                  reported dependency
                                                  conflicts

  Streamlit AppTest       Passed without app      UI rendered in the test
  startup                 exceptions              harness

  Chat input presence     Verified                Chat input was rendered

  Local Streamlit health  HTTP 200                Local Streamlit server
  endpoint                                        was responsive during
                                                  the audit

  Local app page          HTTP 200                App page was served

  Langfuse authentication Passed                  Configured Langfuse
  check                                           authentication check
                                                  succeeded

  One Gemini prompt       Non-empty response      A real response was
  through the app         rendered                received through the
                                                  core chat flow

  Exact-string check for  Did not match           The response was not
  `OK`                                            exactly the requested
                                                  string; this alone does
                                                  not mean generation
                                                  failed

  Langfuse trace          Not independently       Trace delivery remains
  visibility              verified                unconfirmed

  Promptfoo evaluation    Not run in audit        Evaluation outcome is
                                                  unknown

  Automated unit-test     Not configured          No project-specific
  suite                                           automated test suite
                                                  was present in the
                                                  inspected project files
  -----------------------------------------------------------------------

### Manual verification checklist

-   [ ] Confirm `.env` has valid credentials without sharing or
    committing them.
-   [ ] Start the app with `python -m streamlit run app.py`.
-   [ ] Confirm the page opens and displays the Gemini Chatbot title.
-   [ ] Submit a simple non-sensitive prompt.
-   [ ] Confirm an assistant response is rendered.
-   [ ] Submit a second prompt and confirm prior messages remain visible
    within the same session.
-   [ ] Check the Langfuse project for a trace associated with the
    request.
-   [ ] If desired, run the Promptfoo evaluation separately and review
    its actual output.

**Status based on the supplied audit:** The core chat response flow was
exercised successfully. Langfuse trace delivery, long-running stability,
error paths, and Promptfoo evaluation were not fully verified. A
successful build or startup alone would not establish all of those
behaviors.

## 10. Known Limitations and Risks

1.  **No persistent storage:** Conversation history exists only in
    Streamlit session state.
2.  **No authentication or user accounts:** The source does not
    implement a login system or user-specific access controls.
3.  **Hard-coded model identifier:** `gemini-3.5-flash` is specified
    directly in `app.py`.
4.  **Limited error handling:** The Gemini request has no explicit
    exception handling for provider, network, rate-limit, or
    authentication errors.
5.  **No empty-response guard:** The source reads `response.text`
    without checking whether it is empty or absent.
6.  **Langfuse startup dependency:** Failed Langfuse authentication
    stops the application.
7.  **Trace delivery not independently confirmed:** The app calls
    `langfuse.flush()`, but dashboard-level confirmation is still
    needed.
8.  **Repeated instrumentation warning:** The audit observed a non-fatal
    warning during reruns indicating that instrumentation was already
    active.
9.  **No project-specific test suite:** The inspected project files do
    not contain a dedicated unit or integration test suite.
10. **No deployment configuration:** The inspected project files do not
    include a documented deployment setup or public demo.
11. **Promptfoo CLI is separate:** Promptfoo is configured but not
    included in the pinned Python requirements.
12. **External API dependency and cost:** Gemini generation requires
    service access and may consume API quota or incur charges.

## 11. Security and GitHub Publication

The `.gitignore` file includes rules to exclude:

-   `.env` and other `.env.*` files, while allowing `.env.example`.
-   `.venv/`, `venv/`, and `env/`.
-   Python bytecode and `__pycache__/`.
-   `.pytest_cache/`.
-   `.streamlit/secrets.toml`.
-   Logs and generated build directories such as `build/` and `dist/`.

Before publishing:

1.  Confirm `.env` is not tracked or staged.
2.  Review the exact staged files before committing.
3.  Scan intended source and configuration files for credentials.
4.  Keep `.env.example` placeholders only.
5.  Do not publish the local `.venv/` directory or Python cache files.
6.  Verify the intended GitHub remote and branch.
7.  Avoid force-pushing or overwriting existing remote history without
    explicit approval.

The supplied audit reported that the intended publication files were
scanned for common credential patterns and no such patterns were
detected. That is a useful check, but no automated pattern scan can
guarantee that every possible secret is absent.

The audit also reported that the folder was not a Git repository and had
no configured remote at the time of the audit. GitHub publication was
therefore not completed.

## 12. Suggested Future Improvements

These are recommendations, not implemented features:

-   Add structured error handling and user-friendly messages for Gemini
    failures.
-   Validate required environment variables before initializing clients.
-   Add a guard for empty or missing model response text.
-   Make the model identifier configurable through an environment
    variable.
-   Add unit tests for conversation formatting and configuration
    validation.
-   Add integration tests that can be run explicitly with controlled API
    usage.
-   Verify Langfuse trace creation in a documented test procedure.
-   Add persistent storage only if durable chat history is a project
    requirement.
-   Consider a formal system instruction and structured multi-turn
    Gemini chat handling.
-   Add deployment instructions and secret configuration for the chosen
    hosting platform.
-   Pin or document the Promptfoo CLI version if evaluation
    reproducibility is important.

## 13. Glossary

-   **LLM (Large Language Model):** A model that generates text from
    input prompts.
-   **Gemini API:** Google's service interface for sending prompts to
    Gemini models and receiving responses.
-   **Streamlit:** A Python framework for building interactive web
    applications.
-   **Session state:** Per-session state managed by Streamlit across
    reruns; it is not a database.
-   **Observability:** Instrumentation and telemetry used to inspect
    application/model behavior.
-   **Trace:** A record of an operation or request flow, potentially
    including nested events/spans.
-   **OpenInference:** Instrumentation conventions and libraries for
    observing AI/LLM application calls.
-   **Langfuse:** An LLM observability platform used here as the trace
    destination.
-   **Promptfoo:** A tool for evaluating and testing LLM prompts and
    model outputs.

## 14. Final Project Status

**Project identity:** Gemini Chatbot\
**Primary purpose:** A minimal Streamlit chat UI backed by Gemini, with
Langfuse/OpenInference instrumentation.\
**Core status:** The supplied audit reports a successful real Gemini
response through the app.\
**Observability status:** Langfuse authentication succeeded; the
specific trace's delivery was not independently confirmed.\
**Documentation:** This file describes the implementation present in the
supplied archive and distinguishes existing functionality from
recommendations.\
**GitHub status at audit time:** Not pushed; a verified remote was not
configured.

------------------------------------------------------------------------

*Keep this document aligned with the code. Update it whenever
implementation, dependencies, configuration, tests, or deployment
behavior changes.*
