from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Literal


Language = Literal["python", "javascript", "typescript"]
NodeType = Literal["file", "folder", "entrypoint", "test", "config", "unknown"]
EdgeType = Literal[
    "imports",
    "imports_symbol",
    "dynamic_import",
    "test_targets",
    "broken_import",
]


@dataclass(frozen=True, slots=True)
class FileRecord:
    path: str
    language: Language
    loc: int
    size_bytes: int
    last_modified: str
    modified_ns: int


@dataclass(frozen=True, slots=True)
class ImportRecord:
    module: str
    symbols: tuple[str, ...] = ()
    dynamic: bool = False


@dataclass(frozen=True, slots=True)
class ParsedFile:
    file: FileRecord
    imports: tuple[ImportRecord, ...] = ()
    exports: tuple[str, ...] = ()


@dataclass(slots=True)
class GraphNode:
    id: str
    path: str
    label: str
    type: NodeType
    language: str
    group: str
    loc: int
    size_bytes: int
    last_modified: str
    exports: list[str] = field(default_factory=list)
    in_degree: int = 0
    out_degree: int = 0
    risk_score: float = 0.0
    is_entrypoint: bool = False
    is_orphan: bool = False
    has_warning: bool = False
    in_cycle: bool = False
    cycle_id: int | None = None


@dataclass(frozen=True, slots=True)
class GraphLink:
    source: str
    target: str
    type: EdgeType
    symbols: tuple[str, ...]
    status: str


@dataclass(frozen=True, slots=True)
class GraphStats:
    files_scanned: int
    edges_found: int
    warnings: int
    languages: tuple[str, ...]


@dataclass(slots=True)
class GraphDocument:
    project_root: str
    generated_at: str
    nodes: list[GraphNode]
    links: list[GraphLink]
    stats: GraphStats

    def to_dict(self) -> dict[str, Any]:
        return {
            "projectRoot": self.project_root,
            "generatedAt": self.generated_at,
            "nodes": [
                {
                    "id": node.id,
                    "path": node.path,
                    "label": node.label,
                    "type": node.type,
                    "language": node.language,
                    "group": node.group,
                    "loc": node.loc,
                    "sizeBytes": node.size_bytes,
                    "lastModified": node.last_modified,
                    "exports": node.exports,
                    "inDegree": node.in_degree,
                    "outDegree": node.out_degree,
                    "riskScore": node.risk_score,
                    "isEntrypoint": node.is_entrypoint,
                    "isOrphan": node.is_orphan,
                    "hasWarning": node.has_warning,
                    "inCycle": node.in_cycle,
                    "cycleId": node.cycle_id,
                }
                for node in self.nodes
            ],
            "links": [
                {
                    "source": link.source,
                    "target": link.target,
                    "type": link.type,
                    "symbols": list(link.symbols),
                    "status": link.status,
                }
                for link in self.links
            ],
            "stats": {
                "filesScanned": self.stats.files_scanned,
                "edgesFound": self.stats.edges_found,
                "warnings": self.stats.warnings,
                "languages": list(self.stats.languages),
            },
        }

    @classmethod
    def empty(cls, project_root: str) -> "GraphDocument":
        return cls(
            project_root=project_root,
            generated_at=datetime.now().astimezone().isoformat(),
            nodes=[],
            links=[],
            stats=GraphStats(0, 0, 0, ()),
        )
