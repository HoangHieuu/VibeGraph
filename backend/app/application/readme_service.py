import json
import re
import tomllib
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol

from app.domain.graph_models import GraphDocument, GraphLink, GraphNode
from app.domain.output_paths import OutputPaths
from app.domain.readme_models import (
    ReadmeDocument,
    ReadmeEnhancement,
    ReadmeModule,
)


MAX_MODULES = 6
MAX_KEY_FILES = 10
MAX_MODULE_FILES = 5
MAX_MERMAID_EDGES = 14
MERMAID_LABEL_PATTERN = re.compile(r'["\n\r]')


class ReadmeProvider(Protocol):
    model: str

    async def enhance_readme(
        self,
        *,
        project_name: str,
        description: str,
        document: GraphDocument,
        modules: tuple[ReadmeModule, ...],
        entrypoints: tuple[str, ...],
        key_files: tuple[str, ...],
        commands: tuple[str, ...],
        warnings: tuple[str, ...],
    ) -> ReadmeEnhancement: ...


@dataclass(slots=True)
class ReadmeService:
    output_paths: OutputPaths
    graph_loader: Callable[[], GraphDocument]
    provider: ReadmeProvider | None = None

    async def generate(self, description: str = "") -> ReadmeDocument:
        clean_description = description.strip()
        graph = self.graph_loader()
        project_name = self.output_paths.project_root.name
        entrypoints = select_entrypoints(graph)
        modules = select_modules(graph)
        key_files = select_key_files(graph, entrypoints)
        commands = detect_commands(self.output_paths.project_root, entrypoints)
        warnings = collect_warnings(graph)
        mermaid = build_mermaid(graph, key_files)
        overview = build_overview(project_name, graph, clean_description)
        architecture = build_architecture(graph, modules, entrypoints)
        mode = "offline"
        model: str | None = None
        provider_message = (
            "AI-enhanced prose is disabled; using deterministic graph analysis."
        )

        if self.provider is not None:
            model = self.provider.model
            try:
                enhancement = await self.provider.enhance_readme(
                    project_name=project_name,
                    description=clean_description,
                    document=graph,
                    modules=modules,
                    entrypoints=entrypoints,
                    key_files=key_files,
                    commands=commands,
                    warnings=warnings,
                )
                overview = enhancement.overview
                architecture = enhancement.architecture
                modules = tuple(
                    replace(
                        module,
                        summary=enhancement.module_summaries.get(
                            module.name, module.summary
                        ),
                    )
                    for module in modules
                )
                mode = "enhanced"
                provider_message = enhancement.rationale
            except Exception:
                mode = "fallback"
                provider_message = (
                    "OpenRouter enhancement failed; deterministic README "
                    "structure and prose were preserved."
                )

        artifact_path = self.output_paths.readme.relative_to(
            self.output_paths.project_root
        ).as_posix()
        markdown = render_readme(
            project_name=project_name,
            overview=overview,
            architecture=architecture,
            modules=modules,
            entrypoints=entrypoints,
            key_files=key_files,
            commands=commands,
            warnings=warnings,
            mermaid=mermaid,
            mode=mode,
            model=model,
        )
        result = ReadmeDocument(
            mode=mode,  # type: ignore[arg-type]
            model=model,
            project_name=project_name,
            overview=overview,
            architecture=architecture,
            modules=modules,
            entrypoints=entrypoints,
            key_files=key_files,
            commands=commands,
            warnings=warnings,
            mermaid=mermaid,
            markdown=markdown,
            provider_message=provider_message,
            artifact_path=artifact_path,
        )
        self.output_paths.readme.write_text(markdown, encoding="utf-8")
        return result


def select_entrypoints(document: GraphDocument) -> tuple[str, ...]:
    return tuple(
        node.path
        for node in sorted(
            _internal_nodes(document),
            key=lambda node: (
                not node.is_entrypoint,
                -(node.in_degree + node.out_degree),
                node.path,
            ),
        )
        if node.is_entrypoint
    )[:8]


