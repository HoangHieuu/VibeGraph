import json
from pathlib import Path

from app.application.graph_service import ProjectGraphService
from app.infrastructure.output_directory import ensure_output_directory


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_mixed_project(root: Path) -> None:
    write(
        root / "backend" / "app" / "api" / "auth.py",
        "from backend.app.services.session import validate_session\n"
        "def login(): return validate_session()\n",
    )
    write(
        root / "backend" / "app" / "services" / "session.py",
        "def validate_session(): return True\n",
    )
    write(
        root / "backend" / "tests" / "test_auth.py",
        "from backend.app.api.auth import login\n"
        "def test_login(): assert login()\n",
    )
    write(
        root / "frontend" / "src" / "App.tsx",
        'import { api } from "./lib/api";\n'
        'import "./styles.css";\n'
        "export default function App() { return api(); }\n",
    )
    write(root / "frontend" / "src" / "styles.css", "body { color: white; }\n")
    write(
        root / "frontend" / "src" / "lib" / "api.ts",
        'import { missing } from "./missing";\n'
        "export const api = () => missing;\n",
    )
    write(
        root / "frontend" / "src" / "features" / "panel.ts",
        'import type { Graph } from "../types/graph";\n'
        "export const panel = (graph: Graph) => graph;\n",
    )
    write(
        root / "frontend" / "src" / "types" / "graph.ts",
        "export interface Graph { nodes: string[] }\n",
    )


def test_graph_service_builds_and_writes_directed_graph(tmp_path: Path) -> None:
    create_mixed_project(tmp_path)
    paths = ensure_output_directory(tmp_path)
    service = ProjectGraphService.create(tmp_path, paths)

    document = service.scan()

    assert document.stats.files_scanned == 7
    assert set(document.stats.languages) == {"python", "typescript"}
    assert paths.graph.is_file()
    payload = json.loads(paths.graph.read_text(encoding="utf-8"))
    assert len(payload["nodes"]) >= 5
    assert payload["stats"]["filesScanned"] == 7
    assert {
        "id",
        "path",
        "label",
        "language",
        "type",
        "loc",
        "inDegree",
        "outDegree",
    }.issubset(payload["nodes"][0])
    assert {"source", "target", "type", "status"}.issubset(payload["links"][0])

    auth_link = next(
        link
        for link in document.links
        if link.source == "backend/app/api/auth.py"
    )
    assert auth_link.target == "backend/app/services/session.py"
    assert auth_link.status == "healthy"

    unresolved = next(
        link
        for link in document.links
        if link.source == "frontend/src/lib/api.ts"
    )
    assert unresolved.type == "broken_import"
    assert unresolved.status == "unresolved"

    parent_import = next(
        link
        for link in document.links
        if link.source == "frontend/src/features/panel.ts"
    )
    assert parent_import.target == "frontend/src/types/graph.ts"
    assert parent_import.status == "healthy"

    stylesheet = next(
        link
        for link in document.links
        if link.source == "frontend/src/App.tsx"
        and link.target == "unresolved:./styles.css"
    )
    assert stylesheet.status == "external"
    assert document.stats.warnings == 1


def test_file_detail_contains_dependencies_and_exports(tmp_path: Path) -> None:
    create_mixed_project(tmp_path)
    service = ProjectGraphService.create(
        tmp_path, ensure_output_directory(tmp_path)
    )
    service.scan()

    detail = service.file_detail("backend/app/api/auth.py")

    assert detail is not None
    assert detail["exports"] == ["validate_session", "login"]
    assert detail["imports"] == ["backend/app/services/session.py"]
    assert detail["importedBy"] == ["backend/tests/test_auth.py"]
