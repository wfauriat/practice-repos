# python-data-notebook

A reproducible Jupyter project layout: notebooks for exploration, `src/` for reusable code, parametrised runs via papermill, tests on the reusable bits.

## When to reach for this

- You have **data work** to do and want it to be reproducible by future-you.
- You want notebooks but don't want them to become uneditable graveyards.
- You want a starting point that already demonstrates how to **factor reusable code out of a notebook**.

If you need a web service: `python-fastapi-crud`. If you need a CLI: `python-cli-typer`.

## Layout

```
notebooks/        # The exploratory work (numbered 01-, 02-, ...)
└── 01-eda.ipynb
src/              # Reusable code that notebooks import
├── __init__.py
└── loaders.py    # Data loading + light cleaning
data/             # Local data dir (gitignored except .gitkeep)
tests/            # Yes, test the reusable code
└── test_loaders.py
```

The split is the point. Anything you'd copy-paste between notebooks moves into `src/`; the notebook is the *narrative* that calls it.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# Run the notebook end-to-end (great for CI / regression checks)
jupyter nbconvert --to notebook --execute notebooks/01-eda.ipynb \
  --output 01-eda.executed.ipynb

# Or open it interactively
jupyter lab notebooks/

# Run the tests on src/
pytest
```

With `just`:

```bash
just install
just nb        # execute the EDA notebook in-place
just lab       # open Jupyter Lab
just test
```

## Design notes

- **Numbered notebooks**: `01-eda.ipynb`, `02-feature-engineering.ipynb`, ... so the read order is obvious.
- **`src/` is a real package**: notebooks import via `from src.loaders import ...`. Don't dump utility code in the notebook itself unless it's strictly part of *that* analysis's narrative.
- **Test the loaders / utilities, not the notebook**. Notebooks change too often. Pinning the loader contract via tests is what gives you confidence.
- **Papermill** is included for parametrised re-runs (e.g. running the same notebook over different time windows). Use `papermill notebooks/01-eda.ipynb out.ipynb -p tag value`.
- **`data/` is gitignored** by default. Real data should never sit in git; document where to fetch it in the notebook itself.

## When not to keep it as a notebook

If the analysis is going to run on a schedule, get unit-tested, or be embedded in a service — port it to a Python module. Notebooks are scratch paper, not production.
