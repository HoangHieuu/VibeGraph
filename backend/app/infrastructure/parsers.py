import ast
import re
from pathlib import Path

from app.domain.graph_models import FileRecord, ImportRecord, ParsedFile


FROM_IMPORT_PATTERN = re.compile(
    r"""(?:import|export)\s+(?P<clause>[\s\S]*?)\s+from\s+["'](?P<module>[^"']+)["']"""
)
SIDE_EFFECT_IMPORT_PATTERN = re.compile(r"""import\s+["'](?P<module>[^"']+)["']""")
DYNAMIC_IMPORT_PATTERN = re.compile(r"""import\(\s*["'](?P<module>[^"']+)["']\s*\)""")
EXPORT_DECLARATION_PATTERN = re.compile(
    r"""\bexport\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var|interface|type|enum)\s+(?P<name>[A-Za-z_$][\w$]*)"""
)
EXPORT_LIST_PATTERN = re.compile(r"""\bexport\s*\{(?P<items>[^}]+)\}""")


def parse_file(project_root: Path, record: FileRecord) -> ParsedFile:
    source = (project_root / record.path).read_text(
        encoding="utf-8", errors="replace"
    )
    if record.language == "python":
        return _parse_python(record, source)
    return _parse_javascript(record, source)


def _parse_python(record: FileRecord, source: str) -> ParsedFile:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ParsedFile(file=record)

    imports: list[ImportRecord] = []
    exports: list[str] = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(ImportRecord(alias.name) for alias in node.names)
            exports.extend(
                alias.asname or alias.name.split(".", 1)[0]
                for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            module = f"{'.' * node.level}{node.module or ''}"
            imports.append(
                ImportRecord(module, tuple(alias.name for alias in node.names))
            )
            exports.extend(alias.asname or alias.name for alias in node.names)
        elif isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            exports.append(node.name)
        elif isinstance(node, ast.Assign):
            exports.extend(
                target.id
                for target in node.targets
                if isinstance(target, ast.Name)
            )
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            exports.append(node.target.id)

    return ParsedFile(record, tuple(imports), tuple(dict.fromkeys(exports)))


def _parse_javascript(record: FileRecord, source: str) -> ParsedFile:
    imports: list[ImportRecord] = []
    exports: list[str] = []

    for match in FROM_IMPORT_PATTERN.finditer(source):
        imports.append(
            ImportRecord(
                match.group("module"),
                _symbols_from_clause(match.group("clause")),
            )
        )

    for match in SIDE_EFFECT_IMPORT_PATTERN.finditer(source):
        imports.append(ImportRecord(match.group("module")))

    for match in DYNAMIC_IMPORT_PATTERN.finditer(source):
        imports.append(ImportRecord(match.group("module"), dynamic=True))

    exports.extend(
        match.group("name") for match in EXPORT_DECLARATION_PATTERN.finditer(source)
    )
    if re.search(r"\bexport\s+default\b", source):
        exports.append("default")
    for match in EXPORT_LIST_PATTERN.finditer(source):
        for item in match.group("items").split(","):
            exported = item.strip().split(" as ")[-1].strip()
            if exported:
                exports.append(exported)

    unique_imports = tuple(
        dict.fromkeys((item.module, item.symbols, item.dynamic) for item in imports)
    )
    return ParsedFile(
        record,
        tuple(ImportRecord(module, symbols, dynamic) for module, symbols, dynamic in unique_imports),
        tuple(dict.fromkeys(exports)),
    )


def _symbols_from_clause(clause: str) -> tuple[str, ...]:
    normalized = clause.strip()
    if normalized.startswith("type "):
        normalized = normalized.removeprefix("type ").strip()
    symbols: list[str] = []

    if normalized.startswith("{") and "}" in normalized:
        for item in normalized.strip("{} \n").split(","):
            symbol = (
                item.strip()
                .removeprefix("type ")
                .split(" as ")[0]
                .strip()
            )
            if symbol:
                symbols.append(symbol)
    elif normalized.startswith("* as "):
        symbols.append(normalized.removeprefix("* as ").strip())
    elif normalized:
        default_symbol, separator, remainder = normalized.partition(",")
        default_symbol = default_symbol.strip()
        if default_symbol:
            symbols.append(default_symbol)
        if separator and remainder.strip():
            symbols.extend(_symbols_from_clause(remainder))

    return tuple(symbols)
