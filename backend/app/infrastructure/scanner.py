import os
import re
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


def _gitignore_to_regex(
    body: str, anchored: bool, dir_only: bool
) -> re.Pattern[str]:
    index = 0
    length = len(body)
    pattern = ""
    while index < length:
        character = body[index]
        if character == "*":
            if index + 1 < length and body[index + 1] == "*":
                if index + 2 < length and body[index + 2] == "/":
                    pattern += "(?:.*/)?"
                    index += 3
                    continue
                pattern += ".*"
                index += 2
                continue
            pattern += "[^/]*"
            index += 1
            continue
        if character == "?":
            pattern += "[^/]"
            index += 1
            continue
        pattern += re.escape(character)
        index += 1
    prefix = "^" if anchored else "(?:^|.*/)"
    # A matched entry also ignores everything nested beneath it.
    _ = dir_only
    suffix = "(?:/.*)?$"
    return re.compile(prefix + pattern + suffix)


class GitignoreMatcher:
    """Minimal, dependency-free .gitignore evaluator.

    Supports comments, negation, anchoring, directory-only rules, and the
    common ``*``/``**``/``?`` wildcards across nested ``.gitignore`` files.
    """

    def __init__(self) -> None:
        self._rules_by_dir: dict[str, list[tuple[re.Pattern[str], bool]]] = {}

    @property
    def has_rules(self) -> bool:
        return bool(self._rules_by_dir)

    def add_file(self, directory: str, text: str) -> None:
        rules: list[tuple[re.Pattern[str], bool]] = []
        for raw in text.splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            negated = stripped.startswith("!")
            body = stripped[1:] if negated else stripped
            dir_only = body.endswith("/")
            body = body.rstrip("/")
            if body.startswith("/"):
                anchored = True
                body = body[1:]
            else:
                anchored = "/" in body
            if not body:
                continue
            rules.append((_gitignore_to_regex(body, anchored, dir_only), negated))
        if rules:
            self._rules_by_dir[directory] = rules

    def is_ignored(self, relative_path: str) -> bool:
        if not self._rules_by_dir:
            return False
        ignored = False
        for directory in sorted(
            self._rules_by_dir, key=lambda item: item.count("/") if item else -1
        ):
            if directory == "":
                subject = relative_path
            elif relative_path == directory or relative_path.startswith(
                f"{directory}/"
            ):
                subject = relative_path[len(directory) + 1 :]
            else:
                continue
            for regex, negated in self._rules_by_dir[directory]:
                if regex.match(subject):
                    ignored = not negated
        return ignored


def scan_repository(
    project_root: Path,
    cached_records: dict[str, FileRecord] | None = None,
) -> list[FileRecord]:
    resolved_root = project_root.resolve()
    records: list[FileRecord] = []
    cached_records = cached_records or {}
    gitignore = GitignoreMatcher()

    for current_root, directory_names, file_names in os.walk(resolved_root):
        current_path = Path(current_root)
        directory_relative = current_path.relative_to(resolved_root).as_posix()
        directory_relative = "" if directory_relative == "." else directory_relative

        if ".gitignore" in file_names:
            try:
                gitignore.add_file(
                    directory_relative,
                    (current_path / ".gitignore").read_text(
                        encoding="utf-8", errors="replace"
                    ),
                )
            except OSError:
                pass

        prefix = f"{directory_relative}/" if directory_relative else ""
        directory_names[:] = sorted(
            name
            for name in directory_names
            if name not in IGNORED_DIRECTORIES
            and not gitignore.is_ignored(f"{prefix}{name}")
        )

        for filename in sorted(file_names):
            absolute_path = current_path / filename
            if not should_include_file(absolute_path):
                continue
            if gitignore.is_ignored(f"{prefix}{filename}"):
                continue

            stat = absolute_path.stat()
            relative_path = absolute_path.relative_to(resolved_root).as_posix()
            last_modified = datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).isoformat()
            cached = cached_records.get(relative_path)
            if (
                cached is not None
                and cached.size_bytes == stat.st_size
                and cached.modified_ns == stat.st_mtime_ns
            ):
                records.append(cached)
                continue

            content = absolute_path.read_text(encoding="utf-8", errors="replace")
            records.append(
                FileRecord(
                    path=relative_path,
                    language=SUPPORTED_EXTENSIONS[absolute_path.suffix.lower()],
                    loc=len(content.splitlines()),
                    size_bytes=stat.st_size,
                    last_modified=last_modified,
                    modified_ns=stat.st_mtime_ns,
                )
            )

    return records
