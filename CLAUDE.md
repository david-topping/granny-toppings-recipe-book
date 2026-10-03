# Granny Topping's Recipe Book

Digitises handwritten recipe cards (some water-damaged, stained or faded) into a printable cookbook.

## Code style

- Clear, concise and easy to read. Do not over-engineer: no unnecessary classes, abstractions or config layers.
- No docstrings. No comments except short high-level step markers (e.g. `# 1. Load image`).
- Type hints on function signatures.
- Small number of flat modules in `src/toppings/`.
- Format and lint with ruff: `uv run ruff format && uv run ruff check --fix`.

## Project

- Python 3.12, managed with uv. CLI: `uv run toppings preprocess | transcribe | review | export`.
- `ANTHROPIC_API_KEY` from the environment. Model: `claude-sonnet-5-5`.
- `data/scans/` originals, never modified. `data/processed/` preprocessed images. `data/recipes/` one JSON per recipe (named after the scan's file stem). `output/` the finished cookbook.
- Preprocessing must never binarise: it turns stains into ink.
- Transcription preserves granny's wording and units exactly, marks unreadable words `[illegible]` and never guesses.
- Do not call the Anthropic API (transcribe) without asking the user first.
