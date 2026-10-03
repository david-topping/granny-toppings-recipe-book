import base64
import json
import time
from pathlib import Path

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request
from pydantic import ValidationError

from toppings.recipe import PROCESSED, RECIPES, Recipe, save_recipe

MODEL = "claude-sonnet-5-5"
PENDING = Path("data/pending_batch.json")
POLL_SECONDS = 30

SYSTEM_PROMPT = """You are transcribing a photo of a handwritten family recipe card written by the user's late grandmother. \
Some cards have water damage, stains and faded ink. Faithfulness matters far more than tidiness: this is a keepsake, not a modernised recipe.

Rules:
- Preserve her original wording, spelling, abbreviations, punctuation and units exactly as written (e.g. "1 teacup", "2 oz", "a knob of", "mod. oven"). Do not convert, expand, correct or modernise anything.
- If a word or number cannot be read with confidence, write [illegible] in its place. Never guess or fill in what seems likely, even when it seems obvious from context.
- Stains, water marks and creases are not ink. Do not read marks as letters unless they are clearly handwriting.
- title: the recipe name as written. If there is none, use [illegible] or a blank string.
- ingredients: one entry per line. original_text is the full line exactly as written. quantity, unit and item split that same text without changing it; use an empty string for any part that is absent.
- method: one entry per step or sentence-group as she wrote it, keeping her wording.
- notes: anything else on the card (oven temperatures written in margins, serving notes, who the recipe came from). Empty string if none.
- confidence for each field: "high" if every word is clearly legible, "medium" if any part was hard to read, "low" if it contains [illegible] or is mostly uncertain.
- status: always "needs_review"."""


def build_request(custom_id: str, image: Path) -> Request:
    data = base64.standard_b64encode(image.read_bytes()).decode()
    return Request(
        custom_id=custom_id,
        params=MessageCreateParamsNonStreaming(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            output_config={"format": {"type": "json_schema", "schema": anthropic.transform_schema(Recipe)}},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": data}},
                        {"type": "text", "text": "Transcribe this recipe card."},
                    ],
                }
            ],
        ),
    )


def submit(client: anthropic.Anthropic) -> dict | None:
    pending = [p for p in sorted(PROCESSED.glob("*.jpg")) if not (RECIPES / f"{p.stem}.json").exists()]
    if not pending:
        return None
    names = {f"card-{i}": p.stem for i, p in enumerate(pending)}
    requests = [build_request(custom_id, PROCESSED / f"{name}.jpg") for custom_id, name in names.items()]
    batch = client.messages.batches.create(requests=requests)
    job = {"batch_id": batch.id, "names": names}
    PENDING.write_text(json.dumps(job, indent=2))
    print(f"submitted batch {batch.id} with {len(names)} cards")
    return job


def save_results(client: anthropic.Anthropic, job: dict) -> None:
    for result in client.messages.batches.results(job["batch_id"]):
        name = job["names"][result.custom_id]
        if result.result.type != "succeeded":
            print(f"{name}: {result.result.type}")
            continue
        message = result.result.message
        if message.stop_reason != "end_turn":
            print(f"{name}: stopped with {message.stop_reason}")
            continue
        text = next((b.text for b in message.content if b.type == "text"), "")
        try:
            recipe = Recipe.model_validate_json(text)
        except ValidationError as e:
            print(f"{name}: invalid response\n{e}")
            continue
        recipe.status = "needs_review"
        save_recipe(name, recipe)
        print(f"{name}: saved")


def run() -> None:
    client = anthropic.Anthropic()
    RECIPES.mkdir(parents=True, exist_ok=True)

    # 1. Resume a pending batch or submit a new one
    job = json.loads(PENDING.read_text()) if PENDING.exists() else submit(client)
    if job is None:
        print("nothing to transcribe")
        return

    # 2. Wait for the batch to finish
    while (batch := client.messages.batches.retrieve(job["batch_id"])).processing_status != "ended":
        print(f"waiting... {batch.request_counts.processing} cards still processing")
        time.sleep(POLL_SECONDS)

    # 3. Validate and save each recipe
    save_results(client, job)
    PENDING.unlink()
