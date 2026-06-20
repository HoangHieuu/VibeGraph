from fastapi.testclient import TestClient

from app.main import create_app


def write_source_project(root) -> None:
    source = root / "src" / "main.py"
    source.parent.mkdir(parents=True)
    source.write_text("def main(): return True\n", encoding="utf-8")


def test_health_endpoint_reports_local_runtime(tmp_path) -> None:
    write_source_project(tmp_path)
    with TestClient(
        create_app(project_root=tmp_path, watcher_enabled=False)
    ) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "vibegraph-backend",
        "mode": "local",
    }
    assert (tmp_path / ".vibegraph").is_dir()


def test_graph_api_and_rescan_use_generated_artifact(tmp_path) -> None:
    write_source_project(tmp_path)
    with TestClient(
        create_app(project_root=tmp_path, watcher_enabled=False)
    ) as client:
        project_response = client.get("/api/project")
        graph_response = client.get("/api/graph")
        file_response = client.get("/api/files/src/main.py")
        warnings_response = client.get("/api/warnings")
        rescan_response = client.post("/api/rescan")

    assert project_response.status_code == 200
    assert project_response.json()["stats"]["filesScanned"] == 1
    assert graph_response.status_code == 200
    assert graph_response.json()["nodes"][0]["path"] == "src/main.py"
    assert file_response.status_code == 200
    assert file_response.json()["exports"] == ["main"]
    assert warnings_response.json() == []
    assert rescan_response.status_code == 200
    assert (tmp_path / ".vibegraph" / "graph.json").is_file()


def test_packaged_frontend_is_served_without_hiding_api_routes(tmp_path) -> None:
    project_root = tmp_path / "project"
    frontend_root = tmp_path / "frontend"
    write_source_project(project_root)
    frontend_root.mkdir()
    (frontend_root / "index.html").write_text(
        '<main id="root">Packaged VibeGraph</main>',
        encoding="utf-8",
    )

    with TestClient(
        create_app(
            project_root=project_root,
            frontend_root=frontend_root,
            watcher_enabled=False,
        )
    ) as client:
        frontend_response = client.get("/")
        health_response = client.get("/api/health")

    assert frontend_response.status_code == 200
    assert "Packaged VibeGraph" in frontend_response.text
    assert health_response.status_code == 200


def test_packaged_frontend_requires_an_index_file(tmp_path) -> None:
    project_root = tmp_path / "project"
    frontend_root = tmp_path / "frontend"
    write_source_project(project_root)
    frontend_root.mkdir()

    try:
        create_app(project_root=project_root, frontend_root=frontend_root)
    except RuntimeError as error:
        assert "frontend index was not found" in str(error)
    else:
        raise AssertionError("Expected a missing packaged frontend to fail.")
