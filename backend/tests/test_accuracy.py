import json
from pathlib import Path

from app.application.context_service import rank_context_files
from app.application.graph_service import ProjectGraphService
from app.domain.context_models import ContextPackOptions
from app.infrastructure.output_directory import ensure_output_directory


FIXTURE = Path(__file__).parent / "fixtures" / "accuracy_project"


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def test_accuracy_fixture_meets_phase_7_thresholds(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    for source in FIXTURE.rglob("*"):
        if source.is_file():
            target = project / source.relative_to(FIXTURE)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())

    expected = json.loads((project / "expected.json").read_text())
    service = ProjectGraphService.create(
        project, ensure_output_directory(project)
    )
    document = service.scan()

    actual_edges = {
        (link.source, link.target)
        for link in document.links
        if not link.target.startswith("unresolved:")
    }
    expected_edges = {tuple(edge) for edge in expected["edges"]}
    true_edges = actual_edges & expected_edges
    edge_precision = _ratio(len(true_edges), len(actual_edges))
    edge_recall = _ratio(len(true_edges), len(expected_edges))

    actual_warnings = {
        (warning.type, warning.source, warning.target, warning.symbol)
        for warning in service.warnings
    }
    expected_warnings = {
        tuple(warning) for warning in expected["warnings"]
    }
    warning_precision = _ratio(
        len(actual_warnings & expected_warnings), len(actual_warnings)
    )

    recommendations = rank_context_files(
        document,
        expected["contextTask"],
        ContextPackOptions(max_files=8),
    )
    selected = {item.path for item in recommendations}
    required = set(expected["contextRequired"])
    context_recall = _ratio(len(selected & required), len(required))

    assert edge_precision >= 0.95
    assert edge_recall >= 0.95
    assert warning_precision >= 0.98
    assert context_recall >= 0.85

    node_ids = {node.id for node in document.nodes}
    nodes_by_id = {node.id: node for node in document.nodes}

    # A1: .gitignore-listed paths are excluded from the graph.
    assert "src/ignored/excluded.ts" not in node_ids

    # A2: CommonJS require/module.exports resolves like an import edge.
    assert ("src/legacy/loader.js", "src/legacy/config.js") in actual_edges

    # A3: monorepo workspace package imports resolve to local source.
    assert ("src/uses-ui.ts", "packages/ui/src/index.ts") in actual_edges

    # A4: strongly connected files are tagged as cycle members.
    assert nodes_by_id["src/cycle/alpha.ts"].in_cycle is True
    assert nodes_by_id["src/cycle/beta.ts"].in_cycle is True
    assert (
        nodes_by_id["src/cycle/alpha.ts"].cycle_id
        == nodes_by_id["src/cycle/beta.ts"].cycle_id
    )
    assert nodes_by_id["src/app.tsx"].in_cycle is False
