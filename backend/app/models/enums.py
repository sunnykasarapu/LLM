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
    privacy_leakage = "privacy_leakage"
    misinformation = "misinformation"
    adversarial = "adversarial"
    csam_avoidance = "csam_avoidance"


class UserRole(str, Enum):
    admin = "admin"
    evaluator = "evaluator"
    viewer = "viewer"
