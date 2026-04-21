# 🚀 Dry Run Visualizer

> A lightweight, browser-based Python debugger that lets you step through code line-by-line, inspect variables at every step, and understand exactly how your program executes — no IDE required.

---

## 📋 Table of Contents

- [What Is This?](#-what-is-this)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Logic Flow Diagram](#-logic-flow-diagram)
- [Installation & Setup](#-installation--setup)
- [Complete User Flow](#-complete-user-flow)
- [API Reference](#-api-reference)
- [How the Tracer Works](#-how-the-tracer-works)
- [Step Object Reference](#-step-object-reference)
- [Error Handling](#-error-handling)
- [Known Limitations](#-known-limitations)
- [Tech Stack](#-tech-stack)

---

## 🔍 What Is This?

The **Dry Run Visualizer** is a mini debugger for Python code. You paste or type any Python snippet into the browser, click **Run**, and the tool executes it on the server using Python's built-in `sys.settrace` hook. Every time a new line is about to execute, a snapshot is taken: which line, and what are all the local variables at that exact moment.

Those snapshots (called **steps**) are sent back to the browser, where you can:

- Walk through them one at a time with **Prev / Next**
- See which variables changed (highlighted in green)
- Jump to a bird's-eye view of every step with **Run Full**
- See errors pinpointed to the exact failing line

No extensions, no Node.js, no database — just Python, FastAPI, and a single HTML file.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Step-by-step execution** | Navigate forward and backward through every line that executed |
| **Variable tracking** | See the full local variable snapshot at each step |
| **Change highlighting** | Variables that changed since the last step are highlighted green |
| **Line gutter highlight** | The active line number is highlighted gold in the gutter |
| **Run Full view** | See all steps and their variables in a single scrollable table |
| **Error pinpointing** | Runtime errors are caught and attributed to the exact line |
| **Loading states** | Run button disables and shows a spinner during execution |
| **Clear / Reset** | One-click reset of all state |
| **XSS-safe rendering** | All variable names and values are HTML-escaped before display |

---

## 📁 Project Structure

```
dry-run-visualizer/
│
├── tracer.py       # Execution engine — sys.settrace logic, step collection
├── main.py         # FastAPI server — single POST /run endpoint
└── index.html      # Frontend — editor, controls, step display (no build step)
```

All three files live in the **same directory**. There are no sub-packages, no config files, and no build process.

---


## ⚙️ Installation & Setup

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.8 or higher |
| pip | any recent version |

### 1 — Clone or download the project

```bash
# If using git
git clone https://github.com/your-username/dry-run-visualizer.git
cd dry-run-visualizer

# Or just place all three files in one folder
```

### 2 — Install Python dependencies

```bash
pip install fastapi uvicorn
```

That's it. There are no other dependencies.

### 3 — Start the backend server

```bash
uvicorn main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 4 — Open the frontend

Open `index.html` directly in your browser:

```bash
# macOS
open index.html

# Linux
xdg-open index.html

# Windows
start index.html
```

Or drag the file into any browser tab. No local web server needed for the frontend.

### 5 — Verify it works

Visit `http://127.0.0.1:8000/docs` in your browser — you should see FastAPI's auto-generated Swagger UI with the `/run` endpoint listed.

---

## 🧭 Complete User Flow

This section walks through every interaction from opening the app to inspecting results.

---

### Step 1 — Open the app

Open `index.html` in your browser. You will see:

- A **code editor** (textarea) pre-filled with a sample loop
- A **line number gutter** on the left, auto-generated from the code
- Four action buttons: **▶ Run**, **⬅ Prev**, **Next ➡**, **Run Full ⚡**, **✕ Clear**
- A **step info bar** showing a placeholder message
- A **variables panel** below it, also showing a placeholder

`Prev`, `Next`, and `Run Full` are all **disabled** until code has been run.

---

### Step 2 — Write or edit code

Click inside the textarea and type (or modify) any Python snippet. Example:

```python
x = 10
y = 20
result = x + y
print(result)
```

The line number gutter updates **live** as you type — one number per line, always in sync.

---

### Step 3 — Click ▶ Run

Clicking **Run**:

1. Reads the current textarea content
2. Disables the Run button and shows a spinner (`Running…`)
3. Sends a `POST` request to `http://127.0.0.1:8000/run` with the code as JSON
4. The server executes the code under the `sys.settrace` hook
5. Every line event produces a step snapshot
6. The full list of steps is returned as JSON
7. The browser stores the steps array and calls `showStep()` for step 0

If the server is unreachable, an error message is shown in the step info bar.

---

### Step 4 — Inspect Step 1

After a successful run:

- The **step info bar** shows: `Step 1 / N | Line X`
- The **line gutter** highlights line X in gold
- The **variables panel** shows every local variable and its value at that moment
- Variables that are **new or changed** compared to the previous step are shown in **green**
- `Prev`, `Next`, and `Run Full` become enabled

At step 1, all variables are considered "new" so everything shows green.

---

### Step 5 — Click Next ➡

Each click on **Next** advances `current` by 1 and re-renders:

- The step info bar updates the step counter and line number
- The gutter highlight moves to the new active line
- The variables panel re-renders, comparing with the previous step
- Only variables whose values changed appear in green; unchanged ones stay white

When you reach the **last step**, the Next button is automatically disabled.

---

### Step 6 — Click ⬅ Prev

Each click on **Prev** decrements `current` by 1 and re-renders the same way.

When you reach **step 1**, the Prev button is automatically disabled.

---

### Step 7 — Click Run Full ⚡

Clicking **Run Full** switches the variables panel to a **table view** showing every step at once:

| Column | Content |
|---|---|
| Step N | Sequential step number |
| Line X | The line number for that step |
| Variables | All variable key=value pairs for that step |

Error steps in the full view are shown in red with the error message inline.

This view is useful for seeing the entire execution history in one scroll rather than clicking through one step at a time.

---

### Step 8 — Runtime error scenario

If the code raises an exception (e.g. `ZeroDivisionError`, `NameError`), the tracer catches it and appends a special **error step**:

```json
{ "line": 3, "error": "ZeroDivisionError: division by zero" }
```

The frontend renders this as:

- Step info bar turns **red** with the message `❌ Error on line 3: ZeroDivisionError: division by zero`
- The gutter highlights the failing line in gold
- The variables panel is cleared

All steps that executed successfully **before** the error are still fully accessible via Prev.

---

### Step 9 — Click ✕ Clear

Clicking **Clear** resets everything to the initial state:

- `steps` array is emptied
- `current` is reset to -1
- Step info bar and variables panel return to placeholder text
- Line gutter highlight is removed
- `Prev`, `Next`, and `Run Full` are disabled again

The code in the editor is **not** cleared so you can edit and re-run.

---

## 📡 API Reference

### `POST /run`

Executes a Python code string and returns execution steps.

**Request**

```
POST http://127.0.0.1:8000/run
Content-Type: application/json
```

```json
{
  "code": "x = 1\ny = x + 1\nprint(y)"
}
```

**Response 200 — success**

```json
{
  "steps": [
    { "line": 1, "variables": {} },
    { "line": 2, "variables": { "x": 1 } },
    { "line": 3, "variables": { "x": 1, "y": 2 } }
  ]
}
```

**Response 200 — with error step at end**

```json
{
  "steps": [
    { "line": 1, "variables": { "x": 0 } },
    { "line": 2, "error": "ZeroDivisionError: division by zero", "line": 2 }
  ]
}
```

**Response 400 — empty code**

```json
{ "detail": "Code cannot be empty." }
```

**Response 500 — tracer-level crash**

```json
{ "detail": "Tracer error: <message>" }
```

**Interactive docs:** `http://127.0.0.1:8000/docs`

---

## 🔬 How the Tracer Works

Python's `sys.settrace` lets you register a callback that fires on every code event. The tracer uses only the `line` event, which fires **once per line, just before that line executes**.

```
User code line N about to execute
    → Python fires _trace(frame, "line", None)
    → _last_line = frame.f_lineno          # store for error attribution
    → variables = dict(frame.f_locals)     # snapshot all local variables
    → filter out __dunder__ keys           # remove Python internals
    → safe_repr each value                 # make everything JSON-serialisable
    → append {"line": N, "variables": ...} to _steps
    → return _trace                        # keep tracing
```

If an exception is raised at any point during `exec()`, it is caught in the `try/except` block. The last line number stored in `_last_line` is used to attribute the error to the correct line:

```
Exception raised inside exec()
    → caught by except block
    → append {"line": _last_line, "error": str(exc)} to _steps
    → sys.settrace(None) in finally block — always removes the hook
```

The `finally` block guarantees the trace hook is **always removed**, even if something unexpected happens inside the tracer itself.

---

## 📦 Step Object Reference

Every item in the `steps` array follows one of two shapes:

### Normal step

```json
{
  "line": 4,
  "variables": {
    "arr": [1, 2, 3],
    "i": 1,
    "result": 2
  }
}
```

| Field | Type | Description |
|---|---|---|
| `line` | `int` | 1-based line number of the line about to execute |
| `variables` | `object` | Key-value snapshot of all local variables at this point |

### Error step

```json
{
  "line": 7,
  "error": "NameError: name 'x' is not defined"
}
```

| Field | Type | Description |
|---|---|---|
| `line` | `int \| null` | Line where the error occurred; `null` if it fired before any line |
| `error` | `string` | Python exception string |

---

## 🛡 Error Handling

| Scenario | Backend behaviour | Frontend behaviour |
|---|---|---|
| Empty code string | Returns HTTP 400 | Shows error in step info bar |
| Valid code, no error | Returns 200 with steps array | Normal step-through flow |
| Runtime exception in user code | Returns 200 with error step appended | Red bar, line highlight, clears variables |
| Tracer crash (unexpected) | Returns HTTP 500 | Shows error in step info bar |
| Server unreachable | `fetch` throws `TypeError` | Shows "Failed to fetch" error in bar |
| Non-serialisable variable | `_safe_repr` converts to `repr()` string | Displayed as string in variable panel |
| Variable with `__dunder__` name | Filtered in tracer | Never reaches the frontend |

---

## ⚠️ Known Limitations

| Limitation | Detail |
|---|---|
| **Single-file scope only** | The tracer only captures locals inside the top-level `exec` scope. Nested function calls are not traced into. |
| **No `input()` support** | `input()` will hang the server because there is no TTY. Avoid it in user code. |
| **No multi-thread safety** | `sys.settrace` is global to the Python interpreter. Do not run concurrent requests. |
| **No persistent sessions** | Each `/run` call is stateless. State lives only in the browser's `steps` array. |
| **Print output not captured** | `print()` writes to the server's stdout, not to the browser. Output capture is not implemented. |
| **Large code = many steps** | Long loops produce one step per iteration. A `for i in range(10000)` will generate 10 000+ steps. |

---

## 🧰 Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Execution engine | Python `sys.settrace` | Built into Python, no dependencies |
| Backend framework | FastAPI | Minimal, fast, automatic Swagger docs |
| ASGI server | Uvicorn | Standard companion for FastAPI |
| Data validation | Pydantic (via FastAPI) | Request body parsing with zero boilerplate |
| Frontend | Vanilla HTML / CSS / JS | No build step, no framework overhead |
| HTTP communication | Browser `fetch` API | Native, no library needed |

---

## 📄 License

MIT — do whatever you like with it.
