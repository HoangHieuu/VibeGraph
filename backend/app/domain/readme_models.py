from dataclasses import dataclass
from typing import Any, Literal


ReadmeMode = Literal["offline", "enhanced", "fallback"]


@dataclass(frozen=True, slots=True)
class ReadmeModule:
    name: str
    summary: str
    files: tuple[str, ...]
    entrypoints: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "summary": self.summary,
            "files": list(self.files),
            "entrypoints": list(self.entrypoints),
        }


@dataclass(frozen=True, slots=True)
class ReadmeEnhancement:
    overview: str
    architecture: str
    module_summaries: dict[str, str]
    rationale: str


@dataclass(frozen=True, slots=True)
class ReadmeDocument:
    mode: ReadmeMode
    model: str | None
    project_name: str
    overview: str
    architecture: str
    modules: tuple[ReadmeModule, ...]
    entrypoints: tuple[str, ...]
    key_files: tuple[str, ...]
    commands: tuple[str, ...]
    warnings: tuple[str, ...]
    mermaid: str
    markdown: str
    provider_message: str
    artifact_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "model": self.model,
            "projectName": self.project_name,
            "overview": self.overview,
            "architecture": self.architecture,
            "modules": [module.to_dict() for module in self.modules],
            "entrypoints": list(self.entrypoints),
            "keyFiles": list(self.key_files),
            "commands": list(self.commands),
            "warnings": list(self.warnings),
            "mermaid": self.mermaid,
            "markdown": self.markdown,
            "providerMessage": self.provider_message,
            "artifactPath": self.artifact_path,
        }
