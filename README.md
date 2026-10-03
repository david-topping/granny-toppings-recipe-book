# Granny Topping's Recipe Book

Turns photos of Granny's handwritten recipe cards into a printable cookbook.

## Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Run `uv sync`.
3. Run `cp .env.example .env` and put your Anthropic API key in `.env`.
4. Run `export UV_ENV_FILE=.env` so `uv run` loads the key. Do this in each new terminal.

## Usage

1. Copy card photos into `data/scans/` (JPG, PNG, TIFF or WEBP). They are never modified.
2. `uv run toppings preprocess` straightens, crops and cleans each photo into `data/processed/`. Check the results there.
3. `uv run toppings transcribe` sends new cards to Claude and saves one JSON per card in `data/recipes/`. This costs money. It waits until the batch finishes. If you stop it, run it again to resume the same batch.
4. `uv run toppings review`, then open http://127.0.0.1:8000. Correct each recipe against the photo and click **Save and approve**. Yellow fields are medium confidence, red are low, and `[illegible]` marks words Claude couldn't read.
5. `uv run toppings export` writes the approved recipes to `output/cookbook.html`.
6. Open `output/cookbook.html` in a browser, print it and choose **Save as PDF**. Keep `output/scans/` next to the HTML file.

Every command skips work already done, so after adding new photos, run all the steps again.

## Development

`uv run ruff format && uv run ruff check --fix`
