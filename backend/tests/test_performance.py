from pathlib import Path
from time import perf_counter

from app.application.context_service import rank_context_files
from app.application.graph_service import ProjectGraphService
from app.domain.context_models import ContextPackOptions
from app.infrastructure.output_directory import ensure_output_directory


def _create_repository(root: Path, count: int) -> None:
    for index in range(count):
        dependency = (
            f"from module_{index + 1:04d} import value\n"
            if index + 1 < count
            else ""
        )
        (root / f"module_{index:04d}.py").write_text(
            f"{dependency}value = {index}\n",
            encoding="utf-8",
        )


def test_phase_7_large_repository_targets(tmp_path: Path) -> None:
    _create_repository(tmp_path, 1000)
    service = ProjectGraphService.create(
        tmp_path, ensure_output_directory(tmp_path)
    )

    cold_started = perf_counter()
    document = service.scan()
    cold_seconds = perf_counter() - cold_started

    changed = tmp_path / "module_0500.py"
    changed.write_text(
        "from module_0501 import value\nvalue = 50000\n",
        encoding="utf-8",
    )
    refresh_started = perf_counter()
    document = service.scan()
    refresh_seconds = perf_counter() - refresh_started

    context_started = perf_counter()
    recommendations = rank_context_files(
        document,
        "Fix module_0500 value flow",
        ContextPackOptions(max_files=8),
    )
    context_seconds = perf_counter() - context_started

    assert document.stats.files_scanned == 1000
    assert cold_seconds <= 10
    assert refresh_seconds <= 1.5
    assert context_seconds <= 2
    assert service.parsed_files_count == 1
    assert service.reused_files_count == 999
    assert recommendations[0].path == "module_0500.py"
