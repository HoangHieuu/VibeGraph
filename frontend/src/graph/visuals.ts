import type { GraphNode } from "../types/graph";

const MIN_NODE_RADIUS = 2.8;
const MAX_NODE_RADIUS = 8.5;
const LABEL_ZOOM_THRESHOLD = 2.15;

export function nodeRadius(node: GraphNode): number {
  const degree = Math.max(0, node.inDegree + node.outDegree);
  return Math.min(
    MAX_NODE_RADIUS,
    MIN_NODE_RADIUS + Math.sqrt(degree) * 1.05,
  );
}

export function shouldShowNodeLabel(
  globalScale: number,
  emphasized: boolean,
): boolean {
  return emphasized || globalScale >= LABEL_ZOOM_THRESHOLD;
}
