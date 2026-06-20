from pathlib import Path

from app.domain.output_paths import OutputPaths


class OutputDirectoryError(RuntimeError):
    """Raised when VibeGraph cannot prepare its generated-output boundary."""


def ensure_output_directory(project_root: Path) -> OutputPaths:
    try:
        paths = OutputPaths.for_project(project_root)
        paths.directory.mkdir(mode=0o755, exist_ok=True)
    except (OSError, ValueError) as error:
        raise OutputDirectoryError(
            f"Unable to prepare VibeGraph output directory for "
            f"'{project_root}': {error}"
        ) from error

    if not paths.directory.is_dir():
        raise OutputDirectoryError(
            f"VibeGraph output path is not a directory: {paths.directory}"
        )

    return paths
