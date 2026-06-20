import type {
  GraphDocument,
  GraphFilters,
  GraphLink,
  GraphMode,
  GraphNode,
} from "../types/graph";

export function endpointId(endpoint: string | GraphNode): string {
  return typeof endpoint === "string" ? endpoint : endpoint.id;
}

export function filterGraph(
  graph: GraphDocument,
  filters: GraphFilters,
): Pick<GraphDocument, "nodes" | "links"> {
  const visibleNodes = graph.nodes.filter((node) => {
    if (!filters.tests && node.type === "test") return false;
    if (!filters.config && node.type === "config") return false;
    if (!filters.orphans && node.isOrphan) return false;
    return true;
  });
  const visibleIds = new Set(visibleNodes.map((node) => node.id));
  return {
    nodes: visibleNodes,
    links: graph.links.filter(
      (link) =>
        visibleIds.has(endpointId(link.source)) &&
        visibleIds.has(endpointId(link.target)),
    ),
  };
}

export function graphForMode(
  graph: Pick<GraphDocument, "nodes" | "links">,
  mode: GraphMode,
): Pick<GraphDocument, "nodes" | "links"> {
  if (mode === "files") return graph;

  const moduleByNode = new Map<string, string>();
  const modules = new Map<string, GraphNode>();
  for (const node of graph.nodes) {
    const folder =
      node.type === "unknown"
        ? "External"
        : node.path.includes("/")
          ? node.path.split("/").slice(0, -1).join("/")
          : "Root";
    const id = `module:${folder}`;
    moduleByNode.set(node.id, id);
    const existing = modules.get(id);
    if (existing) {
      existing.loc += node.loc;
      existing.inDegree += node.inDegree;
      existing.outDegree += node.outDegree;
      existing.hasWarning ||= node.hasWarning;
      existing.exports.push(node.id);
    } else {
      modules.set(id, {
        ...node,
        id,
        path: folder,
        label: folder.split("/").at(-1) ?? folder,
        type: "folder",
        exports: [node.id],
      });
    }
  }

  const linkKeys = new Set<string>();
  const links: GraphLink[] = [];
  for (const link of graph.links) {
    const source = moduleByNode.get(endpointId(link.source));
    const target = moduleByNode.get(endpointId(link.target));
    if (!source || !target || source === target) continue;
    const key = `${source}->${target}`;
    if (linkKeys.has(key)) continue;
    linkKeys.add(key);
    links.push({ ...link, source, target });
  }
  return { nodes: [...modules.values()], links };
}

export function searchNodes(
  nodes: GraphNode[],
  query: string,
): GraphNode[] {
  const normalized = query.trim().toLowerCase();
  if (!normalized) return [];
  return nodes
    .filter(
      (node) =>
        node.label.toLowerCase().includes(normalized) ||
        node.path.toLowerCase().includes(normalized),
    )
    .slice(0, 8);
}

export function neighborsFor(
  nodeId: string,
  links: GraphLink[],
): Set<string> {
  const neighbors = new Set([nodeId]);
  for (const link of links) {
    const source = endpointId(link.source);
    const target = endpointId(link.target);
    if (source === nodeId) neighbors.add(target);
    if (target === nodeId) neighbors.add(source);
  }
  return neighbors;
}

export function linkKey(link: GraphLink): string {
  return `${endpointId(link.source)}->${endpointId(link.target)}:${link.type}`;
}

export function highlightFor(
  nodeId: string | null,
  links: GraphLink[],
): {
  nodes: Set<string>;
  links: Set<string>;
} {
  const highlightedNodes = new Set<string>();
  const highlightedLinks = new Set<string>();
  if (!nodeId) {
    return { nodes: highlightedNodes, links: highlightedLinks };
  }

  highlightedNodes.add(nodeId);
  for (const link of links) {
    const source = endpointId(link.source);
    const target = endpointId(link.target);
    if (source !== nodeId && target !== nodeId) continue;

    highlightedNodes.add(source);
    highlightedNodes.add(target);
    highlightedLinks.add(linkKey(link));
  }

  return { nodes: highlightedNodes, links: highlightedLinks };
}
