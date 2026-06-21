from pathlib import Path

from app.infrastructure.parsers import parse_file
from app.infrastructure.scanner import scan_repository


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_scanner_detects_supported_languages_and_ignores_noise(
    tmp_path: Path,
) -> None:
    write(tmp_path / "app.py", "import os\n")
    write(tmp_path / "src" / "main.js", "export const value = 1\n")
    write(tmp_path / "src" / "view.jsx", "export default function View() {}\n")
    write(tmp_path / "src" / "tool.ts", "export function tool() {}\n")
    write(tmp_path / "src" / "App.tsx", "export default function App() {}\n")
    write(tmp_path / "node_modules" / "ignored.ts", "export const ignored = 1\n")
    write(tmp_path / ".vibegraph" / "generated.ts", "export const ignored = 1\n")
    write(
        tmp_path / "backend" / ".uv-cache" / "ignored.py",
        "ignored = True\n",
    )
    write(tmp_path / "dist" / "bundle.js", "export const ignored = 1\n")
    write(tmp_path / "src" / "bundle.min.js", "export const ignored = 1\n")
    write(tmp_path / "README.md", "ignored\n")

    records = scan_repository(tmp_path)

    assert [record.path for record in records] == [
        "app.py",
        "src/App.tsx",
        "src/main.js",
        "src/tool.ts",
        "src/view.jsx",
    ]
    assert {record.language for record in records} == {
        "python",
        "javascript",
        "typescript",
    }


def test_scanner_honors_gitignore_patterns(tmp_path: Path) -> None:
    write(tmp_path / ".gitignore", "generated/\n*.local.ts\n/secrets.ts\n")
    write(tmp_path / "keep.ts", "export const keep = 1\n")
    write(tmp_path / "generated" / "schema.ts", "export const gen = 1\n")
    write(tmp_path / "src" / "config.local.ts", "export const local = 1\n")
    write(tmp_path / "secrets.ts", "export const secret = 1\n")
    write(tmp_path / "src" / "nested" / "secrets.ts", "export const ok = 1\n")

    records = scan_repository(tmp_path)

    assert [record.path for record in records] == [
        "keep.ts",
        "src/nested/secrets.ts",
    ]


def test_javascript_parser_extracts_commonjs_and_type_only_imports(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "legacy.js",
        "\n".join(
            [
                'const config = require("./config");',
                'import type { Session } from "./session";',
                'import "./styles.css";',
                "function build() { return config; }",
                "module.exports = { build, version: 1 };",
                'exports.helper = () => config;',
            ]
        ),
    )
    record = scan_repository(tmp_path)[0]

    parsed = parse_file(tmp_path, record)

    modules = [item.module for item in parsed.imports]
    assert "./config" in modules
    assert "./styles.css" in modules
    require_import = next(
        item for item in parsed.imports if item.module == "./config"
    )
    assert require_import.dynamic is True
    type_import = next(
        item for item in parsed.imports if item.module == "./session"
    )
    assert type_import.symbols == ()
    assert "build" in parsed.exports
    assert "version" in parsed.exports
    assert "helper" in parsed.exports


def test_python_parser_extracts_imports_and_top_level_exports(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "api.py",
        "\n".join(
            [
                "import os",
                "from services.session import validate_session",
                "DEFAULT_TIMEOUT = 30",
                "async def login(): pass",
                "class AuthController: pass",
            ]
        ),
    )
    record = scan_repository(tmp_path)[0]

    parsed = parse_file(tmp_path, record)

    assert [item.module for item in parsed.imports] == [
        "os",
        "services.session",
    ]
    assert parsed.imports[1].symbols == ("validate_session",)
    assert parsed.exports == (
        "os",
        "validate_session",
        "DEFAULT_TIMEOUT",
        "login",
        "AuthController",
    )


def test_typescript_parser_extracts_import_variants_and_exports(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "auth.ts",
        "\n".join(
            [
                'import session from "./session";',
                'import { AuthError as ErrorType } from "./errors";',
                'import Client, { type Session, refresh } from "./client";',
                'import * as tools from "./tools";',
                'const lazy = import("./lazy");',
                "export function login() {}",
                "export class AuthController {}",
                "export const logout = () => {};",
                "export default login;",
            ]
        ),
    )
    record = scan_repository(tmp_path)[0]

    parsed = parse_file(tmp_path, record)

    assert [item.module for item in parsed.imports] == [
        "./session",
        "./errors",
        "./client",
        "./tools",
        "./lazy",
    ]
    assert parsed.imports[0].symbols == ("default",)
    assert parsed.imports[1].symbols == ("AuthError",)
    assert parsed.imports[2].symbols == ("default", "Session", "refresh")
    assert parsed.imports[3].symbols == ()
    assert parsed.imports[4].dynamic is True
    assert parsed.exports == (
        "login",
        "AuthController",
        "logout",
        "default",
    )


def test_typescript_parser_ignores_text_and_tracks_reexports(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "index.ts",
        "\n".join(
            [
                '// import { fake } from "./comment";',
                "const text = \"import fake from './string'\";",
                'export { helper as renamed } from "./helper";',
                'export * as tools from "./tools";',
                "export interface Session { id: string }",
            ]
        ),
    )
    parsed = parse_file(tmp_path, scan_repository(tmp_path)[0])

    assert [(item.module, item.symbols) for item in parsed.imports] == [
        ("./helper", ("helper",)),
        ("./tools", ()),
    ]
    assert parsed.exports == ("renamed", "tools", "Session")
