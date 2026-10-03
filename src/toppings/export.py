import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from toppings.recipe import OUTPUT, find_scan, load_recipe, recipe_names

TITLE = "Granny Topping's Recipes"


def run() -> None:
    # 1. Collect approved recipes
    approved = [(name, load_recipe(name)) for name in recipe_names()]
    approved = sorted(((n, r) for n, r in approved if r.status == "approved"), key=lambda nr: nr[1].title.lower())
    if not approved:
        print("no approved recipes yet, run `uv run toppings review` first")
        return

    # 2. Copy original scans next to the cookbook
    images = OUTPUT / "scans"
    images.mkdir(parents=True, exist_ok=True)
    entries = []
    for name, recipe in approved:
        scan = find_scan(name)
        if scan:
            shutil.copy2(scan, images / scan.name)
        entries.append({"recipe": recipe, "scan": f"scans/{scan.name}" if scan else None})

    # 3. Render the cookbook
    env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"), autoescape=True)
    html = env.get_template("cookbook.html").render(title=TITLE, entries=entries)
    out = OUTPUT / "cookbook.html"
    out.write_text(html)
    print(f"wrote {len(entries)} recipes to {out}, open it in a browser and print to PDF")
