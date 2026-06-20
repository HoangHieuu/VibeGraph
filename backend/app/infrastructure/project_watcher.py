import threading
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from app.infrastructure.scanner import (
    IGNORED_DIRECTORIES,
    SUPPORTED_EXTENSIONS,
)


class ProjectEventHandler(FileSystemEventHandler):
    def __init__(self, notify: Callable[[Path], None]) -> None:
        self.notify = notify

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory or event.event_type in {
            "opened",
            "closed_no_write",
        }:
            return
        paths = [Path(event.src_path)]
        destination = getattr(event, "dest_path", "")
        if destination:
            paths.append(Path(destination))
        for path in paths:
            if is_supported_event_path(path):
                self.notify(path)


class ProjectWatcher:
    def __init__(
        self,
        project_root: Path,
        callback: Callable[[tuple[str, ...]], None],
        *,
        debounce_seconds: float = 0.75,
        poll_interval_seconds: float = 0.1,
    ) -> None:
        self.project_root = project_root.resolve()
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.observer = PollingObserver(timeout=poll_interval_seconds)
        self.handler = ProjectEventHandler(self.notify)
        self._pending: set[str] = set()
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def start(self) -> None:
        self.observer.schedule(
            self.handler,
            str(self.project_root),
            recursive=True,
        )
        self.observer.start()

    def stop(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
        self.observer.stop()
        self.observer.join(timeout=5)

    def notify(self, path: Path) -> None:
        try:
            relative = path.resolve().relative_to(self.project_root).as_posix()
        except ValueError:
            return
        with self._lock:
            self._pending.add(relative)
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(
                self.debounce_seconds,
                self._flush,
            )
            self._timer.daemon = True
            self._timer.start()

    def _flush(self) -> None:
        with self._lock:
            changed = tuple(sorted(self._pending))
            self._pending.clear()
            self._timer = None
        if changed:
            self.callback(changed)


def is_supported_event_path(path: Path) -> bool:
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False
    return not any(part in IGNORED_DIRECTORIES for part in path.parts)
