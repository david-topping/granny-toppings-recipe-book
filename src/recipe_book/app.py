import re
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.datastructures import FormData

from recipe_book.recipe import (
    Chapter,
    Ingredient,
    Recipe,
    Source,
    chapter_paths,
    load_chapter,
    save_chapter,
)

IMAGES = Path("data/processed")
FIELDS = ["quantity", "unit", "item", "preparation", "note"]
EXTRA_ROWS = 3

app = FastAPI()
app.mount("/images", StaticFiles(directory=IMAGES), name="images")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def all_recipes() -> list[tuple[Path, Chapter, Recipe]]:
    return [
        (path, chapter, recipe)
        for path in chapter_paths()
        for chapter in [load_chapter(path)]
        for recipe in chapter.recipes
    ]


def lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def recipe_from_form(form: FormData, recipe_id: str, approved: bool) -> Recipe:
    rows = [
        {field: form.get(f"ing-{n}-{field}", "").strip() for field in FIELDS}
        for n in range(int(form["ingredient_count"]))
    ]
    return Recipe(
        id=recipe_id,
        title=form["title"].strip(),
        makes=form["makes"].strip(),
        ingredients=[Ingredient(**row) for row in rows if row["item"]],
        method=[s.strip() for s in form.getlist("method") if s.strip()],
        notes=[s.strip() for s in form.getlist("notes") if s.strip()],
        source=Source(pages=re.findall(r"IMG_\d+", form["pages"]), note=form["source_note"].strip()),
        checks=lines(form["checks"]),
        approved=approved,
    )


@app.get("/", response_class=HTMLResponse)
def index(request: Request, show: str = "") -> HTMLResponse:
    chapters = [load_chapter(path) for path in chapter_paths()]
    recipes = [r for c in chapters for r in c.recipes]
    approved = sum(r.approved for r in recipes)
    shown = [(c.title, [r for r in c.recipes if show != "todo" or not r.approved]) for c in chapters]
    context = {
        "chapters": [(t, rs) for t, rs in shown if rs],
        "approved": approved,
        "total": len(recipes),
        "show": show,
    }
    return templates.TemplateResponse(request, "index.html", context)


@app.get("/recipe/{recipe_id}", response_class=HTMLResponse)
def edit(request: Request, recipe_id: str) -> HTMLResponse:
    recipes = all_recipes()
    ids = [r.id for _, _, r in recipes]
    if recipe_id not in ids:
        raise HTTPException(404)
    position = ids.index(recipe_id)
    _, chapter, recipe = recipes[position]
    context = {
        "recipe": recipe,
        "chapter": chapter.title,
        "ingredients": [i.model_dump() for i in recipe.ingredients] + [dict.fromkeys(FIELDS, "")] * EXTRA_ROWS,
        "method": recipe.method + [""] * EXTRA_ROWS,
        "notes": recipe.notes + [""],
        "previous": ids[position - 1] if position > 0 else None,
        "next": ids[position + 1] if position < len(ids) - 1 else None,
    }
    return templates.TemplateResponse(request, "recipe.html", context)


@app.post("/recipe/{recipe_id}")
async def save(request: Request, recipe_id: str) -> RedirectResponse:
    form = await request.form()
    for path, chapter, recipe in all_recipes():
        if recipe.id == recipe_id:
            approved = {"approve": True, "unapprove": False}.get(form["action"], recipe.approved)
            index = [r.id for r in chapter.recipes].index(recipe_id)
            chapter.recipes[index] = recipe_from_form(form, recipe_id, approved)
            save_chapter(path, chapter)
            return RedirectResponse(f"/recipe/{recipe_id}?saved=1", status_code=303)
    raise HTTPException(404)


def main() -> None:
    print("review at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
