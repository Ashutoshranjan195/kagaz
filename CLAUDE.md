# Kagaz — Project Rules

## What this is
An offline-first AI tool that generates printable nature scavenger hunts 
for kids. Parent enters city + age + month, a local Gemma model (via Ollama) 
generates a hunt in Hindi+English, TabPFN (optional) filters which item 
types are seasonally likely, and ReportLab produces a printable PDF.

## Stack
- Python 3.13 on Windows 11, CMD shell
- Ollama (gemma2:2b) via the official `ollama` Python package
- TabPFN (OPTIONAL — must gracefully fall back to pandas if unavailable)
- ReportLab for PDF
- Streamlit for UI
- PyYAML for config

## Hard rules
- All model calls go through src/ollama_client.py. Never call Ollama 
  directly from any other module.
- Model must return valid JSON. Enforce with format="json" in the Ollama 
  call, and retry exactly once with a stricter reminder if json.loads fails.
  Raise ModelJSONError on second failure.
- Prompts live only in src/prompts.py. Never inline prompt strings elsewhere.
- Config (model name, temperature, paths) lives in config.yaml; env vars in 
  .env override it. Use pathlib.Path everywhere — no os.path, no forward-slash 
  strings.
- Safety: no hunt item may suggest touching, eating, tasting, or picking 
  unknown plants, mushrooms, berries, or insects. There is a 
  validate_hunt() safety hard-stop with a forbidden-words list.
- Never commit data/raw or output/*.pdf. Add them to .gitignore.
- Every new public function gets a one-line docstring.
- All terminal instructions you give me must be Windows CMD syntax.

## Workflow
- When I ask for a new feature: check this file first, propose a short plan, 
  wait for "ok", then write code.
- After writing any file, show the diff and wait for my "ok" before moving on.
- Do not invent APIs. If unsure about a package's current API, ask me or 
  use the installed version in requirements.txt.