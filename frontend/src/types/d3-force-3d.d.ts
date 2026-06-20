declare module "d3-force-3d" {
  interface ForceCollide<NodeDatum> {
    (alpha: number): void;
    initialize(nodes: NodeDatum[], ...args: unknown[]): void;
    iterations(value: number): ForceCollide<NodeDatum>;
    radius(
      value: number | ((node: NodeDatum) => number),
    ): ForceCollide<NodeDatum>;
    strength(value: number): ForceCollide<NodeDatum>;
  }

  export function forceCollide<NodeDatum>(
    radius?: number | ((node: NodeDatum) => number),
  ): ForceCollide<NodeDatum>;

  interface ForceRadial<NodeDatum> {
    (alpha: number): void;
    initialize(nodes: NodeDatum[], ...args: unknown[]): void;
    strength(
      value: number | ((node: NodeDatum) => number),
    ): ForceRadial<NodeDatum>;
  }

  export function forceRadial<NodeDatum>(
    radius?: number | ((node: NodeDatum) => number),
    x?: number,
    y?: number,
  ): ForceRadial<NodeDatum>;
}
