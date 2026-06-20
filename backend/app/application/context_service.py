import math
import re
from collections import deque
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from app.domain.context_models import (
    ContextEnhancement,
    ContextPack,
    ContextPackOptions,
    ContextRecommendation,
)
from app.domain.graph_models import GraphDocument, GraphLink, GraphNode
from app.domain.output_paths import OutputPaths


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")
STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "for",
        "in",
        "of",
        "on",
        "the",
        "to",
        "with",
        "fix",
        "add",
        "change",
        "update",
        "implement",
        "js",
        "jsx",
        "py",
        "src",
        "test",
        "tests",
        "ts",
        "tsx",
    }
)


class ContextProvider(Protocol):
    model: str

    async def enhance(
        self,
        *,
        task: str,
        recommendations: tuple[ContextRecommendation, ...],
        nodes: dict[str, GraphNode],
        links: list[GraphLink],
        prompt: str,
    ) -> ContextEnhancement: ...


@dataclass(slots=True)
class ContextPackService:
    output_paths: OutputPaths
    graph_loader: Callable[[], GraphDocument]
    provider: ContextProvider | None = None

    async def generate(
        self,
        task: str,
        options: ContextPackOptions,
    ) -> ContextPack:
        clean_task = task.strip()
        document = self.graph_loader()
        recommendations = rank_context_files(document, clean_task, options)
        prompt = build_prompt(clean_task, recommendations)
        mode = "offline"
        model: str | None = None
        provider_message = "AI-enhanced wording is disabled; using graph heuristics."

        if self.provider is not None:
            model = self.provider.model
            try:
                enhancement = await self.provider.enhance(
                    task=clean_task,
                    recommendations=recommendations,
                    nodes={node.id: node for node in document.nodes},
                    links=document.links,
                    prompt=prompt,
                )
                recommendations = tuple(
                    ContextRecommendation(
                        path=item.path,
                        reason=enhancement.reasons.get(item.path, item.reason),
                        score=item.score,
                    )
                    for item in recommendations
                )
                prompt = enhancement.prompt
                mode = "enhanced"
                provider_message = enhancement.rationale
            except Exception:
                mode = "fallback"
                provider_message = (
                    "OpenRouter enhancement failed; deterministic graph "
                    "recommendations were preserved."
                )

        selected_nodes = {
            node.id: node
            for node in document.nodes
            if any(item.path == node.id for item in recommendations)
        }
        selected_bytes = sum(node.size_bytes for node in selected_nodes.values())
        repository_bytes = sum(
            node.size_bytes for node in document.nodes if node.type != "unknown"
        )
        estimated_tokens = max(1, math.ceil(selected_bytes / 4))
        reduction_percent = (
            max(0, round((1 - selected_bytes / repository_bytes) * 100))
            if repository_bytes
            else 0
        )
        mentions = "\n".join(f"@{item.path}" for item in recommendations)
        artifact_path = (
            self.output_paths.context.relative_to(
                self.output_paths.project_root
            ).as_posix()
        )
        pack = ContextPack(
            task=clean_task,
            mode=mode,  # type: ignore[arg-type]
            model=model,
            recommendations=recommendations,
            prompt=prompt,
            mentions=mentions,
            estimated_tokens=estimated_tokens,
            reduction_percent=reduction_percent,
            provider_message=provider_message,
            artifact_path=artifact_path,
        )
        self.output_paths.context.write_text(
            render_context_markdown(pack),
            encoding="utf-8",
        )
        return pack


def rank_context_files(
    document: GraphDocument,
    task: str,
    options: ContextPackOptions,
) -> tuple[ContextRecommendation, ...]:
    eligible = {
        node.id: node
        for node in document.nodes
        if _is_eligible(node, options)
    }
    if not eligible:
        return ()

    task_lower = task.lower()
    task_tokens = _tokens(task)
    base_scores: dict[str, float] = {}
    reasons: dict[str, list[str]] = {}
    explicit_seed_ids: list[str] = []

    for node_id, node in eligible.items():
        score = 0.0
        node_reasons: list[str] = []
        path_lower = node.path.lower()
        label_lower = node.label.lower()
        path_tokens = _tokens(node.path)
        export_tokens = {
            token
            for exported in node.exports
            for token in _tokens(exported)
        }

        if path_lower in task_lower:
            score += 120
            node_reasons.append("explicitly named in the task")
            explicit_seed_ids.append(node_id)
        elif label_lower in task_lower:
            score += 95
            node_reasons.append("filename named in the task")
            explicit_seed_ids.append(node_id)

        path_overlap = task_tokens & path_tokens
        if path_overlap:
            score += 18 * len(path_overlap)
            node_reasons.append(
                f"path matches {', '.join(sorted(path_overlap)[:3])}"
            )

        symbol_overlap = task_tokens & export_tokens
        if symbol_overlap:
            score += 24 * len(symbol_overlap)
            node_reasons.append(
                f"exports match {', '.join(sorted(symbol_overlap)[:3])}"
            )

        if node.is_entrypoint:
            score += 3
        score += node.risk_score * 5
        score += _recency_bonus(node.last_modified)
        base_scores[node_id] = score
        reasons[node_id] = node_reasons

    seed_ids = explicit_seed_ids[:4] or [
        node_id
        for node_id, score in sorted(
            base_scores.items(), key=lambda item: (-item[1], item[0])
        )
        if score >= 18
    ][:2]
    if not seed_ids:
        seed_ids = [
            node_id
            for node_id, _ in sorted(
                eligible.items(),
                key=lambda item: (
                    -(item[1].in_degree + item[1].out_degree),
                    item[0],
                ),
            )
        ][:2]

    distances, relation_reasons = _graph_distances(
        seed_ids,
        document.links,
        options.max_depth,
    )
    scored: list[tuple[str, float]] = []
    for node_id, node in eligible.items():
        score = base_scores[node_id]
        distance = distances.get(node_id)
        if distance is not None:
            score += {0: 65, 1: 56, 2: 25, 3: 10, 4: 4}.get(distance, 0)
            if relation_reasons.get(node_id):
                reasons[node_id].append(relation_reasons[node_id])
        if node.type == "test" and options.include_tests:
            score += 12
            reasons[node_id].append("relevant test coverage")
        scored.append((node_id, score))

    selected = sorted(scored, key=lambda item: (-item[1], item[0]))[
        : options.max_files
    ]
    return tuple(
        ContextRecommendation(
            path=node_id,
            reason="; ".join(dict.fromkeys(reasons[node_id]))
            or "high-connectivity graph neighbor",
            score=round(score, 2),
        )
        for node_id, score in selected
    )


