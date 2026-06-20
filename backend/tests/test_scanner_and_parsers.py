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
    assert parsed.imports[0].symbols == ("session",)
    assert parsed.imports[1].symbols == ("AuthError",)
    assert parsed.imports[2].symbols == ("Client", "Session", "refresh")
    assert parsed.imports[3].symbols == ("tools",)
    assert parsed.imports[4].dynamic is True
    assert parsed.exports == (
        "login",
        "AuthController",
        "logout",
        "default",
    )
