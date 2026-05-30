class PromptSandbox:
    max_prompt_chars = 4000

    def isolate(self, prompt: str) -> str:
        normalized = " ".join(prompt.split())
        bounded = normalized[: self.max_prompt_chars]
        return f"[SANDBOXED_ADVERSARIAL_EVALUATION_PROMPT]\n{bounded}"

