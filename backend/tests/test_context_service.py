import asyncio
import json
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app.application.context_service import (
    ContextPackService,
    rank_context_files,
)
from app.application.graph_service import ProjectGraphService
from app.domain.context_models import (
    ContextEnhancement,
    ContextPackOptions,
    ContextRecommendation,
)
from app.domain.graph_models import GraphNode
from app.infrastructure.openrouter_client import OpenRouterClient
from app.infrastructure.output_directory import ensure_output_directory
from app.main import create_app
from tests.test_graph_service import create_mixed_project


class SuccessfulProvider:
    model = "deepseek/deepseek-v4-flash"

    async def enhance(self, **kwargs) -> ContextEnhancement:
        recommendations = kwargs["recommendations"]
        return ContextEnhancement(
            rationale="DeepSeek improved wording from structured graph data.",
            prompt="Enhanced prompt without source contents.",
            reasons={
                recommendations[0].path: "Enhanced reason for the top file."
            },
        )


class FailingProvider:
    model = "deepseek/deepseek-v4-flash"

    async def enhance(self, **kwargs) -> ContextEnhancement:
        raise RuntimeError("provider unavailable")


def build_service(
    root: Path,
    provider=None,
) -> ContextPackService:
    create_mixed_project(root)
    paths = ensure_output_directory(root)
    graph = ProjectGraphService.create(root, paths)
    graph.scan()
    return ContextPackService(
        output_paths=paths,
        graph_loader=lambda: graph.document,
        provider=provider,
    )


def test_ranking_uses_task_matches_graph_neighbors_and_tests(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    recommendations = rank_context_files(
        service.graph_loader(),
        "Fix login error handling in auth.py",
        ContextPackOptions(),
    )
    paths = [item.path for item in recommendations]

    assert paths[0] == "backend/app/api/auth.py"
    assert "backend/app/services/session.py" in paths
    assert "backend/tests/test_auth.py" in paths
    assert all(not path.startswith("unresolved:") for path in paths)


def test_direct_graph_neighbors_outrank_generic_path_matches(
    tmp_path: Path,
) -> None:
    create_mixed_project(tmp_path)
    write = lambda path, content: (
        path.parent.mkdir(parents=True, exist_ok=True),
        path.write_text(content, encoding="utf-8"),
    )
    write(
        tmp_path / "frontend" / "src" / "GraphCanvas.tsx",
        'import App from "./App";\nexport const GraphCanvas = () => App;\n',
    )
    write(
        tmp_path / "backend" / "graph_report.py",
        "def graph_report(): return True\n",
    )
    paths = ensure_output_directory(tmp_path)
    graph = ProjectGraphService.create(tmp_path, paths)
    graph.scan()

    recommendations = rank_context_files(
        graph.document,
        "Improve GraphCanvas.tsx hover behavior",
        ContextPackOptions(max_files=4),
    )
    ranked_paths = [item.path for item in recommendations]

    assert ranked_paths.index("frontend/src/App.tsx") < ranked_paths.index(
        "backend/graph_report.py"
    )


def test_ranking_does_not_pad_with_unrelated_recent_files(
    tmp_path: Path,
) -> None:
    service = build_service(tmp_path)
    (tmp_path / "unrelated_test.py").write_text(
        "def test_unrelated(): assert True\n",
        encoding="utf-8",
    )
    graph = ProjectGraphService.create(
        tmp_path, ensure_output_directory(tmp_path)
    )
    graph.scan()

    recommendations = rank_context_files(
        graph.document,
        "Fix login error handling in auth.py",
        ContextPackOptions(max_files=8),
    )

    assert "unrelated_test.py" not in {
        item.path for item in recommendations
    }
    assert all(
        any(
            evidence in item.reason
            for evidence in (
                "task",
                "path matches",
                "exports match",
                "dependency",
                "importer",
                "graph depth",
                "test connected",
            )
        )
        for item in recommendations
    )


def test_offline_context_pack_writes_markdown(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    pack = asyncio.run(
        service.generate(
            "Fix login error handling in auth.py",
            ContextPackOptions(max_files=4),
        )
    )

    assert pack.mode == "offline"
    assert pack.model is None
    assert 1 <= len(pack.recommendations) <= 4
    assert pack.reduction_percent >= 0
    artifact = tmp_path / ".vibegraph" / "context.md"
    assert artifact.is_file()
    markdown = artifact.read_text(encoding="utf-8")
    assert "Fix login error handling" in markdown
    assert "backend/app/api/auth.py" in markdown
    assert "OPENROUTER_API_KEY" not in markdown


def test_provider_enhances_wording_without_changing_files(
    tmp_path: Path,
) -> None:
    offline = build_service(tmp_path / "offline")
    enhanced = build_service(tmp_path / "enhanced", SuccessfulProvider())
    options = ContextPackOptions(max_files=4)

    offline_pack = asyncio.run(offline.generate("Fix auth login", options))
    enhanced_pack = asyncio.run(enhanced.generate("Fix auth login", options))

    assert enhanced_pack.mode == "enhanced"
    assert enhanced_pack.model == "deepseek/deepseek-v4-flash"
    assert enhanced_pack.prompt == "Enhanced prompt without source contents."
    assert [item.path for item in enhanced_pack.recommendations] == [
        item.path for item in offline_pack.recommendations
    ]


def test_provider_failure_falls_back_to_deterministic_pack(
    tmp_path: Path,
) -> None:
    service = build_service(tmp_path, FailingProvider())

    pack = asyncio.run(service.generate("Fix auth login", ContextPackOptions()))

    assert pack.mode == "fallback"
    assert "failed" in pack.provider_message.lower()
    assert pack.recommendations


def test_context_pack_api_works_without_key(tmp_path: Path) -> None:
    create_mixed_project(tmp_path)
    with TestClient(
        create_app(
            project_root=tmp_path,
            environment={},
            watcher_enabled=False,
        )
    ) as client:
        response = client.post(
            "/api/context-pack",
            json={"task": "Fix login error handling in auth.py"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "offline"
    assert payload["recommendations"][0]["path"] == "backend/app/api/auth.py"
    assert payload["artifactPath"] == ".vibegraph/context.md"


def test_openrouter_payload_contains_metadata_not_source_content() -> None:
    captured: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["authorization"] = request.headers["Authorization"]
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "rationale": "Structured metadata only.",
                                    "prompt": "Use the ranked files.",
                                    "reasons": [],
                                }
                            )
                        }
                    }
                ]
            },
        )

    client = OpenRouterClient(
        api_key="secret-test-key",
        transport=httpx.MockTransport(handler),
    )
    recommendation = (
        ContextRecommendation(
            path="src/auth.py",
            reason="explicit match",
            score=100,
        ),
    )
    node = GraphNode(
        id="src/auth.py",
        path="src/auth.py",
        label="auth.py",
        type="file",
        language="python",
        group="backend",
        loc=20,
        size_bytes=400,
        last_modified="",
        exports=["login"],
    )

    asyncio.run(
        client.enhance(
            task="Fix login",
            recommendations=recommendation,
            nodes={"src/auth.py": node},
            links=[],
            prompt="Deterministic prompt",
        )
    )

    body_text = json.dumps(captured["body"])
    assert captured["authorization"] == "Bearer secret-test-key"
    assert "src/auth.py" in body_text
    assert "def login" not in body_text
    assert "/tmp/project" not in body_text
    assert "prompt under 2,500 characters" in body_text