def select_modules(document: GraphDocument) -> tuple[ReadmeModule, ...]:
    grouped: dict[str, list[GraphNode]] = defaultdict(list)
    for node in _internal_nodes(document):
        if node.type not in {"test", "config"}:
            grouped[node.group].append(node)

    ranked_groups = sorted(
        grouped.items(),
        key=lambda item: (
            -sum(node.in_degree + node.out_degree + 1 for node in item[1]),
            item[0],
        ),
    )[:MAX_MODULES]
    modules: list[ReadmeModule] = []
    for name, nodes in ranked_groups:
        ranked_nodes = sorted(
            nodes,
            key=lambda node: (
                not node.is_entrypoint,
                -(node.in_degree + node.out_degree),
                node.path,
            ),
        )
        files = tuple(node.path for node in ranked_nodes[:MAX_MODULE_FILES])
        entrypoints = tuple(node.path for node in ranked_nodes if node.is_entrypoint)
        languages = ", ".join(sorted({node.language for node in nodes}))
        modules.append(
            ReadmeModule(
                name=name,
                summary=(
                    f"Contains {len(nodes)} {languages} source "
                    f"{'file' if len(nodes) == 1 else 'files'} centered on "
                    f"{files[0]}."
                ),
                files=files,
                entrypoints=entrypoints,
            )
        )
    return tuple(modules)


def select_key_files(
    document: GraphDocument,
    entrypoints: tuple[str, ...],
) -> tuple[str, ...]:
    entrypoint_set = set(entrypoints)
    ranked = sorted(
        _internal_nodes(document),
        key=lambda node: (
            node.path not in entrypoint_set,
            -node.risk_score,
            -(node.in_degree + node.out_degree),
            node.path,
        ),
    )
    return tuple(node.path for node in ranked[:MAX_KEY_FILES])


def detect_commands(
    project_root: Path,
    entrypoints: tuple[str, ...],
) -> tuple[str, ...]:
    commands: list[str] = []
    package_path = project_root / "package.json"
    if package_path.is_file():
        try:
            package = json.loads(package_path.read_text(encoding="utf-8"))
            scripts = package.get("scripts", {})
            manager = str(package.get("packageManager", "npm")).split("@", 1)[0]
            prefix = manager if manager in {"pnpm", "yarn", "bun"} else "npm run"
            for name in ("dev", "start", "test", "check", "build"):
                if isinstance(scripts, dict) and isinstance(scripts.get(name), str):
                    commands.append(f"{prefix} {name}")
        except (json.JSONDecodeError, OSError):
            pass

    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.is_file():
        try:
            pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
            scripts = pyproject.get("project", {}).get("scripts", {})
            if isinstance(scripts, dict):
                commands.extend(f"uv run {name}" for name in sorted(scripts)[:3])
        except (tomllib.TOMLDecodeError, OSError, AttributeError):
            pass

    if not commands:
        for entrypoint in entrypoints[:3]:
            if entrypoint.endswith(".py"):
                commands.append(f"python {entrypoint}")
            elif entrypoint.endswith((".js", ".jsx")):
                commands.append(f"node {entrypoint}")
    return tuple(dict.fromkeys(commands))


def collect_warnings(document: GraphDocument) -> tuple[str, ...]:
    warnings: list[str] = []
    exports_by_path = {node.path: set(node.exports) for node in document.nodes}
    for link in document.links:
        if link.status == "unresolved":
            warnings.append(
                f"{link.source} could not resolve "
                f"{link.target.removeprefix('unresolved:')}."
            )
        elif link.status == "missing_symbol":
            target_exports = exports_by_path.get(link.target, set())
            for symbol in link.symbols:
                if symbol not in target_exports:
                    warnings.append(
                        f"{link.source} imports {symbol} from {link.target}, "
                        f"but {symbol} is not exported."
                    )
    return tuple(warnings)


