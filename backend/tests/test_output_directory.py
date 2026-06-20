from pathlib import Path

import pytest

from app.domain.output_paths import (
    SCANNER_IGNORED_DIRECTORIES,
    OutputPaths,
)
from app.infrastructure.output_directory import (
    OutputDirectoryError,
    ensure_output_directory,
)
from app.main import resolve_project_root


def test_output_paths_reserve_all_required_artifacts(tmp_path: Path) -> None:
    paths = OutputPaths.for_project(tmp_path)

    assert paths.directory == tmp_path / ".vibegraph"
    assert paths.graph == tmp_path / ".vibegraph" / "graph.json"
    assert paths.context == tmp_path / ".vibegraph" / "context.md"
    assert paths.readme == tmp_path / ".vibegraph" / "README.generated.md"
    assert paths.warnings == tmp_path / ".vibegraph" / "warnings.json"
    assert SCANNER_IGNORED_DIRECTORIES == frozenset({".vibegraph"})


def test_output_directory_creation_is_idempotent(tmp_path: Path) -> None:
    first = ensure_output_directory(tmp_path)
    second = ensure_output_directory(tmp_path)

    assert first == second
    assert first.directory.is_dir()
    assert list(first.directory.iterdir()) == []


def test_output_directory_reports_a_path_conflict(tmp_path: Path) -> None:
    output_path = tmp_path / ".vibegraph"
    output_path.write_text("not a directory", encoding="utf-8")

    with pytest.raises(
        OutputDirectoryError,
        match="Unable to prepare VibeGraph output directory",
    ):
        ensure_output_directory(tmp_path)


def test_project_root_can_be_selected_from_environment(tmp_path: Path) -> None:
    selected = resolve_project_root(
        environment={"VIBEGRAPH_PROJECT_ROOT": str(tmp_path)},
        current_directory=Path("/unused"),
    )

    assert selected == tmp_path


def test_project_root_defaults_to_current_directory(tmp_path: Path) -> None:
    assert (
        resolve_project_root(environment={}, current_directory=tmp_path)
        == tmp_path
    )
