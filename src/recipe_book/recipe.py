import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict

RECIPES = Path("recipes")


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Ingredient(Model):
    quantity: str = ""
    unit: str = ""
    item: str
    preparation: str = ""
    note: str = ""


class Source(Model):
    pages: list[str]
    note: str = ""


class Recipe(Model):
    id: str
    title: str
    makes: str = ""
    ingredients: list[Ingredient]
    method: list[str]
    notes: list[str]
    source: Source
    checks: list[str]
    approved: bool = False


class Chapter(Model):
    id: str
    title: str
    recipes: list[Recipe]


def chapter_paths() -> list[Path]:
    return sorted(RECIPES.glob("*.json"))


def load_chapter(path: Path) -> Chapter:
    return Chapter.model_validate_json(path.read_text())


def save_chapter(path: Path, chapter: Chapter) -> None:
    path.write_text(json.dumps(chapter.model_dump(), indent=2, ensure_ascii=False) + "\n")
