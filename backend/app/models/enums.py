from enum import Enum


class EvaluationStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class AttackCategory(str, Enum):
    jailbreak = "jailbreak"
    injection = "injection"
    toxicity = "toxicity"
    hallucination = "hallucination"
    bias = "bias"


class UserRole(str, Enum):
    admin = "admin"
    evaluator = "evaluator"
    viewer = "viewer"
