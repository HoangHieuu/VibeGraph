from dataclasses import asdict, dataclass
from typing import Any, Literal


ContextMode = Literal["offline", "enhanced", "fallback"]


@dataclass(frozen=True, slots=True)
class ContextPackOptions:
    max_files: int = 8
    max_depth: int = 2
    include_tests: bool = True
    include_config: bool = False
    include_docs: bool = False


@dataclass(frozen=True, slots=True)
class ContextRecommendation:
    path: str
    reason: str
    score: float


@dataclass(frozen=True, slots=True)
class ContextEnhancement:
    rationale: str
    prompt: str
    reasons: dict[str, str]


@dataclass(frozen=True, slots=True)
class ContextPack:
    task: str
    mode: ContextMode
    model: str | None
    recommendations: tuple[ContextRecommendation, ...]
    prompt: str
    mentions: str
    estimated_tokens: int
    reduction_percent: int
    provider_message: str
    artifact_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "mode": self.mode,
            "model": self.model,
            "recommendations": [
                asdict(recommendation)
                for recommendation in self.recommendations
            ],
            "prompt": self.prompt,
            "mentions": self.mentions,
            "estimatedTokens": self.estimated_tokens,
            "reductionPercent": self.reduction_percent,
            "providerMessage": self.provider_message,
            "artifactPath": self.artifact_path,
        }
