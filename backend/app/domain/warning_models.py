from dataclasses import dataclass
from typing import Any, Literal


WarningType = Literal[
    "BROKEN_IMPORT",
    "DELETED_IMPORTED_FILE",
    "MISSING_EXPORTED_SYMBOL",
    "NEW_ORPHAN_FILE",
    "NEW_CIRCULAR_DEPENDENCY",
]


@dataclass(frozen=True, slots=True)
class GraphWarning:
    type: WarningType
    level: Literal["warn"]
    message: str
    source: str
    target: str
    symbol: str | None
    timestamp: str

    @property
    def key(self) -> str:
        return f"{self.type}:{self.source}:{self.target}:{self.symbol or ''}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "level": self.level,
            "message": self.message,
            "source": self.source,
            "target": self.target,
            "symbol": self.symbol,
            "timestamp": self.timestamp,
        }