def build_prompt(
    task: str,
    recommendations: tuple[ContextRecommendation, ...],
) -> str:
    files = "\n".join(
        f"- {item.path}: {item.reason}" for item in recommendations
    )
    return (
        f"Task: {task}\n\n"
        "Use only the repository files listed below as the initial context. "
        "Inspect their direct relationships before proposing changes. Do not "
        "assume files outside this set are irrelevant if the evidence points "
        "to an additional dependency.\n\n"
        f"Recommended files:\n{files}"
    )


def render_context_markdown(pack: ContextPack) -> str:
    files = "\n".join(
        f"{index}. `{item.path}` — {item.reason}"
        for index, item in enumerate(pack.recommendations, start=1)
    )
    model = pack.model or "none"
    return (
        "# VibeGraph Context Pack\n\n"
        f"## Task\n\n{pack.task}\n\n"
        f"## Mode\n\n- Mode: `{pack.mode}`\n- Model: `{model}`\n"
        f"- Provider status: {pack.provider_message}\n\n"
        f"## Recommended Files\n\n{files}\n\n"
        f"## File Mentions\n\n```text\n{pack.mentions}\n```\n\n"
        f"## Suggested Prompt\n\n```text\n{pack.prompt}\n```\n\n"
        "## Estimate\n\n"
        f"- Estimated context: {pack.estimated_tokens:,} tokens\n"
        f"- Reduction from full repository: {pack.reduction_percent}%\n"
    )


def _is_eligible(node: GraphNode, options: ContextPackOptions) -> bool:
    if node.type == "unknown":
        return False
    if node.type == "test" and not options.include_tests:
        return False
    if node.type == "config" and not options.include_config:
        return False
    if not options.include_docs and Path(node.path).suffix.lower() in {
        ".md",
        ".mdx",
        ".rst",
    }:
        return False
    return True


def _tokens(value: str) -> set[str]:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    normalized = re.sub(r"[_./-]+", " ", normalized)
    return {
        token.lower()
        for token in TOKEN_PATTERN.findall(normalized)
        if len(token) > 1 and token.lower() not in STOP_WORDS
    }


def _recency_bonus(value: str) -> float:
    if not value:
        return 0
    try:
        modified = datetime.fromisoformat(value)
        if modified.tzinfo is None:
            modified = modified.replace(tzinfo=timezone.utc)
        age_days = max(
            0,
            (datetime.now(timezone.utc) - modified.astimezone(timezone.utc)).days,
        )
        return max(0, 4 - age_days / 30)
    except ValueError:
        return 0


def _graph_distances(
    seeds: list[str],
    links: list[GraphLink],
    max_depth: int,
) -> tuple[dict[str, int], dict[str, str]]:
    adjacency: dict[str, list[tuple[str, str]]] = {}
    for link in links:
        adjacency.setdefault(link.source, []).append(
            (link.target, "direct dependency")
        )
        adjacency.setdefault(link.target, []).append(
            (link.source, "direct importer")
        )

    distances = {seed: 0 for seed in seeds}
    reasons: dict[str, str] = {}
    queue = deque(seeds)
    while queue:
        current = queue.popleft()
        distance = distances[current]
        if distance >= max_depth:
            continue
        for neighbor, relation in adjacency.get(current, []):
            next_distance = distance + 1
            if neighbor in distances and distances[neighbor] <= next_distance:
                continue
            distances[neighbor] = next_distance
            reasons[neighbor] = (
                relation
                if next_distance == 1
                else f"graph neighbor at depth {next_distance}"
            )
            queue.append(neighbor)
    return distances, reasons
