# SentinelOS — Intent Engine

This is your (Person 2) slice of the project: a module that takes a raw shell
command and returns structured JSON describing what the command is *trying*
to do. It works in two modes:

- **Mock mode** — no API key needed. Rule-based guesses. Good enough for
  your teammates to build against today.
- **Live mode** — uses the real Claude API. Needs an API key.

You do not need to understand FastAPI, venvs, or Claude's API before
starting. Just follow these steps in order.

---

## 0. What you need installed first

Open a terminal and check you have Python 3.10+:

```bash
python3 --version
```

If that fails or shows something below 3.10, install Python from
https://www.python.org/downloads/ first, then come back.

---

## 1. Get the files onto your machine

If you already have the `sentinelos/` folder, `cd` into this folder:

```bash
cd sentinelos/backend/intent_engine
```

You should see these files here:
```
engine.py
api.py
test_engine.py
requirements.txt
README.md
```

---

## 2. Create an isolated Python environment (venv)

This keeps this project's packages separate from everything else on your
machine. Run:

```bash
python3 -m venv venv
```

Then **activate** it:

- macOS / Linux:
  ```bash
  source venv/bin/activate
  ```
- Windows (PowerShell):
  ```powershell
  venv\Scripts\Activate.ps1
  ```

You'll know it worked because your terminal prompt now starts with `(venv)`.

You need to do this `activate` step every time you open a new terminal to
work on this project.

---

## 3. Install the required packages

With the venv active:

```bash
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, the Anthropic SDK, Pydantic, and Pytest.

---

## 4. Run the tests (proves the code works, costs nothing)

```bash
pytest test_engine.py -v
```

Expected output: 5 tests, all `PASSED`. This uses the offline mock, so no
API key is needed and nothing is sent over the internet.

---

## 5. Try it from the command line (mock mode)

```bash
python engine.py "rm *.log"
```

You'll get back a JSON object describing the command — destructive: true,
scope: multiple_items, etc. This is the rule-based mock, not the real AI.

Try a few more:
```bash
python engine.py "ls -la"
python engine.py "chmod -R 777 /etc"
```

---

## 6. (Optional but recommended) Turn on the real AI

To get real reasoning instead of the rule-based mock, you need an Anthropic
API key.

1. Get a key from https://console.anthropic.com (Settings → API Keys).
2. Set it as an environment variable:
   - macOS / Linux:
     ```bash
     export ANTHROPIC_API_KEY="your-key-here"
     ```
   - Windows (PowerShell):
     ```powershell
     $env:ANTHROPIC_API_KEY="your-key-here"
     ```
3. Run the same command again:
   ```bash
   python engine.py "rm *.log"
   ```
   It will now say `[LIVE]` instead of `[MOCK]`, and the response will be
   real model reasoning, not a hardcoded rule.

This costs a small amount per call — fine for testing, keep an eye on it if
you're demoing repeatedly.

---

## 7. Run it as a server (so teammates can call it over HTTP)

This is what Person 3 (Risk Engine) and Person 5 (Frontend) will actually
talk to.

```bash
uvicorn api:app --reload --port 8001
```

Leave this running in its own terminal. In a **second terminal**, test it:

```bash
curl http://127.0.0.1:8001/health
```
Expected: `{"status":"ok"}`

```bash
curl -X POST http://127.0.0.1:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{"command":"rm *.log"}'
```
Expected: a JSON response with `"mode"` and `"result"` fields.

You can also open `http://127.0.0.1:8001/docs` in a browser — FastAPI
auto-generates an interactive test page there.

---

## 8. What your teammates need from you

The JSON shape in `engine.py` under `INTENT_SCHEMA_DESCRIPTION` is the
**contract**. Person 3 (Risk Engine) and Person 4 (Simulation) will write
code that expects exactly these fields:

```
intent, target_paths, resource_type, is_destructive, scope,
confidence, obfuscated, notes, raw_command
```

If you need to change a field name, message the team before you do —
changing this file breaks their code silently.

---

## 9. Common problems

**`ModuleNotFoundError: No module named 'anthropic'`**
→ Your venv isn't activated, or step 3 didn't finish. Re-run step 2's
activate command, then step 3.

**`command not found: python3`**
→ Try `python` instead of `python3`.

**Server won't start / port already in use**
→ Something else is using port 8001. Run
`uvicorn api:app --reload --port 8002` and use that port instead.

**Getting `[MOCK]` even though you set the API key**
→ You set the key in a different terminal window than the one you're
running the command in. Environment variables don't carry across terminals
— set it again in the terminal you're actually using.
