import ast
from pathlib import Path

import tree_sitter_javascript
import tree_sitter_typescript
from tree_sitter import Language, Node, Parser

from app.domain.graph_models import FileRecord, ImportRecord, ParsedFile


JAVASCRIPT_LANGUAGE = Language(tree_sitter_javascript.language())
TYPESCRIPT_LANGUAGE = Language(tree_sitter_typescript.language_typescript())
TSX_LANGUAGE = Language(tree_sitter_typescript.language_tsx())


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
    source_bytes = source.encode("utf-8")
    parser = Parser(_language_for(record.path))
    root = parser.parse(source_bytes).root_node
    imports: list[ImportRecord] = []
    exports: list[str] = []

    for node in root.named_children:
        if node.type == "import_statement":
            import_record = _import_from_statement(node, source_bytes)
            if _node_text(node, source_bytes).lstrip().startswith("import type"):
                # A type-only import has no runtime binding to validate.
                import_record = ImportRecord(import_record.module)
            imports.append(import_record)
        elif node.type == "export_statement":
            exported_import, exported_names = _export_from_statement(
                node, source_bytes
            )
            if exported_import is not None:
                imports.append(exported_import)
            exports.extend(exported_names)
        elif node.type == "expression_statement":
            exports.extend(_commonjs_exports(node, source_bytes))

    for node in _walk_named(root):
        if node.type != "call_expression":
            continue
        function = node.child_by_field_name("function")
        arguments = node.child_by_field_name("arguments")
        if function is None or arguments is None:
            continue
        is_dynamic_import = function.type == "import"
        is_require = (
            function.type == "identifier"
            and _node_text(function, source_bytes) == "require"
        )
        if not (is_dynamic_import or is_require):
            continue
        module_node = next(
            (child for child in arguments.named_children if child.type == "string"),
            None,
        )
        if module_node is not None:
            imports.append(
                ImportRecord(_string_value(module_node, source_bytes), dynamic=True)
            )

    unique_imports = tuple(
        dict.fromkeys((item.module, item.symbols, item.dynamic) for item in imports)
    )
    return ParsedFile(
        record,
        tuple(ImportRecord(module, symbols, dynamic) for module, symbols, dynamic in unique_imports),
        tuple(dict.fromkeys(exports)),
    )


def _language_for(path: str) -> Language:
    suffix = Path(path).suffix.lower()
    if suffix == ".ts":
        return TYPESCRIPT_LANGUAGE
    if suffix == ".tsx":
        return TSX_LANGUAGE
    return JAVASCRIPT_LANGUAGE


def _import_from_statement(node: Node, source: bytes) -> ImportRecord:
    source_node = node.child_by_field_name("source")
    module = _string_value(source_node, source) if source_node else ""
    symbols: list[str] = []
    clause = next(
        (child for child in node.named_children if child.type == "import_clause"),
        None,
    )
    if clause is None:
        return ImportRecord(module)

    for child in clause.named_children:
        if child.type == "identifier":
            symbols.append("default")
        elif child.type == "named_imports":
            symbols.extend(_source_names(child, "import_specifier", source))
        elif child.type == "namespace_import":
            continue
    return ImportRecord(module, tuple(dict.fromkeys(symbols)))


def _export_from_statement(
    node: Node,
    source: bytes,
) -> tuple[ImportRecord | None, tuple[str, ...]]:
    source_node = node.child_by_field_name("source")
    declaration = node.child_by_field_name("declaration")
    exported: list[str] = []
    imported: ImportRecord | None = None
    default_export = any(
        child.type == "default" or _node_text(child, source) == "default"
        for child in node.children
    )

    export_clause = next(
        (child for child in node.named_children if child.type == "export_clause"),
        None,
    )
    namespace_export = next(
        (
            child
            for child in node.named_children
            if child.type == "namespace_export"
        ),
        None,
    )

    if export_clause is not None:
        exported.extend(_alias_names(export_clause, "export_specifier", source))
    if namespace_export is not None:
        identifiers = [
            _node_text(child, source)
            for child in namespace_export.named_children
            if child.type in {"identifier", "type_identifier"}
        ]
        exported.extend(identifiers[-1:])

    if declaration is not None:
        exported.extend(_declared_names(declaration, source))
    if default_export:
        exported.append("default")

    if source_node is not None:
        module = _string_value(source_node, source)
        symbols = (
            _source_names(export_clause, "export_specifier", source)
            if export_clause is not None
            else ()
        )
        imported = ImportRecord(module, symbols)

    return imported, tuple(dict.fromkeys(exported))


def _commonjs_exports(node: Node, source: bytes) -> tuple[str, ...]:
    assignment = next(
        (
            child
            for child in node.named_children
            if child.type == "assignment_expression"
        ),
        None,
    )
    if assignment is None:
        return ()
    left = assignment.child_by_field_name("left")
    right = assignment.child_by_field_name("right")
    if left is None:
        return ()
    left_text = _node_text(left, source).replace(" ", "")
    if left_text in {"module.exports", "exports"}:
        if right is not None and right.type == "object":
            return _object_keys(right, source)
        return ("default",)
    if left_text.startswith("module.exports."):
        return (left_text.rsplit(".", 1)[-1],)
    if left_text.startswith("exports."):
        return (left_text.rsplit(".", 1)[-1],)
    return ()


def _object_keys(node: Node, source: bytes) -> tuple[str, ...]:
    keys: list[str] = []
    for child in node.named_children:
        if child.type == "pair":
            key = child.child_by_field_name("key")
            if key is not None:
                keys.append(_node_text(key, source).strip("\"'"))
        elif child.type == "shorthand_property_identifier":
            keys.append(_node_text(child, source))
    return tuple(keys)


def _declared_names(node: Node, source: bytes) -> tuple[str, ...]:
    name = node.child_by_field_name("name")
    if name is not None:
        return (_node_text(name, source),)
    if node.type in {"lexical_declaration", "variable_declaration"}:
        names = []
        for declarator in node.named_children:
            if declarator.type != "variable_declarator":
                continue
            declared = declarator.child_by_field_name("name")
            if declared is not None:
                names.extend(_binding_names(declared, source))
        return tuple(names)
    return ()


def _binding_names(node: Node, source: bytes) -> tuple[str, ...]:
    if node.type in {"identifier", "type_identifier"}:
        return (_node_text(node, source),)
    return tuple(
        _node_text(child, source)
        for child in _walk_named(node)
        if child.type in {"shorthand_property_identifier_pattern", "identifier"}
    )


def _source_names(
    container: Node,
    specifier_type: str,
    source: bytes,
) -> tuple[str, ...]:
    names: list[str] = []
    for specifier in container.named_children:
        if specifier.type != specifier_type:
            continue
        name = specifier.child_by_field_name("name")
        if name is not None:
            names.append(_node_text(name, source))
    return tuple(names)


def _alias_names(
    container: Node,
    specifier_type: str,
    source: bytes,
) -> tuple[str, ...]:
    names: list[str] = []
    for specifier in container.named_children:
        if specifier.type != specifier_type:
            continue
        alias = specifier.child_by_field_name("alias")
        name = specifier.child_by_field_name("name")
        selected = alias or name
        if selected is not None:
            names.append(_node_text(selected, source))
    return tuple(names)


def _walk_named(node: Node):
    for child in node.named_children:
        yield child
        yield from _walk_named(child)


def _string_value(node: Node, source: bytes) -> str:
    fragment = next(
        (child for child in node.named_children if child.type == "string_fragment"),
        None,
    )
    if fragment is not None:
        return _node_text(fragment, source)
    return _node_text(node, source).strip("\"'")


def _node_text(node: Node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")
