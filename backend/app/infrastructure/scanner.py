import os
from datetime import datetime, timezone
from pathlib import Path

from app.domain.graph_models import FileRecord, Language
from app.domain.output_paths import SCANNER_IGNORED_DIRECTORIES


SUPPORTED_EXTENSIONS: dict[str, Language] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
}

IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "__pycache__",
        ".next",
        "dist",
        "build",
        "coverage",
        ".cache",
        ".uv-cache",
        ".turbo",
        *SCANNER_IGNORED_DIRECTORIES,
    }
)

IGNORED_FILENAMES = frozenset(
    {
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "poetry.lock",
    }
)


def should_include_file(path: Path) -> bool:
    if path.name in IGNORED_FILENAMES:
        return False
    if path.name.endswith(".min.js") or path.suffix == ".map":
        return False
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def scan_repository(project_root: Path) -> list[FileRecord]:
    resolved_root = project_root.resolve()
    records: list[FileRecord] = []

    for current_root, directory_names, file_names in os.walk(resolved_root):
        directory_names[:] = sorted(
            name for name in directory_names if name not in IGNORED_DIRECTORIES
        )

        current_path = Path(current_root)
        for filename in sorted(file_names):
            absolute_path = current_path / filename
            if not should_include_file(absolute_path):
                continue

            stat = absolute_path.stat()
            content = absolute_path.read_text(encoding="utf-8", errors="replace")
            records.append(
                FileRecord(
                    path=absolute_path.relative_to(resolved_root).as_posix(),
                    language=SUPPORTED_EXTENSIONS[absolute_path.suffix.lower()],
                    loc=len(content.splitlines()),
                    size_bytes=stat.st_size,
                    last_modified=datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ).isoformat(),
                )
            )

    return records
