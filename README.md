# Granny Topping's Recipe Book

Granny's handwritten recipes as structured JSON, with a small web app to check each one against the original page photo, edit it and approve it.

## Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Run `uv sync`.

## Usage

1. Run `uv run toppings`, then open http://127.0.0.1:8000.
2. Click a recipe. The page photo is on the left and the recipe's fields are on the right. The yellow **Checks** box lists anything to verify, such as a faded amount.
3. Correct the fields against the photo, delete each check once it's resolved, then click **Save and approve**. Use the blank rows to add ingredients, steps or notes, and clear a row to remove it. Use **Next** to move through the book.
4. Click **Still to approve** on the list page to see what's left.

Press Ctrl+C in the terminal to stop the app.

## Files

- `recipes/` one JSON file per chapter; the number prefix (`01-`, `02-`…) gives the chapter order and recipes are in book order within each file. The structure is defined in `src/toppings/recipe.py` and checked on every save:

  ```json
  {
    "id": "jams-and-preserves",
    "title": "Jams and Preserves",
    "recipes": [
      {
        "id": "caramel-slices",
        "title": "Caramel Slices",
        "makes": "",
        "ingredients": [
          {"quantity": "4", "unit": "oz", "item": "marg", "preparation": "for the base", "note": ""},
          {"quantity": "4", "unit": "oz", "item": "marg", "preparation": "for the caramel", "note": ""}
        ],
        "method": ["For the base, cream the marg and caster sugar. Add the flour and baking powder.", "..."],
        "notes": [],
        "source": {"pages": ["IMG_0370"], "note": ""},
        "checks": [],
        "approved": false
      }
    ]
  }
  ```

  For the book, use `title`, `makes`, `ingredients` (one flat list; a line is `quantity unit item, preparation (note)`), `method` and `notes`. Parts of a recipe such as a base or topping are named in the method steps ("For the topping, …"), and an ingredient used in more than one part says which in its `preparation`. `source` says which page photo a recipe came from. `checks` are review notes such as "amount faded" and are not for printing. `id` is a stable slug for links and file names.
- `data/processed/` the page photos shown in the app.
- `data/scans/` the original iPhone photos (HEIC).

## Development

`uv run ruff format && uv run ruff check --fix`
