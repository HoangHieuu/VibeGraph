import json
import threading
import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.application.graph_service import ProjectGraphService
from app.infrastructure.output_directory import ensure_output_directory
from app.infrastructure.project_watcher import (
    ProjectWatcher,
    is_supported_event_path,
)
from app.main import create_app
from tests.test_graph_service import write


def create_dependency_project(root: Path) -> None:
    write(
        root / "app" / "api.py",
        "from app.service import validate_session\n"
        "def login(): return validate_session()\n",
    )
    write(
        root / "app" / "service.py",
        "def validate_session(): return True\n",
    )


def test_missing_symbol_and_deleted_file_warnings_are_persisted(
    tmp_path: Path,
) -> None:
    create_dependency_project(tmp_path)
    paths = ensure_output_directory(tmp_path)
    service = ProjectGraphService.create(tmp_path, paths)
    service.scan()

    write(tmp_path / "app" / "service.py", "def replacement(): return True\n")
    missing_document = service.scan()

    assert [warning.type for warning in service.warnings] == [
        "MISSING_EXPORTED_SYMBOL"
    ]
    assert missing_document.stats.warnings == 1
    assert next(
        link
        for link in missing_document.links
        if link.source == "app/api.py"
    ).status == "missing_symbol"
    assert json.loads(paths.warnings.read_text(encoding="utf-8"))[0][
        "symbol"
    ] == "validate_session"

    (tmp_path / "app" / "service.py").unlink()
    service.scan()

    warning_types = {warning.type for warning in service.warnings}
    assert "DELETED_IMPORTED_FILE" in warning_types
    assert "BROKEN_IMPORT" in warning_types

    service.scan()
    assert "DELETED_IMPORTED_FILE" in {
        warning.type for warning in service.warnings
    }


def test_new_orphan_and_cycle_warnings_follow_graph_transitions(
    tmp_path: Path,
) -> None:
    write(tmp_path / "src" / "a.py", "from src.b import b\ndef a(): return b()\n")
    write(tmp_path / "src" / "b.py", "def b(): return True\n")
    service = ProjectGraphService.create(
        tmp_path, ensure_output_directory(tmp_path)
    )
    service.scan()
    assert not service.warnings

    write(tmp_path / "src" / "a.py", "def a(): return True\n")
    service.scan()
    orphan_sources = {
        warning.source
        for warning in service.warnings
        if warning.type == "NEW_ORPHAN_FILE"
    }
    assert {"src/a.py", "src/b.py"}.issubset(orphan_sources)

    write(tmp_path / "src" / "a.py", "from src.b import b\ndef a(): return b()\n")
    service.scan()
    write(tmp_path / "src" / "b.py", "from src.a import a\ndef b(): return a()\n")
    service.scan()

    cycles = [
        warning
        for warning in service.warnings
        if warning.type == "NEW_CIRCULAR_DEPENDENCY"
    ]
    assert len(cycles) == 1
    assert "src/a.py" in cycles[0].message
    assert "src/b.py" in cycles[0].message


def test_project_watcher_filters_and_debounces_supported_changes(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, ...]] = []
    received = threading.Event()

    def callback(paths: tuple[str, ...]) -> None:
        events.append(paths)
        received.set()

    watcher = ProjectWatcher(tmp_path, callback, debounce_seconds=0.05)
    watcher.start()
    try:
        source = tmp_path / "src" / "main.py"
        source.parent.mkdir(parents=True)
        source.write_text("def main(): return 1\n", encoding="utf-8")
        source.write_text("def main(): return 2\n", encoding="utf-8")

        assert received.wait(timeout=2)
        time.sleep(0.1)
    finally:
        watcher.stop()

    assert events
    assert events[-1] == ("src/main.py",)
    assert is_supported_event_path(source)
    assert not is_supported_event_path(tmp_path / ".vibegraph" / "graph.json")
    assert not is_supported_event_path(tmp_path / "README.md")


def test_websocket_receives_graph_and_warning_updates(tmp_path: Path) -> None:
    create_dependency_project(tmp_path)
    application = create_app(
        project_root=tmp_path,
        environment={},
        watcher_enabled=False,
    )
    with TestClient(application) as client:
        with client.websocket_connect("/ws/events") as websocket:
            write(
                tmp_path / "app" / "service.py",
                "def replacement(): return True\n",
            )
            response_holder: list[int] = []

            def trigger_rescan() -> None:
                response_holder.append(client.post("/api/rescan").status_code)

            trigger = threading.Thread(target=trigger_rescan)
            trigger.start()
            graph_event = websocket.receive_json()
            warning_event = websocket.receive_json()
            trigger.join(timeout=2)

    assert response_holder == [200]
    assert graph_event["type"] == "graph_updated"
    assert graph_event["changedPaths"] == ["manual-rescan"]
    assert graph_event["warnings"][0]["type"] == "MISSING_EXPORTED_SYMBOL"
    assert warning_event["type"] == "warning_created"
    assert warning_event["warning"]["symbol"] == "validate_session"
