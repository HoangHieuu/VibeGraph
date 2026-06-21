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
    parsed_cache: dict[str, ParsedFile]
    parsed_files_count: int
    reused_files_count: int

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
            {},
            0,
            0,
        )

    def scan(self, *, force: bool = False) -> GraphDocument:
        with self.lock:
            previous = self.document
            cached_records = (
                {}
                if force
                else {
                    path: parsed.file
                    for path, parsed in self.parsed_cache.items()
                }
            )
            records = scan_repository(self.project_root, cached_records)
            parsed: list[ParsedFile] = []
            parsed_count = 0
            reused_count = 0
            for record in records:
                cached = None if force else self.parsed_cache.get(record.path)
                if cached is not None and cached.file == record:
                    parsed.append(cached)
                    reused_count += 1
                else:
                    parsed.append(parse_file(self.project_root, record))
                    parsed_count += 1
            self.parsed_cache = {item.file.path: item for item in parsed}
            self.parsed_files_count = parsed_count
            self.reused_files_count = reused_count
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
    resolution = load_resolution_config(project_root)

    for parsed in parsed_files:
        node = _node_from_parsed(parsed)
        nodes[node.id] = node
        graph.add_node(node.id)

    for parsed in parsed_files:
        for imported in parsed.imports:
            target = resolve_import(
                project_root,
                parsed.file.path,
                imported,
                parsed_by_path,
                resolution,
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
                    and (
                        resolution.matches(imported.module)
                        or any(
                            bool(part) and (project_root / part).exists()
                            for part in imported.module.split(".")[:1]
                        )
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

    _tag_cycle_membership(nodes, links)

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


def _tag_cycle_membership(
    nodes: dict[str, GraphNode], links: list[GraphLink]
) -> None:
    cycle_graph = nx.DiGraph()
    cycle_graph.add_nodes_from(
        node_id for node_id, node in nodes.items() if node.type != "unknown"
    )
    cycle_graph.add_edges_from(
        (link.source, link.target)
        for link in links
        if link.status == "healthy"
        and link.source in nodes
        and link.target in nodes
        and nodes[link.source].type != "unknown"
        and nodes[link.target].type != "unknown"
    )
    components = sorted(
        (
            tuple(sorted(component))
            for component in nx.strongly_connected_components(cycle_graph)
            if len(component) > 1
        ),
        key=lambda item: item,
    )
    for index, component in enumerate(components):
        for node_id in component:
            node = nodes.get(node_id)
            if node is None:
                continue
            node.in_cycle = True
            node.cycle_id = index


def resolve_import(
    project_root: Path,
    source_path: str,
    imported: ImportRecord,
    parsed_by_path: dict[str, ParsedFile],
    resolution: "ResolutionConfig | None" = None,
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
            candidates.append(Path("src") / module_path)
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
        extensions = (".ts", ".tsx", ".js", ".jsx")
        if resolution is not None:
            candidates.extend(resolution.candidates(module))
        candidates.append(Path(module))

    for candidate in candidates:
        normalized = Path(*candidate.parts)
        candidate_strings: list[str] = []
        if normalized.suffix in extensions:
            candidate_strings.append(normalized.as_posix())
            if normalized.suffix in {".js", ".jsx"}:
                without_suffix = normalized.with_suffix("")
                candidate_strings.extend(
                    without_suffix.with_suffix(extension).as_posix()
                    for extension in extensions
                )
        else:
            candidate_strings.extend(
                f"{normalized.as_posix()}{extension}"
                for extension in extensions
            )
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
    return tuple(
        symbol for symbol in imported.symbols if symbol not in target_exports
    )


@dataclass(frozen=True, slots=True)
class WorkspacePackage:
    name: str
    directory: str
    entries: tuple[str, ...]

    def matches(self, module: str) -> bool:
        return module == self.name or module.startswith(f"{self.name}/")

    def candidates(self, module: str) -> list[Path]:
        if module == self.name:
            result = [Path(entry) for entry in self.entries]
            result.append(Path(self.directory))
            result.append(Path(self.directory) / "src")
            return result
        prefix = f"{self.name}/"
        if module.startswith(prefix):
            return [Path(self.directory) / module[len(prefix) :]]
        return []


@dataclass(frozen=True, slots=True)
class ResolutionConfig:
    base_url: Path
    paths: tuple[tuple[str, tuple[str, ...]], ...]
    workspaces: tuple[WorkspacePackage, ...] = ()

    def matches(self, module: str) -> bool:
        # Workspace packages are intentionally excluded here: when their source
        # entry cannot be resolved we keep them as external rather than emitting
        # a false broken-import warning.
        return any(_path_pattern_matches(pattern, module) for pattern, _ in self.paths)

    def candidates(self, module: str) -> list[Path]:
        candidates: list[Path] = []
        for pattern, replacements in self.paths:
            if "*" in pattern:
                prefix, suffix = pattern.split("*", 1)
                if not module.startswith(prefix) or not module.endswith(suffix):
                    continue
                wildcard = module[len(prefix) : len(module) - len(suffix) or None]
            elif module == pattern:
                wildcard = ""
            else:
                continue
            for replacement in replacements:
                candidates.append(
                    self.base_url / replacement.replace("*", wildcard)
                )
        for package in self.workspaces:
            candidates.extend(package.candidates(module))
        if self.base_url != Path("."):
            candidates.append(self.base_url / module)
        return candidates


def _path_pattern_matches(pattern: str, module: str) -> bool:
    if "*" not in pattern:
        return module == pattern
    prefix, suffix = pattern.split("*", 1)
    return module.startswith(prefix) and module.endswith(suffix)


def load_resolution_config(project_root: Path) -> ResolutionConfig:
    base_url = Path(".")
    paths: tuple[tuple[str, tuple[str, ...]], ...] = ()
    for filename in ("tsconfig.json", "jsconfig.json"):
        path = project_root / filename
        if not path.is_file():
            continue
        try:
            raw = path.read_text(encoding="utf-8")
            raw = _strip_json_comments(raw)
            raw = _strip_trailing_commas(raw)
            compiler_options = json.loads(raw).get("compilerOptions", {})
            base_url = Path(compiler_options.get("baseUrl", "."))
            paths = tuple(
                (pattern, tuple(replacements))
                for pattern, replacements in compiler_options.get(
                    "paths", {}
                ).items()
                if isinstance(pattern, str)
                and isinstance(replacements, list)
                and all(isinstance(item, str) for item in replacements)
            )
        except (OSError, ValueError, TypeError):
            base_url, paths = Path("."), ()
        break
    return ResolutionConfig(base_url, paths, _load_workspaces(project_root))


def _load_workspaces(project_root: Path) -> tuple[WorkspacePackage, ...]:
    manifest = project_root / "package.json"
    if not manifest.is_file():
        return ()
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ()
    workspaces = data.get("workspaces")
    patterns: list[str] = []
    if isinstance(workspaces, list):
        patterns = [item for item in workspaces if isinstance(item, str)]
    elif isinstance(workspaces, dict):
        declared = workspaces.get("packages")
        if isinstance(declared, list):
            patterns = [item for item in declared if isinstance(item, str)]
    packages: list[WorkspacePackage] = []
    for pattern in patterns:
        for directory in sorted(project_root.glob(pattern)):
            if not directory.is_dir():
                continue
            package = _read_workspace_package(project_root, directory)
            if package is not None:
                packages.append(package)
    return tuple(packages)


def _read_workspace_package(
    project_root: Path, directory: Path
) -> WorkspacePackage | None:
    manifest = directory / "package.json"
    if not manifest.is_file():
        return None
    try:
        meta = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    name = meta.get("name")
    if not isinstance(name, str) or not name:
        return None
    relative_directory = directory.relative_to(project_root).as_posix()
    return WorkspacePackage(
        name=name,
        directory=relative_directory,
        entries=_entry_strings(meta, relative_directory),
    )


def _entry_strings(meta: dict[str, Any], directory: str) -> tuple[str, ...]:
    values: list[str] = []
    for key in ("main", "module"):
        value = meta.get(key)
        if isinstance(value, str):
            values.append(value)
    values.extend(_exports_strings(meta.get("exports")))
    entries: list[str] = []
    for value in values:
        cleaned = value.lstrip("./")
        if cleaned:
            entries.append(f"{directory}/{cleaned}")
    return tuple(dict.fromkeys(entries))


def _exports_strings(exports: Any) -> list[str]:
    if isinstance(exports, str):
        return [exports]
    if isinstance(exports, dict):
        dot = exports.get(".")
        if isinstance(dot, str):
            return [dot]
        if isinstance(dot, dict):
            return [value for value in dot.values() if isinstance(value, str)]
    return []


def _strip_json_comments(value: str) -> str:
    result: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(value):
        character = value[index]
        next_character = value[index + 1] if index + 1 < len(value) else ""
        if in_string:
            result.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if character == '"':
            in_string = True
            result.append(character)
            index += 1
            continue
        if character == "/" and next_character == "/":
            index += 2
            while index < len(value) and value[index] not in "\r\n":
                index += 1
            continue
        if character == "/" and next_character == "*":
            index += 2
            while index + 1 < len(value) and value[index : index + 2] != "*/":
                index += 1
            index += 2
            continue
        result.append(character)
        index += 1
    return "".join(result)


def _strip_trailing_commas(value: str) -> str:
    result: list[str] = []
    in_string = False
    escaped = False
    index = 0
    while index < len(value):
        character = value[index]
        if in_string:
            result.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if character == '"':
            in_string = True
            result.append(character)
            index += 1
            continue
        if character == ",":
            cursor = index + 1
            while cursor < len(value) and value[cursor].isspace():
                cursor += 1
            if cursor < len(value) and value[cursor] in "}]":
                index += 1
                continue
        result.append(character)
        index += 1
    return "".join(result)


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
