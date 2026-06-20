import json
import math
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import networkx as nx

from app.domain.graph_models import (
    GraphDocument,
    GraphLink,
    GraphNode,
    GraphStats,
    ImportRecord,
    ParsedFile,
)
from app.domain.output_paths import OutputPaths
from app.domain.warning_models import GraphWarning
from app.application.warning_service import derive_warnings
from app.infrastructure.parsers import parse_file
from app.infrastructure.scanner import scan_repository


@dataclass(slots=True)
class ProjectGraphService:
    project_root: Path
    output_paths: OutputPaths
    document: GraphDocument
    warnings: tuple[GraphWarning, ...]
    initialized: bool
    lock: threading.RLock

    @classmethod
    def create(
        cls, project_root: Path, output_paths: OutputPaths
    ) -> "ProjectGraphService":
        return cls(
            project_root.resolve(),
            output_paths,
            GraphDocument.empty(str(project_root.resolve())),
            (),
            False,
            threading.RLock(),
        )

    def scan(self) -> GraphDocument:
        with self.lock:
            previous = self.document
            records = scan_repository(self.project_root)
            parsed = [parse_file(self.project_root, record) for record in records]
            document = build_graph_document(self.project_root, parsed)
            warnings = derive_warnings(
                previous,
                document,
                self.warnings,
                initialized=self.initialized,
            )
            warning_paths = {
                warning.source for warning in warnings
            } | {
                warning.target
                for warning in warnings
                if warning.target in {node.id for node in document.nodes}
            }
            for node in document.nodes:
                node.has_warning = node.has_warning or node.id in warning_paths
            document.stats = GraphStats(
                files_scanned=document.stats.files_scanned,
                edges_found=document.stats.edges_found,
                warnings=len(warnings),
                languages=document.stats.languages,
            )
            self.document = document
            self.warnings = warnings
            self.initialized = True
            self.output_paths.graph.write_text(
                json.dumps(document.to_dict(), indent=2),
                encoding="utf-8",
            )
            self.output_paths.warnings.write_text(
                json.dumps(
                    [warning.to_dict() for warning in warnings],
                    indent=2,
                ),
                encoding="utf-8",
            )
            return document

    def file_detail(self, path: str) -> dict[str, Any] | None:
        node = next((item for item in self.document.nodes if item.id == path), None)
        if node is None:
            return None

        imports = [
            link.target for link in self.document.links if link.source == path
        ]
        imported_by = [
            link.source for link in self.document.links if link.target == path
        ]
        return {
            **next(
                item
                for item in self.document.to_dict()["nodes"]
                if item["id"] == path
            ),
            "imports": imports,
            "importedBy": imported_by,
            "warnings": [
                warning.to_dict()
                for warning in self.warnings
                if warning.source == path or warning.target == path
            ],
        }


def build_graph_document(
    project_root: Path, parsed_files: list[ParsedFile]
) -> GraphDocument:
    graph = nx.DiGraph()
    parsed_by_path = {item.file.path: item for item in parsed_files}
    nodes: dict[str, GraphNode] = {}
    links: list[GraphLink] = []

    for parsed in parsed_files:
        node = _node_from_parsed(parsed)
        nodes[node.id] = node
        graph.add_node(node.id)

    for parsed in parsed_files:
        for imported in parsed.imports:
            target = resolve_import(
                project_root, parsed.file.path, imported, parsed_by_path
            )
            if target is None:
                target = f"unresolved:{imported.module}"
                module_suffix = Path(imported.module).suffix
                is_supported_relative = imported.module.startswith(".") and (
                    not module_suffix
                    or module_suffix in {".py", ".js", ".jsx", ".ts", ".tsx"}
                )
                is_local_import = is_supported_relative or (
                    not imported.module.startswith(".")
                    and any(
                        bool(part) and (project_root / part).exists()
                        for part in imported.module.split(".")[:1]
                    )
                )
                if target not in nodes:
                    nodes[target] = GraphNode(
                        id=target,
                        path=imported.module,
                        label=imported.module,
                        type="unknown",
                        language="unknown",
                        group="external",
                        loc=0,
                        size_bytes=0,
                        last_modified="",
                        has_warning=is_local_import,
                    )
                    graph.add_node(target)
                edge_type = "broken_import" if is_local_import else "imports"
                status = "unresolved" if is_local_import else "external"
            else:
                missing_symbols = _missing_imported_symbols(
                    nodes[parsed.file.path],
                    nodes[target],
                    imported,
                )
                edge_type = (
                    "broken_import"
                    if missing_symbols
                    else "dynamic_import"
                    if imported.dynamic
                    else "test_targets"
                    if nodes[parsed.file.path].type == "test"
                    else "imports_symbol"
                    if imported.symbols
                    else "imports"
                )
                status = "missing_symbol" if missing_symbols else "healthy"

            graph.add_edge(parsed.file.path, target)
            links.append(
                GraphLink(
                    parsed.file.path,
                    target,
                    edge_type,
                    imported.symbols,
                    status,
                )
            )

    maximum_degree = max(
        1, max((degree for _, degree in graph.degree()), default=0)
    )
    for node_id, node in nodes.items():
        node.in_degree = graph.in_degree[node_id]
        node.out_degree = graph.out_degree[node_id]
        node.is_orphan = node.in_degree == 0 and node.out_degree == 0
        node.risk_score = round(
            math.log1p(node.in_degree + node.out_degree)
            / math.log1p(maximum_degree),
            3,
        )
        node.has_warning = node.has_warning or any(
            link.status in {"unresolved", "missing_symbol"}
            and (link.source == node_id or link.target == node_id)
            for link in links
        )

    languages = tuple(
        sorted({item.file.language for item in parsed_files})
    )
    warning_count = sum(
        link.status in {"unresolved", "missing_symbol"} for link in links
    )
    return GraphDocument(
        project_root=str(project_root.resolve()),
        generated_at=datetime.now().astimezone().isoformat(),
        nodes=sorted(nodes.values(), key=lambda item: item.id),
        links=links,
        stats=GraphStats(
            files_scanned=len(parsed_files),
            edges_found=len(links),
            warnings=warning_count,
            languages=languages,
        ),
    )


