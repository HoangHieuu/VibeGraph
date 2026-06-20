from datetime import datetime, timezone

import networkx as nx

from app.domain.graph_models import GraphDocument
from app.domain.warning_models import GraphWarning


def derive_warnings(
    previous: GraphDocument,
    current: GraphDocument,
    previous_warnings: tuple[GraphWarning, ...] = (),
    *,
    initialized: bool,
) -> tuple[GraphWarning, ...]:
    timestamp = datetime.now(timezone.utc).isoformat()
    warnings: dict[str, GraphWarning] = {}
    previous_by_key = {warning.key: warning for warning in previous_warnings}

    for link in current.links:
        if link.status == "unresolved":
            warning = _warning(
                "BROKEN_IMPORT",
                (
                    f"{link.source} could not resolve "
                    f"{link.target.removeprefix('unresolved:')}."
                ),
                link.source,
                link.target,
                None,
                timestamp,
            )
            warnings[warning.key] = warning
        elif link.status == "missing_symbol":
            target = next(
                (node for node in current.nodes if node.id == link.target), None
            )
            target_exports = set(target.exports if target else ())
            for symbol in link.symbols:
                if symbol in target_exports:
                    continue
                warning = _warning(
                    "MISSING_EXPORTED_SYMBOL",
                    (
                        f"{link.source} imports {symbol} from {link.target}, "
                        f"but {symbol} is not exported."
                    ),
                    link.source,
                    link.target,
                    symbol,
                    timestamp,
                )
                warnings[warning.key] = warning

    if not initialized:
        return tuple(sorted(warnings.values(), key=lambda item: item.key))

    current_node_ids = {
        node.id for node in current.nodes if node.type != "unknown"
    }
    for node in previous.nodes:
        if node.type == "unknown" or node.id in current_node_ids:
            continue
        for link in previous.links:
            if link.target != node.id or link.status not in {
                "healthy",
                "missing_symbol",
            }:
                continue
            warning = _warning(
                "DELETED_IMPORTED_FILE",
                f"{link.source} imports deleted file {node.id}.",
                link.source,
                node.id,
                None,
                timestamp,
            )
            warnings[warning.key] = previous_by_key.get(warning.key, warning)

    for warning in previous_warnings:
        if (
            warning.type == "DELETED_IMPORTED_FILE"
            and warning.target not in current_node_ids
            and warning.source in current_node_ids
        ):
            warnings[warning.key] = warning

    previous_nodes = {node.id: node for node in previous.nodes}
    for node in current.nodes:
        if node.type == "unknown" or not node.is_orphan:
            continue
        was_connected = (
            node.id in previous_nodes and not previous_nodes[node.id].is_orphan
        )
        warning = _warning(
            "NEW_ORPHAN_FILE",
            f"{node.id} has no incoming or outgoing local dependencies.",
            node.id,
            node.id,
            None,
            timestamp,
        )
        if was_connected or warning.key in previous_by_key:
            warnings[warning.key] = previous_by_key.get(warning.key, warning)

    for cycle in _cycles(current):
        source = cycle[0]
        target = " -> ".join((*cycle, cycle[0]))
        warning = _warning(
            "NEW_CIRCULAR_DEPENDENCY",
            f"Circular dependency detected: {target}.",
            source,
            target,
            None,
            timestamp,
        )
        previous_cycles = set(_cycles(previous))
        if cycle not in previous_cycles or warning.key in previous_by_key:
            warnings[warning.key] = previous_by_key.get(warning.key, warning)

    return tuple(sorted(warnings.values(), key=lambda item: item.key))


def _cycles(document: GraphDocument) -> tuple[tuple[str, ...], ...]:
    graph = nx.DiGraph()
    graph.add_nodes_from(
        node.id for node in document.nodes if node.type != "unknown"
    )
    graph.add_edges_from(
        (link.source, link.target)
        for link in document.links
        if link.status == "healthy"
    )
    normalized: set[tuple[str, ...]] = set()
    for cycle in nx.simple_cycles(graph):
        if len(cycle) < 2:
            continue
        rotations = [
            tuple(cycle[index:] + cycle[:index]) for index in range(len(cycle))
        ]
        normalized.add(min(rotations))
    return tuple(sorted(normalized))


def _warning(
    warning_type,
    message: str,
    source: str,
    target: str,
    symbol: str | None,
    timestamp: str,
) -> GraphWarning:
    return GraphWarning(
        type=warning_type,
        level="warn",
        message=message,
        source=source,
        target=target,
        symbol=symbol,
        timestamp=timestamp,
    )
