<img width="1280" height="640" alt="AYYO Malayalam Python Companion Banner" src="https://github.com/user-attachments/assets/8920b256-2ba8-4988-b824-5351134eb4bd" />

# AYYO.py — Malayalam Python Playground & Code Companion 🎯

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Framework](https://img.shields.io/badge/framework-Flask%203.0.3-green.svg)
![WSGI](https://img.shields.io/badge/WSGI-Waitress%20%7C%20Gunicorn-orange.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![TinkerHub](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Useless Projects](https://img.shields.io/badge/UselessProjects--3.0-26?link=https%3A%2F%2Ftinkerhub.org%2Fevents%2F1M8ORET9A1%2Fuseless-projects-3.0)

---

## 📌 Basic Details

### Team Name: AYYO Tech
- **Project Name**: AYYO Malayalam Python Playground & Companion
- **Repository**: [https://github.com/Ann-Maria-Jaison/useless_project_temp.git](https://github.com/Ann-Maria-Jaison/useless_project_temp.git)

---

## 💡 Project Description

### What is AYYO?
**AYYO.py** is an interactive, full-stack Python playground and code companion designed with a hilarious Malayalam/Manglish twist. It goes beyond simple code execution by providing sandboxed runtime execution, AST-based static code analysis, automated refactoring, security inspection, personality profiling, automated unit test generation, emoji code visualization, and voice feedback synthesis via offline TTS.

### The Problem (That Nobody Asked to Solve)
Standard IDEs and compilers emit dry, intimidating error messages like `ZeroDivisionError: division by zero` or `IndexError: list index out of range`. Beginner developers often feel frustrated and lost when faced with cryptic stack traces.

### The Solution (That Everyone Needs!)
AYYO intercepts Python code and runtime errors, translating them into friendly, witty Manglish commentary ("*Ayyo! Zero base division math rule breaking detected bro!*"), complete with code cleanup recommendations, personality scorecards, auto-generated unit tests, and spoken voice responses!

---

## ✨ Key Features

| Mode / Feature | Icon | Description |
| :--- | :---: | :--- |
| **Diagnose Mode** | 🔴 | Runs code inside a sub-second isolated sandbox. Translates runtime errors into friendly Manglish explanations with actionable fixes. |
| **Code Explainer** | 🧠 | Parses Abstract Syntax Trees (AST) to explain variables, loops, functions, and predictable outputs in plain English & Manglish. |
| **Code Detective** | 🕵️ | Audits code for security smells, infinite loops, dead code, and suspicious patterns. |
| **Code Cleaner** | 🧹 | Formats messy Python code, adds missing docstrings, cleans unnecessary print statements, and normalizes formatting. |
| **Personality Profiler**| 🧬 | Analyzes coding style and assigns scores across 5 traits: *Risk*, *Patience*, *Overengineering*, *Drama*, and *Curiosity*. |
| **Test Lab** | 🧪 | Automatically generates dynamic unit test cases for user functions and executes them against the sandbox. |
| **Voice Synthesis** | 🔊 | Converts diagnostic feedback into spoken audio using `pyttsx3` offline speech synthesis engine. |
| **Emoji View & Palette** | 🎨 | Renders Python code as emoji visual tokens and provides interactive quick-program templates. |

---

## 🏗️ System Architecture

AYYO is designed as a modular 4-layer architecture comprising a responsive Web Frontend / CLI, a Flask REST Routing Layer, a Core Static & Runtime Analysis Engine, and an Isolated Subprocess Sandbox.

```mermaid
graph TD
    %% User Interfaces
    subgraph Presentation_Layer ["1. Presentation Layer"]
        UI["Web IDE (HTML5 / JS / Tailwind CSS)"]
        CLI["CLI Interface (main.py)"]
        LibraryUI["Emoji Code Library Catalog"]
    end

    %% Web & API Routing
    subgraph Routing_Layer ["2. Web & WSGI Routing Layer"]
        WSGI["WSGI Server (Waitress / Gunicorn)"]
        Flask["Flask App (app.py)"]
        BP_Run["Run Blueprint (routes/run.py)"]
        BP_Lib["Library Blueprint (routes/library.py)"]
    end

    %% Core Business Logic Engine
    subgraph Engine_Layer ["3. Core Analysis & Feature Engine"]
        Analyzer["AST Analyzer (core/analyzer.py)"]
        Explainer["Code Explainer (core/explainer.py)"]
        Detective["Code Detective (core/detective.py)"]
        Cleaner["Code Cleaner (core/cleaner.py)"]
        Personality["Personality Engine (core/personality.py)"]
        TestLab["Test Lab Generator (core/test_lab.py)"]
        VoiceEngine["Voice Synthesizer (core/voice.py)"]
        EmojiEngine["Emoji Engine (core/emoji_view.py)"]
    end

    %% Sandbox & Execution
    subgraph Execution_Layer ["4. Sandboxed Execution & External Integrations"]
        Runner["Subprocess Sandbox Runner (core/runner.py)"]
        PyExec["Isolated Python Process"]
        TTS["pyttsx3 / SAPI5 / espeak Audio Engine"]
    end

    %% Connections
    UI -->|HTTP / JSON| WSGI
    LibraryUI -->|HTTP / JSON| WSGI
    CLI -->|Direct Imports| Engine_Layer

    WSGI --> Flask
    Flask --> BP_Run
    Flask --> BP_Lib

    BP_Run --> Analyzer
    BP_Run --> Explainer
    BP_Run --> Detective
    BP_Run --> Cleaner
    BP_Run --> Personality
    BP_Run --> TestLab
    BP_Run --> VoiceEngine
    BP_Run --> EmojiEngine

    Analyzer --> Runner
    TestLab --> Runner
    BP_Run --> Runner

    Runner -->|Executes Code with Timeout| PyExec
    VoiceEngine -->|Renders WAV Audio| TTS
```

---

## 🔄 Data Flow Diagrams (DFD)

### DFD Level 0: Context Diagram
The Context Diagram represents the high-level interaction between the User and the AYYO System.

```mermaid
graph LR
    User(("User / Developer"))
    
    subgraph AYYO_System ["AYYO Python Playground System"]
        SystemProcess["AYYO Code Companion Engine"]
    end

    User -->|1. Submit Python Code / Execution Request| SystemProcess
    User -->|2. Select Mode (Diagnose, Explain, Test, Clean)| SystemProcess
    
    SystemProcess -->|3. Return Execution Output & Error Diagnostics| User
    SystemProcess -->|4. Return AST Analysis & Code Personality| User
    SystemProcess -->|5. Stream Voice Audio Feedback (WAV)| User
```

---

### DFD Level 1: Subsystem Data Flow Diagram
DFD Level 1 illustrates how user data moves across internal processing modules.

```mermaid
graph TD
    User(("User"))

    %% Subsystems
    P1["1.0 Request Handler & Input Validator"]
    P2["2.0 AST Code Analyzer & Parser"]
    P3["3.0 Subprocess Execution Sandbox"]
    P4["4.0 Error Explainer & Hints Engine"]
    P5["5.0 Personality & Test Lab Processor"]
    P6["6.0 Speech Audio Synthesizer"]

    %% Data Stores
    D1[("Emoji & Quick Templates Store")]
    D2[("Error & Hints Library")]

    %% Flow Connections
    User -->|Raw Code & Config| P1
    P1 -->|Validated Code String| P2
    P1 -->|Validated Code String| P3
    
    P3 -->|Execution Result / Stdout / Stderr| P4
    P2 -->|AST Structure & Tokens| P4
    P2 -->|AST Structure & Tokens| P5
    
    D2 -->|Error Patterns & Tips| P4
    D1 -->|Snippet Templates| P1

    P4 -->|Formatted Diagnostics & Manglish Verdict| User
    P5 -->|Personality Scorecard & Test Results| User

    P4 -->|Text to Speak| P6
    P6 -->|WAV Audio Stream| User
```

---

### DFD Level 2: Sandboxed Code Execution & Error Pipeline
DFD Level 2 details the exact processing steps when a code execution request is processed.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Route as routes/run.py
    participant Runner as core/runner.py
    participant Subprocess as Isolated Python Process
    participant Analyzer as core/analyzer.py
    participant Explainer as core/explainer.py
    participant Voice as core/voice.py

    User->>Route: POST /run (code, timeout)
    Route->>Route: Validate payload size (< 20 KB) & clamp timeout (1-10s)
    
    Route->>Runner: run_code(code, timeout)
    Runner->>Subprocess: Popen(["python", "-c", code])
    
    alt Code Execution Succeeds
        Subprocess-->>Runner: Return stdout output (Exit Code 0)
        Runner-->>Route: {"ok": true, "output": "..."}
    else Execution Times Out / Errors
        Subprocess-->>Runner: TimeoutExpired / Exception Traceback
        Runner->>Analyzer: Analyze traceback & line number
        Analyzer-->>Runner: Extracted error type, line, and offending code
        Runner-->>Route: {"ok": false, "error": {...}}
    end

    Route->>Explainer: explain_code(analysis)
    Explainer-->>Route: Manglish summary & hints

    opt Voice Mode Enabled
        Route->>Voice: speak_text(text)
        Voice-->>Route: WAV Audio Bytes
    end

    Route-->>User: JSON Response (+ WAV Audio)
```

---

## 📂 Project Structure & Component Breakdown

```
ayyo/
├── app.py                  # Flask Application Factory & Server Entrypoint (Dev)
├── wsgi.py                 # Production WSGI Entrypoint (Waitress / Gunicorn)
├── main.py                 # Interactive Command Line Interface (CLI)
├── requirements.txt        # Python Dependencies (Flask, pyttsx3, waitress, gunicorn)
├── Dockerfile              # Production Docker Container Build Specification
├── docker-compose.yml      # Local Docker Compose Orchestration
├── Procfile                # Heroku / Railway / Render Deployment Process Descriptor
├── render.yaml             # Render Infrastructure-as-Code Manifest
├── .gitignore              # Ignored files (caches, environments, secrets)
├── README.md               # Complete Project Documentation
│
├── core/                   # Core Analysis & Business Logic Engine
│   ├── analyzer.py         # AST parser & code structure extractor
│   ├── autofix.py          # Auto-correction suggestion algorithms
│   ├── cleaner.py          # Code beautifier & refactoring engine
│   ├── detective.py        # Static security & smell inspector
│   ├── emoji_library.py    # Pre-built emoji program catalog
│   ├── emoji_palette.py    # Palette token mappings
│   ├── emoji_view.py       # Code-to-Emoji visual parser
│   ├── errors.py           # Custom error classifier & translations
│   ├── explainer.py        # Code summarizer & expected output predictor
│   ├── hints.py            # Helpful debugging tips provider
│   ├── personality.py      # Code personality trait scoring algorithm
│   ├── renderer.py         # Terminal output formatting utilities
│   ├── run.py              # Low-level execution helper
│   ├── runner.py           # Subprocess sandbox executor with timeout control
│   ├── sandbox.py          # Security restrictions & isolation rules
│   ├── test_lab.py         # Dynamic unit test generator & runner
│   └── voice.py            # pyttsx3 text-to-speech audio synthesizer
│
├── routes/                 # Web Route Blueprints
│   ├── __init__.py
│   ├── run.py              # Execution, analysis, personality & voice REST APIs
│   └── library.py          # Emoji library snippet endpoints
│
├── static/                 # Frontend Static Assets
│   ├── style.css           # Custom CSS styling
│   └── avatar.jpg          # AYYO Mascot Avatar
│
├── templates/              # HTML Web Views
│   ├── index.html          # Main Web IDE Playground interface
│   └── library.html        # Emoji Library catalog interface
│
└── tests/                  # Automated Test Suite
    ├── __init__.py
    └── test_ayyo.py        # Unit tests for core engines & Flask routes
```

---

## 📡 REST API Reference

| Endpoint | Method | Request Payload | Description |
| :--- | :---: | :--- | :--- |
| `/run` | `POST` | `{"code": "...", "timeout": 5}` | Executes Python code in sandbox and returns stdout/error. |
| `/analyze` | `POST` | `{"code": "..."}` | Returns static syntax/lint issues without running code. |
| `/explain` | `POST` | `{"code": "..."}` | Returns AST breakdown (variables, functions, loops) and Manglish take. |
| `/detective` | `POST` | `{"code": "..."}` | Audits code for security risks, suspicious activity, and audit scores. |
| `/cleaner` | `POST` | `{"code": "..."}` | Returns refactored, formatted code and list of modifications made. |
| `/personality` | `POST` | `{"code": "..."}` | Computes developer personality score distribution. |
| `/test-lab` | `POST` | `{"code": "..."}` | Generates automated unit test code for functions present in input. |
| `/test-lab/run` | `POST` | `{"code": "...", "tests": [...]}` | Executes generated unit tests against user code. |
| `/voices` | `GET` | *None* | Lists available system text-to-speech voices. |
| `/speak` | `POST` | `{"text": "...", "rate": 150}` | Returns a `audio/wav` binary stream of synthesized speech. |
| `/api/emoji-view` | `POST` | `{"code": "..."}` | Converts python code into line-by-line emoji visual representation. |
| `/api/emoji-palette`| `GET` | *None* | Returns emoji palette definitions and quick program templates. |

---

## ⚙️ Installation & Local Setup

### Prerequisites
- Python **3.10** or higher
- `pip` (Python package manager)
- *(Optional)* `espeak` and `ffmpeg` (for Linux voice synthesis)

### Step 1: Clone Repository
```bash
git clone https://github.com/Ann-Maria-Jaison/useless_project_temp.git
cd useless_project_temp
```

### Step 2: Create Virtual Environment & Install Dependencies
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 3: Run the Application

#### Option A: Run CLI Interface
```bash
python main.py
```

#### Option B: Run Web IDE (Development Mode)
```bash
python app.py
```
*Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.*

#### Option C: Run Production WSGI Server (Waitress)
```bash
python wsgi.py
```

---

## 🚀 Production Deployment Guide

### 1. Local / On-Premise WSGI Serving
The project uses `waitress` as a production-grade multi-threaded WSGI server on Windows/Linux:
```bash
python wsgi.py
```

### 2. Containerized Deployment (Docker & Docker Compose)
To run in a self-contained Linux environment with `espeak` TTS pre-installed:

```bash
# Build and run container in detached mode
docker-compose up -d --build
```
*Access the app at `http://localhost:5000`.*

### 3. Cloud Deployment (Render / Heroku / Railway)
- **Render**: Connect your GitHub repository. Render will automatically read `render.yaml` or `Dockerfile`.
- **Heroku / Railway / Fly.io**: Deploy directly. The platform will execute `gunicorn wsgi:app` specified in the [Procfile](file:///c:/Users/Ann/Desktop/ayyo/Procfile).

---

## 🧪 Testing & Verification

Run the automated unittest suite to verify all core engines and HTTP endpoints:

```bash
python -m unittest discover tests
```

**Test Output:**
```
.............
----------------------------------------------------------------------
Ran 13 tests in 0.129s

OK
```

---

## 📜 Team & Acknowledgments

- **Developed for**: TinkerHub Useless Projects 3.0 Hackathon
- **Made with**: ❤️, Python, Flask, and lots of Malayalam humor!

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProjects--3.0-26?link=https%3A%2F%2Ftinkerhub.org%2Fevents%2F1M8ORET9A1%2Fuseless-projects-3.0)
