from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

SCANS = Path("data/scans")
PROCESSED = Path("data/processed")
RECIPES = Path("data/recipes")
OUTPUT = Path("output")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}

Confidence = Literal["high", "medium", "low"]


class Ingredient(BaseModel):
    model_config = ConfigDict(extra="forbid")
    quantity: str
    unit: str
    item: str
    original_text: str
    confidence: Confidence


class Step(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str
    confidence: Confidence


class Recipe(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    title_confidence: Confidence
    ingredients: list[Ingredient]
    method: list[Step]
    notes: str
    notes_confidence: Confidence
    status: Literal["needs_review", "approved"]


def scan_images() -> list[Path]:
    return sorted(p for p in SCANS.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)


def find_scan(name: str) -> Path | None:
    return next((p for p in scan_images() if p.stem == name), None)


def load_recipe(name: str) -> Recipe:
    return Recipe.model_validate_json((RECIPES / f"{name}.json").read_text())


def save_recipe(name: str, recipe: Recipe) -> None:
    (RECIPES / f"{name}.json").write_text(recipe.model_dump_json(indent=2))


def recipe_names() -> list[str]:
    return sorted(p.stem for p in RECIPES.glob("*.json"))
