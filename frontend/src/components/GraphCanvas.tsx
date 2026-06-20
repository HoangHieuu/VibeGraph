import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import ForceGraph2D, {
  type ForceGraphMethods,
  type NodeObject,
} from "react-force-graph-2d";
import { forceCollide, forceRadial } from "d3-force-3d";

import {
  highlightFor,
  linkKey,
  neighborsFor,
} from "../graph/transforms";
import { nodeRadius, shouldShowNodeLabel } from "../graph/visuals";
import type { GraphLink, GraphNode } from "../types/graph";

const GROUP_COLORS: Record<string, string> = {
  frontend: "#49d5cf",
  backend: "#6d97ff",
  agent: "#60e0ac",
  test: "#b77af4",
  config: "#e8a423",
  external: "#70787c",
  root: "#8b9498",
};

interface GraphCanvasProps {
  nodes: GraphNode[];
  links: GraphLink[];
  selectedId: string | null;
  matchedIds: Set<string>;
  focusRequest: number;
  onSelectNode: (node: GraphNode) => void;
}

export function GraphCanvas({
  nodes,
  links,
  selectedId,
  matchedIds,
  focusRequest,
  onSelectNode,
}: GraphCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<
    ForceGraphMethods<GraphNode, GraphLink> | undefined
  >(undefined);
  const [size, setSize] = useState({ width: 800, height: 600 });
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const highlights = useMemo(
    () => highlightFor(hoveredId, links),
    [hoveredId, links],
  );
  const hoverActive = hoveredId !== null;

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const observer = new ResizeObserver(([entry]) => {
      if (entry) {
        setSize({
          width: Math.max(320, entry.contentRect.width),
          height: Math.max(300, entry.contentRect.height),
        });
      }
    });
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!selectedId || focusRequest === 0) return;
    const selected = nodes.find((node) => node.id === selectedId) as
      | NodeObject<GraphNode>
      | undefined;
    if (selected?.x !== undefined && selected.y !== undefined) {
      graphRef.current?.centerAt(selected.x, selected.y, 450);
      graphRef.current?.zoom(2.6, 450);
    }
  }, [focusRequest, nodes, selectedId]);

  useEffect(() => {
    const graph = graphRef.current;
    if (!graph || nodes.length === 0) return;

    const charge = graph.d3Force("charge") as
      | {
          distanceMax(value: number): unknown;
          strength(value: number): {
            distanceMax(value: number): unknown;
          };
        }
      | undefined;
    charge?.strength(-68).distanceMax(420);

    const link = graph.d3Force("link") as
      | {
          distance(value: number): {
            strength(value: number): unknown;
          };
        }
      | undefined;
    link?.distance(38).strength(0.46);

    graph.d3Force(
      "collide",
      forceCollide<NodeObject<GraphNode>>(
        (node) => nodeRadius(node) + 3.5,
      )
        .strength(0.95)
        .iterations(2),
    );
    graph.d3Force(
      "radial",
      forceRadial<NodeObject<GraphNode>>(0).strength(0.025),
    );
    graph.d3ReheatSimulation();
  }, [links, nodes]);

  const drawNode = useCallback(
    (
      node: NodeObject<GraphNode>,
      context: CanvasRenderingContext2D,
      globalScale: number,
    ) => {
      const x = node.x ?? 0;
      const y = node.y ?? 0;
      const selected = node.id === selectedId;
      const matched = matchedIds.has(String(node.id));
      const hovered = node.id === hoveredId;
      const connected = highlights.nodes.has(String(node.id));
      const emphasized = selected || matched || connected;
      const color = node.hasWarning
        ? "#e56f61"
        : GROUP_COLORS[node.group] ?? "#8b9498";
      const radius = nodeRadius(node);
      const dimmed = hoverActive && !connected;

      context.beginPath();
      context.arc(x, y, radius, 0, Math.PI * 2);
      context.globalAlpha = dimmed ? 0.1 : hovered ? 1 : connected ? 0.92 : 0.78;
      context.fillStyle = hovered ? "#45d7ff" : connected ? "#d8f8ff" : color;
      context.fill();
      context.lineWidth = (selected ? 2.2 : matched ? 1.8 : 0.9) / globalScale;
      context.strokeStyle = hovered
        ? "#ffffff"
        : node.hasWarning
          ? "#ffc0b8"
        : emphasized
          ? "#8eeaff"
          : "#101416";
      context.stroke();
      context.globalAlpha = 1;

      if (selected) {
        context.beginPath();
        context.arc(x, y, radius + 3 / globalScale, 0, Math.PI * 2);
        context.lineWidth = 1.4 / globalScale;
        context.strokeStyle = "rgba(101, 227, 180, 0.72)";
        context.stroke();
      }

      if (!shouldShowNodeLabel(globalScale, emphasized)) return;

      const label = node.label;
      const fontSize = 11 / globalScale;
      context.font = `600 ${fontSize}px Inter, sans-serif`;
      const textWidth = context.measureText(label).width;
      const paddingX = 4 / globalScale;
      const paddingY = 2.5 / globalScale;
      const labelX = x + radius + 4 / globalScale;
      const labelY = y - radius - 2 / globalScale;

      context.fillStyle = "rgba(16, 20, 22, 0.86)";
      context.beginPath();
      context.roundRect(
        labelX - paddingX,
        labelY - fontSize / 2 - paddingY,
        textWidth + paddingX * 2,
        fontSize + paddingY * 2,
        2 / globalScale,
      );
      context.fill();
      context.fillStyle = hovered
        ? "#ffffff"
        : connected
          ? "#d8f8ff"
          : "#d5dbdd";
      context.textAlign = "left";
      context.textBaseline = "middle";
      context.fillText(label, labelX, labelY);
    },
    [
      highlights.nodes,
      hoverActive,
      hoveredId,
      matchedIds,
      selectedId,
    ],
  );

  const paintPointer = useCallback(
    (
      node: NodeObject<GraphNode>,
      color: string,
      context: CanvasRenderingContext2D,
      globalScale: number,
    ) => {
      const radius = nodeRadius(node) + 9 / globalScale;
      context.fillStyle = color;
      context.beginPath();
      context.arc(node.x ?? 0, node.y ?? 0, radius, 0, Math.PI * 2);
      context.fill();
    },
    [],
  );

  return (
    <div className="graph-canvas" ref={containerRef}>
      <ForceGraph2D<GraphNode, GraphLink>
        backgroundColor="#101416"
        cooldownTicks={180}
        d3VelocityDecay={0.32}
        enableNodeDrag
        enablePanInteraction
        enableZoomInteraction
        graphData={{ nodes, links }}
        height={size.height}
        linkColor={(link) =>
          hoverActive
            ? highlights.links.has(linkKey(link))
              ? "#52d9ff"
              : "rgba(255,255,255,0.035)"
            : !["healthy", "external"].includes(link.status)
              ? "#c5695f"
              : "#424a4e"
        }
        linkDirectionalArrowColor={(link) =>
          hoverActive
            ? highlights.links.has(linkKey(link))
              ? "#9cecff"
              : "rgba(255,255,255,0.025)"
            : !["healthy", "external"].includes(link.status)
              ? "#c5695f"
              : "#596267"
        }
        linkDirectionalArrowLength={2.4}
        linkDirectionalArrowRelPos={0.85}
        linkWidth={(link) =>
          hoverActive
            ? highlights.links.has(linkKey(link))
              ? 1.8
              : 0.35
            : !["healthy", "external"].includes(link.status)
              ? 1.2
              : 0.8
        }
        nodeCanvasObject={drawNode}
        nodeLabel=""
        nodePointerAreaPaint={paintPointer}
        onEngineStop={() => graphRef.current?.zoomToFit(350, 30)}
        onNodeClick={(node, event) => {
          onSelectNode(node);
          if (event.detail >= 2) {
            const neighbors = neighborsFor(node.id, links);
            graphRef.current?.zoomToFit(
              450,
              90,
              (candidate) => neighbors.has(String(candidate.id)),
            );
          }
        }}
        onNodeHover={(node) => setHoveredId(node?.id ?? null)}
        ref={graphRef}
        showPointerCursor
        width={size.width}
      />
    </div>
  );
}
