from dataclasses import dataclass

from app.models.enums import AttackCategory


@dataclass(frozen=True)
class AttackPrompt:
    category: AttackCategory
    prompt: str
    difficulty: int


class AttackEngine:
    def generate(self, categories: list[AttackCategory | str], dataset: list[dict]) -> list[AttackPrompt]:
        prompts: list[AttackPrompt] = []
        wanted = {category.value if isinstance(category, AttackCategory) else category for category in categories}
        for item in dataset:
            if item["category"] in wanted:
                prompts.append(
                    AttackPrompt(
                        category=AttackCategory(item["category"]),
                        prompt=item["prompt"],
                        difficulty=int(item.get("difficulty", 1)),
                    )
                )
        return prompts
