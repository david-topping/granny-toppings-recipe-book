# Granny Topping's Recipe Book

Granny's handwritten recipes (some water-damaged, stained or faded) as structured JSON, with a web app to check, edit and approve each one beside its page photo.

## Code style

- Clear, concise and easy to read. Do not over-engineer: no unnecessary classes, abstractions or config layers.
- No docstrings. No comments except short high-level step markers (e.g. `# 1. Load image`).
- Type hints on function signatures.
- Small number of flat modules in `src/toppings/`.
- Format and lint with ruff: `uv run ruff format && uv run ruff check --fix`.

## Project

- Python 3.12, managed with uv. `uv run toppings` starts the review app (FastAPI + Jinja templates, plain HTML and minimal CSS, no JS framework) at http://127.0.0.1:8000.
- `recipes/NN-<chapter-id>.json`: one file per chapter, in book order, the source of truth. The structure is the Pydantic models in `src/toppings/recipe.py` (`Chapter` → `Recipe` → `Ingredient`); keep every recipe in that shape and load/save through those models.
- Book content: `title`, `makes`, `ingredients` (one flat list), `method`, `notes`, ingredient `note`. No ingredient sections: name parts of a recipe in the method ("For the topping, …"), and if an ingredient is used in two parts, say which in its `preparation` ("for the topping"). Never invent a method step for a part that has none; add a check instead. Review-only: `checks` (e.g. "amount faded"), `source`, `approved`. Never put review remarks in book fields.
- `id` is a stable slug, unique across the book; don't change it when a title is edited.
- Units are singular and consistent (oz, lb, pt, tsp, tbsp, cup, "level tsp", "small tin").
- `save_chapter` writes `json.dumps(indent=2, ensure_ascii=False)` plus a trailing newline; saving an unedited recipe must leave the file byte-identical.
- `data/processed/IMG_xxxx.jpg` page photos shown in the app. `data/scans/` original HEIC photos, never modified.
- Preserve Granny's wording, quantities and units; never invent anything not on the page.