def resolve_import(
    project_root: Path,
    source_path: str,
    imported: ImportRecord,
    parsed_by_path: dict[str, ParsedFile],
) -> str | None:
    module = imported.module
    source = Path(source_path)
    candidates: list[Path] = []

    if source.suffix == ".py":
        if module.startswith("."):
            level = len(module) - len(module.lstrip("."))
            base = source.parent
            for _ in range(max(level - 1, 0)):
                base = base.parent
            module_path = module.lstrip(".").replace(".", "/")
            candidates.append(base / module_path)
        else:
            module_path = Path(module.replace(".", "/"))
            candidates.append(module_path)
            source_parent = source.parent
            for ancestor in [source_parent, *source_parent.parents]:
                if ancestor == Path("."):
                    continue
                candidates.append(ancestor / module_path)
        extensions = (".py",)
    elif module.startswith("."):
        candidates.append(source.parent / module)
        extensions = (".ts", ".tsx", ".js", ".jsx")
    else:
        return None

    for candidate in candidates:
        normalized = Path(*candidate.parts)
        candidate_strings = [
            normalized.with_suffix(extension).as_posix()
            for extension in extensions
        ]
        candidate_strings.extend(
            (normalized / f"index{extension}").as_posix()
            for extension in extensions
        )
        if source.suffix == ".py":
            candidate_strings.append((normalized / "__init__.py").as_posix())

        for candidate_string in candidate_strings:
            absolute_candidate = (project_root / candidate_string).resolve()
            try:
                clean = absolute_candidate.relative_to(project_root).as_posix()
            except ValueError:
                continue
            if clean in parsed_by_path:
                return clean

    return None


def _missing_imported_symbols(
    source: GraphNode,
    target: GraphNode,
    imported: ImportRecord,
) -> tuple[str, ...]:
    if not imported.symbols:
        return ()
    target_exports = set(target.exports)
    if source.language != "python" and "default" in target_exports:
        return ()
    return tuple(
        symbol for symbol in imported.symbols if symbol not in target_exports
    )


def _node_from_parsed(parsed: ParsedFile) -> GraphNode:
    path = Path(parsed.file.path)
    lower_path = parsed.file.path.lower()
    is_test = (
        "test" in path.parts
        or "__tests__" in path.parts
        or path.name.startswith("test_")
        or ".test." in path.name
        or ".spec." in path.name
    )
    is_config = (
        "config" in path.stem.lower()
        or path.name in {"vite.config.ts", "vite.config.js"}
    )
    is_entrypoint = path.name in {
        "main.py",
        "app.py",
        "index.js",
        "index.ts",
        "main.tsx",
        "main.jsx",
    }
    node_type = (
        "test"
        if is_test
        else "config"
        if is_config
        else "entrypoint"
        if is_entrypoint
        else "file"
    )
    group = (
        "test"
        if is_test
        else "config"
        if is_config
        else "frontend"
        if any(part in lower_path for part in ("frontend", "components", "pages"))
        else "agent"
        if any(part in lower_path for part in ("agent", "tools", "prompts"))
        else "backend"
        if any(part in lower_path for part in ("backend", "api", "services"))
        else path.parts[0] if len(path.parts) > 1 else "root"
    )
    return GraphNode(
        id=parsed.file.path,
        path=parsed.file.path,
        label=path.name,
        type=node_type,
        language=parsed.file.language,
        group=group,
        loc=parsed.file.loc,
        size_bytes=parsed.file.size_bytes,
        last_modified=parsed.file.last_modified,
        exports=list(parsed.exports),
        is_entrypoint=is_entrypoint,
    )
