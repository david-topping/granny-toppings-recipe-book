from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.datastructures import FormData

from toppings.recipe import (
    PROCESSED,
    SCANS,
    Ingredient,
    Recipe,
    Step,
    find_scan,
    load_recipe,
    recipe_names,
    save_recipe,
)

EXTRA_ROWS = 2

app = FastAPI()
app.mount("/processed", StaticFiles(directory=PROCESSED), name="processed")
app.mount("/scans", StaticFiles(directory=SCANS), name="scans")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def recipe_from_form(form: FormData, status: str) -> Recipe:
    ingredients = [
        Ingredient(
            quantity=form[f"ing-{i}-quantity"].strip(),
            unit=form[f"ing-{i}-unit"].strip(),
            item=form[f"ing-{i}-item"].strip(),
            original_text=form[f"ing-{i}-original_text"].strip(),
            confidence=form[f"ing-{i}-confidence"],
        )
        for i in range(int(form["ingredient_count"]))
    ]
    method = [
        Step(text=form[f"step-{i}-text"].strip(), confidence=form[f"step-{i}-confidence"])
        for i in range(int(form["step_count"]))
    ]
    return Recipe(
        title=form["title"].strip(),
        title_confidence=form["title_confidence"],
        ingredients=[i for i in ingredients if i.original_text or i.item],
        method=[s for s in method if s.text],
        notes=form["notes"].strip(),
        notes_confidence=form["notes_confidence"],
        status=status,
    )


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    recipes = [(name, load_recipe(name)) for name in recipe_names()]
    return templates.TemplateResponse(request, "index.html", {"recipes": recipes})


@app.get("/recipe/{name}", response_class=HTMLResponse)
def edit(request: Request, name: str) -> HTMLResponse:
    recipe = load_recipe(name)
    blank_ingredient = Ingredient(quantity="", unit="", item="", original_text="", confidence="high")
    context = {
        "name": name,
        "recipe": recipe,
        "ingredients": recipe.ingredients + [blank_ingredient] * EXTRA_ROWS,
        "steps": recipe.method + [Step(text="", confidence="high")] * EXTRA_ROWS,
        "scan": find_scan(name),
        "names": recipe_names(),
    }
    return templates.TemplateResponse(request, "recipe.html", context)


@app.post("/recipe/{name}")
async def save(request: Request, name: str) -> RedirectResponse:
    form = await request.form()
    statuses = {"approve": "approved", "unapprove": "needs_review"}
    status = statuses.get(form["action"], load_recipe(name).status)
    save_recipe(name, recipe_from_form(form, status))
    return RedirectResponse(f"/recipe/{name}?saved=1", status_code=303)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    print(f"review at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
