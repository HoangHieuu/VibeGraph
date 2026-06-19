const nodes = [
  [12, 22],
  [20, 36],
  [31, 27],
  [39, 18],
  [47, 31],
  [57, 17],
  [66, 27],
  [77, 22],
  [86, 38],
  [18, 64],
  [29, 72],
  [42, 63],
  [53, 76],
  [67, 67],
  [79, 72],
];

const links = [
  [0, 1],
  [1, 2],
  [2, 3],
  [2, 4],
  [3, 4],
  [4, 5],
  [5, 6],
  [6, 7],
  [7, 8],
  [9, 10],
  [10, 11],
  [11, 12],
  [11, 13],
  [13, 14],
];

export function GraphBackdrop() {
  return (
    <svg
      aria-hidden="true"
      className="graph-backdrop"
      preserveAspectRatio="none"
      viewBox="0 0 100 100"
    >
      {links.map(([sourceIndex, targetIndex]) => {
        const source = nodes[sourceIndex];
        const target = nodes[targetIndex];

        if (!source || !target) {
          return null;
        }

        return (
          <line
            key={`${sourceIndex}-${targetIndex}`}
            x1={source[0]}
            x2={target[0]}
            y1={source[1]}
            y2={target[1]}
          />
        );
      })}

      {nodes.map(([x, y], index) => (
        <g key={`${x}-${y}`} transform={`translate(${x} ${y})`}>
          <rect height="2.8" rx="0.35" width="2.4" x="-1.2" y="-1.4" />
          <path d="M-.55-.35 0 .1-.55.55M.55-.35 0 .1.55.55" />
          <title>{`Preview file node ${index + 1}`}</title>
        </g>
      ))}
    </svg>
  );
}
