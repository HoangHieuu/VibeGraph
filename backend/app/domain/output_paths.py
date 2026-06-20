from dataclasses import dataclass
from pathlib import Path


OUTPUT_DIRECTORY_NAME = ".vibegraph"
GRAPH_FILENAME = "graph.json"
CONTEXT_FILENAME = "context.md"
README_FILENAME = "README.generated.md"
WARNINGS_FILENAME = "warnings.json"

SCANNER_IGNORED_DIRECTORIES = frozenset({OUTPUT_DIRECTORY_NAME})


@dataclass(frozen=True, slots=True)
class OutputPaths:
    project_root: Path
    directory: Path
    graph: Path
    context: Path
    readme: Path
    warnings: Path

    @classmethod
    def for_project(cls, project_root: Path) -> "OutputPaths":
        resolved_root = project_root.expanduser().resolve()

        if not resolved_root.exists():
            raise ValueError(f"Project root does not exist: {resolved_root}")

        if not resolved_root.is_dir():
            raise ValueError(f"Project root is not a directory: {resolved_root}")

        directory = resolved_root / OUTPUT_DIRECTORY_NAME

        return cls(
            project_root=resolved_root,
            directory=directory,
            graph=directory / GRAPH_FILENAME,
            context=directory / CONTEXT_FILENAME,
            readme=directory / README_FILENAME,
            warnings=directory / WARNINGS_FILENAME,
        )