def build_mermaid(
    document: GraphDocument,
    key_files: tuple[str, ...],
) -> str:
    selected = set(key_files)
    node_ids = {path: f"N{index}" for index, path in enumerate(key_files)}
    lines = ["flowchart TD"]
    for path in key_files:
        label = MERMAID_LABEL_PATTERN.sub(" ", path)
        lines.append(f'  {node_ids[path]}["{label}"]')

    edge_count = 0
    for link in sorted(
        document.links,
        key=lambda item: (item.source, item.target, item.type),
    ):
        if (
            link.status == "healthy"
            and link.source in selected
            and link.target in selected
            and edge_count < MAX_MERMAID_EDGES
        ):
            lines.append(f"  {node_ids[link.source]} --> {node_ids[link.target]}")
            edge_count += 1
    return "\n".join(lines)


def build_overview(
    project_name: str,
    document: GraphDocument,
    description: str,
) -> str:
    if description:
        return description
    languages = ", ".join(document.stats.languages) or "supported"
    return (
        f"{project_name} contains {document.stats.files_scanned} analyzed source "
        f"files across {languages}, connected by {document.stats.edges_found} "
        "detected dependency relationships."
    )


def build_architecture(
    document: GraphDocument,
    modules: tuple[ReadmeModule, ...],
    entrypoints: tuple[str, ...],
) -> str:
    module_names = ", ".join(module.name for module in modules) or "no modules"
    entrypoint_text = (
        ", ".join(entrypoints)
        if entrypoints
        else "No conventional entry point was detected"
    )
    return (
        f"The dependency graph is organized into {module_names}. "
        f"Detected entry points: {entrypoint_text}. "
        f"The current graph reports {document.stats.warnings} unresolved local "
        f"{'dependency' if document.stats.warnings == 1 else 'dependencies'}."
    )


def render_readme(
    *,
    project_name: str,
    overview: str,
    architecture: str,
    modules: tuple[ReadmeModule, ...],
    entrypoints: tuple[str, ...],
    key_files: tuple[str, ...],
    commands: tuple[str, ...],
    warnings: tuple[str, ...],
    mermaid: str,
    mode: str,
    model: str | None,
) -> str:
    module_text = "\n\n".join(
        (
            f"### {module.name}\n\n{module.summary}\n\n"
            + "\n".join(f"- `{path}`" for path in module.files)
        )
        for module in modules
    ) or "No source modules were detected."
    entrypoint_text = (
        "\n".join(f"- `{path}`" for path in entrypoints)
        or "- No conventional entry points detected."
    )
    command_text = (
        "\n\n".join(f"```bash\n{command}\n```" for command in commands)
        or "No standard run commands were detected."
    )
    key_file_text = (
        "\n".join(f"- `{path}`" for path in key_files)
        or "- No source files detected."
    )
    warning_text = (
        "\n".join(f"- {warning}" for warning in warnings)
        or "No unresolved local dependencies were detected."
    )
    attribution = (
        f"Generated by VibeGraph in {mode} mode"
        + (
            f" using `{model}` for prose enhancement"
            if mode == "enhanced" and model
            else ""
        )
        + ". Graph structure, commands, key files, and Mermaid output were "
        "derived deterministically from local project metadata."
    )
    return (
        f"# {project_name}\n\n"
        f"## Overview\n\n{overview}\n\n"
        f"## Architecture\n\n{architecture}\n\n"
        f"### Entry Points\n\n{entrypoint_text}\n\n"
        f"## Main Modules\n\n{module_text}\n\n"
        f"## Mermaid Diagram\n\n```mermaid\n{mermaid}\n```\n\n"
        f"## How to Run\n\n{command_text}\n\n"
        f"## Key Files\n\n{key_file_text}\n\n"
        f"## Known Architecture Warnings\n\n{warning_text}\n\n"
        f"## Generated by VibeGraph\n\n{attribution}\n"
    )


def _internal_nodes(document: GraphDocument) -> list[GraphNode]:
    return [node for node in document.nodes if node.type != "unknown"]
