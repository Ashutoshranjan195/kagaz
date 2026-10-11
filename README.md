# Kagaz 🍂 — Printable Nature Scavenger Hunts for Kids

An offline-first, privacy-focused AI application that generates printable bilingual (Hindi + English) nature scavenger hunts for children. 

A parent or teacher selects a **city**, **child age group**, and **month**. Kagaz uses local open-weights language models via Ollama and seasonal weather history to produce a tailored outdoor scavenger hunt rendered directly onto an A4 printable PDF.

---

## Key Highlights

- 🔒 **100% Offline & Private:** Runs entirely locally via Ollama. No child or location data ever leaves the machine.
- 🇮🇳 **True Bilingual Generation:** Uses Devanagari script for Hindi translations paired with English instructions and child-friendly hints.
- 🌦️ **Seasonal Intelligence:** Filters activities using historical weather conditions (temperature, humidity, rainfall) via TabPFN with pandas fallback.
- 🖨️ **Print-Ready PDFs:** Formats clean, single-page A4 scavenger hunt checklists with checkboxes, hints, emojis, bonus family challenges, and parent safety notes.
- 🆓 **Zero Cloud Costs:** Perfect for schools, NGOs, and parents without API keys or subscriptions.

---

## Tech Stack

- **Runtime:** Python 3.13
- **Local LLM Engine:** [Ollama](https://ollama.com/) (`qwen2.5:7b` / `gemma2:2b`)
- **Document Generation:** ReportLab (with Noto Sans Devanagari & Segoe UI Emoji support)
- **Interactive UI:** Streamlit
- **ML / Seasonal Filter:** TabPFN & pandas
- **Configuration & Validation:** PyYAML, Pydantic, python-dotenv, Pytest

---

## Project Structure

```
kagaz/
├── app/
│   └── streamlit_app.py      # Interactive web dashboard
├── assets/
│   └── fonts/                # Devanagari TTF fonts (auto-downloaded)
├── data/
│   ├── raw/                  # Historical weather CSV
│   └── processed/
├── output/                   # Generated printable PDFs
├── scripts/
│   └── test_generation.py    # CLI generation script
├── src/
│   ├── config.py             # App configuration loader
│   ├── hunt_generator.py     # End-to-end hunt orchestration
│   ├── ollama_client.py      # Ollama API client & retry logic
│   ├── pdf_builder.py        # ReportLab PDF layout & font styling
│   ├── prompts.py            # System & user prompt templates
│   ├── tabpfn_filter.py      # Seasonal item type classifier
│   └── utils.py              # Hunt validation and safety checks
├── tests/
│   └── test_generator.py     # Unit and validation tests
├── config.yaml               # Default system settings
├── requirements.txt          # Python dependencies
└── README.md
```

---

## Getting Started

### 1. Prerequisites
- Python 3.13+ installed on your system.
- [Ollama](https://ollama.com/) installed and running.
- Pull the model:
  ```bash
  ollama pull qwen2.5:7b
  ```
  *(Or `ollama pull gemma2:2b` if using lighter hardware)*

### 2. Installation

Clone the repository and set up a virtual environment:

```powershell
git clone https://github.com/Ashutoshranjan195/kagaz.git
cd kagaz

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Ensure `.env` contains:
```env
MODEL_NAME=qwen2.5:7b
```

---

## Usage

### Run via Interactive Web App
Launch the Streamlit web interface:

```powershell
streamlit run app\streamlit_app.py
```

### Run via Command Line
Generate a hunt directly using the CLI:

```powershell
python scripts\test_generation.py --city Pune --age 6-8 --month October --n 6
```

Generated PDFs are saved into the `output\` directory:
```
output/kagaz_pune_october_<timestamp>.pdf
```

---

## Running Tests

Execute the test suite using pytest:

```powershell
python -m pytest tests/test_generator.py -v --tb=short
```

---

## Safety & Content Guidelines

Safety is enforced via a strict verification pipeline:
- **No Dangerous Interactions:** Hard stop checks prevent prompts suggesting touching, tasting, eating, or picking unfamiliar plants, mushrooms, berries, or insects.
- **Pure Observation & Safe Gathering:** Activities are restricted to spotting, listening, smelling, counting, texturing, or collecting fallen safe items (dry leaves, twigs, small stones).
- **Device-Free Fun:** Prompts strictly avoid anything requiring screens, apps, or purchases.

---

## License

This project is licensed under the MIT License.
