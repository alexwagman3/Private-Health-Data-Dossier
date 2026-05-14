# Biomarker Brief

A Jupyter notebook that turns a stack of lab PDFs into a plain-English
briefing you can hand to your doctor. Runs entirely on your laptop. No
account, no API keys, no telemetry.

> ## ⚠️ Not medical advice
>
> **This is an educational tool.** It cannot diagnose, treat, or replace a
> clinician. **Bring the output to your doctor — do not act on it.**
> Reference ranges vary by lab, age, sex, and clinical context. A
> "flagged" value here may be normal for you, and a "normal" value here
> may not be.

---

## What it does

You drop your lab PDFs (Quest, LabCorp, Function Health, generic CSV from
a patient portal) into `data/sample_labs/`. You run eight cells. Out the
other end you get three artifacts in `./output/`:

- **`brief.md`** — a short, plain-English summary of what stood out and a
  list of questions for your next doctor's appointment, written by a
  local LLM.
- **`trends.png`** — a grid of trend charts for every biomarker measured
  on at least two dates, with the optimal range shaded.
- **`flagged_markers.csv`** — a flat table of every parsed result with
  its severity classification, so you can sort and filter in a
  spreadsheet.

The notebook also catches **worsening-but-still-in-range trends** — the
kind of slow drift that single-snapshot review misses.

---

## Privacy: your labs never leave your laptop

Every step of the pipeline runs on your machine:

| Step | Where it runs |
| --- | --- |
| PDF text extraction (`pdfplumber`) | Local Python |
| Regex parsing of result lines | Local Python |
| Normalizing vendor names → canonical names | Local Python + `biomarker_reference.json` |
| Flagging out-of-range values | Local Python |
| Trend plotting | Local matplotlib |
| Per-marker explanations + executive summary | **Local LLM via Ollama** |
| Export | Local filesystem |

The only network requests this tool makes during normal use go to
`http://localhost:11434` — that's your own Ollama server, on your
machine. There is no cloud LLM, no external API, no analytics, no
account.

The single exception is the initial `pip install -r requirements.txt` and
the one-time `ollama pull <model>` to fetch the model weights. After
that, you can run the notebook on a fully air-gapped machine.

---

## Setup (about 10 minutes, one time)

### 1. Install Ollama

Ollama is a small program that runs open-source LLMs locally.

| OS | Install |
| --- | --- |
| macOS | Download from [ollama.com](https://ollama.com) |
| Windows | Download from [ollama.com](https://ollama.com) |
| Linux | `curl -fsSL https://ollama.com/install.sh \| sh` then `ollama serve` |

Once installed, Ollama runs in the background and exposes an HTTP API at
`http://localhost:11434`.

### 2. Pull a model

```bash
ollama pull llama3.2
```

`llama3.2` (~2 GB) is small, fast, and a fine default. For appreciably
better medical reasoning at the cost of memory and speed, try one of
these:

```bash
ollama pull llama3.1:8b      # ~5 GB, much stronger summaries
ollama pull qwen2.5:14b      # ~9 GB, slower but better at nuance
ollama pull meditron:7b      # community medical-tuned model
```

You can change `OLLAMA_MODEL` in **Cell 1** to point at whichever one you
pulled.

### 3. Install Python dependencies

```bash
git clone https://github.com/alexwagman3/private-health-data-dossier.git
cd private-health-data-dossier
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
```

### 4. Run the notebook

```bash
jupyter notebook notebooks/biomarker_brief.ipynb
```

Run the cells top to bottom. The first time, the LLM brief (Cell 7) is
the slow step — expect 30 – 120 seconds depending on your model and
hardware.

---

## How to add your own labs

1. Put your lab PDFs in `data/sample_labs/`. The included samples are
   100% synthetic — feel free to delete them once you've seen the
   pipeline work.
2. The notebook will pick up any `.pdf` or `.csv` it finds. There's a
   secondary folder `data/sample_csv/` with an example portal-export
   CSV — point Cell 2's `DATA_DIR` there if you have a CSV instead of a
   PDF.
3. Re-run cells 2 onward.

If a vendor's layout is too weird for the regex parser, the notebook
automatically asks the local LLM to extract rows as a fallback (Cell 3).

### Adding markers to the reference

`data/biomarker_reference.json` ships with ~60 common markers (lipid
panel, CMP, CBC, thyroid, hormones, vitamins, inflammation). To add
more, append an entry of the form:

```json
{
  "canonical_name": "Your Marker",
  "also_known_as": ["Alt Name 1", "Alt Name 2"],
  "unit": "mg/dL",
  "optimal_range": [10, 50],
  "clinical_range": [5, 100],
  "what_it_measures": "...",
  "why_it_matters": "...",
  "category": "metabolic"
}
```

`also_known_as` is the most important field — it's how vendor-specific
names get matched back to a canonical one.

---

## Local Jupyter vs. Google Colab

You can run this notebook in [Google Colab](https://colab.research.google.com/),
and it will work — but the privacy story changes:

| | Local Jupyter | Colab |
| --- | --- | --- |
| Where your PDFs live during processing | Your laptop | Google's servers, in a temporary VM |
| Where the LLM runs | Your laptop | Google's servers |
| Persists after you close the tab | Yes, in `./output/` | No — VM is wiped |
| Works offline | Yes | No |
| Free GPU | Whatever you have | Yes, T4 |

**Local Jupyter is the recommended default.** Your data never touches
anyone else's machine. Colab is acceptable for trying it out or for
people without a usable local Python environment, but the temporary VM
is still someone else's hardware. If you go the Colab route, make a
private copy of the notebook (`File → Save a copy in Drive`) before
running anything.

---

## Repository layout

```
.
├── notebooks/
│   └── biomarker_brief.ipynb       # The pipeline. 8 code cells.
├── data/
│   ├── biomarker_reference.json    # Canonical marker names + ranges + explanations
│   ├── sample_labs/                # Fake lab PDFs (3 vendors, 3 dates)
│   │   ├── _generate_samples.py    # Re-run to regenerate the PDFs
│   │   ├── labs_2024-03-04_quest.pdf
│   │   ├── labs_2024-09-18_labcorp.pdf
│   │   └── labs_2025-04-22_function.pdf
│   └── sample_csv/
│       └── example_portal_export.csv
├── output/                          # Cell 8 writes here
├── requirements.txt
└── README.md
```

---

## Sources for the reference ranges

`biomarker_reference.json` cites these public sources:

- **NIH National Library of Medicine — MedlinePlus Lab Test Information**
  (<https://medlineplus.gov/lab-tests/>)
- **Mayo Clinic — Tests & Procedures**
  (<https://www.mayoclinic.org/tests-procedures>)
- **American Heart Association — Cholesterol guidelines**
  (<https://www.heart.org/en/health-topics/cholesterol>)
- **American Diabetes Association — Standards of Care**
  (<https://diabetes.org/about-diabetes/diagnosis>)
- **American Thyroid Association — Thyroid Function Tests**
  (<https://www.thyroid.org/thyroid-function-tests/>)

These references describe *typical adult* ranges. Your lab prints its
own reference range on every report — that is the authoritative number
for your sample. This tool gives you a consistent overlay across labs;
your clinician gives you the interpretation.

---

## What this brief is not

It is not a diagnosis. It is not a treatment plan. It is not a
substitute for a clinician's eye on your record. It is a structured way
to read your own labs, see what's drifting, and walk into your next
appointment with sharper questions.

If a value here genuinely worries you, call your doctor — not the
notebook.
