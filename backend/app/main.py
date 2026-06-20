import asyncio
import os
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pydantic import Field

from app.application.context_service import ContextPackService
from app.application.graph_service import ProjectGraphService
from app.application.readme_service import ReadmeService
from app.domain.context_models import ContextPackOptions
from app.infrastructure.openrouter_client import create_openrouter_client
from app.infrastructure.output_directory import ensure_output_directory
from app.infrastructure.event_broker import EventBroker
from app.infrastructure.project_watcher import ProjectWatcher


class HealthResponse(BaseModel):
    status: str
    service: str
    mode: str


class ContextPackRequest(BaseModel):
    task: str = Field(min_length=3, max_length=2000)
    max_files: int = Field(default=8, alias="maxFiles", ge=1, le=20)
    max_depth: int = Field(default=2, alias="maxDepth", ge=0, le=4)
    include_tests: bool = Field(default=True, alias="includeTests")
    include_config: bool = Field(default=False, alias="includeConfig")
    include_docs: bool = Field(default=False, alias="includeDocs")


class ReadmeRequest(BaseModel):
    description: str = Field(default="", max_length=2000)


def resolve_project_root(
    environment: Mapping[str, str] = os.environ,
    current_directory: Path | None = None,
) -> Path:
    configured_root = environment.get("VIBEGRAPH_PROJECT_ROOT")

    if configured_root:
        return Path(configured_root)

    return current_directory or Path.cwd()


def create_app(
    project_root: Path | None = None,
    environment: Mapping[str, str] = os.environ,
    context_provider: object | None = None,
    frontend_root: Path | None = None,
    watcher_enabled: bool = True,
    watcher_debounce_seconds: float = 0.75,
) -> FastAPI:
    selected_project_root = project_root or resolve_project_root()
    selected_frontend_root = frontend_root
    if selected_frontend_root is None:
        configured_frontend_root = environment.get("VIBEGRAPH_FRONTEND_ROOT")
        if configured_frontend_root:
            selected_frontend_root = Path(configured_frontend_root)

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        loop = asyncio.get_running_loop()
        output_paths = ensure_output_directory(selected_project_root)
        graph_service = ProjectGraphService.create(
            output_paths.project_root, output_paths
        )
        provider = (
            context_provider
            if context_provider is not None
            else create_openrouter_client(environment)
        )
        context_service = ContextPackService(
            output_paths=output_paths,
            graph_loader=lambda: graph_service.document,
            provider=provider,  # type: ignore[arg-type]
        )
        readme_service = ReadmeService(
            output_paths=output_paths,
            graph_loader=lambda: graph_service.document,
            provider=provider,  # type: ignore[arg-type]
        )
        application.state.output_paths = output_paths
        application.state.graph_service = graph_service
        application.state.context_service = context_service
        application.state.readme_service = readme_service
        application.state.event_broker = EventBroker()
        application.state.scan_lock = asyncio.Lock()
        graph_service.scan()

        def schedule_scan(changed_paths: tuple[str, ...]) -> None:
            loop.call_soon_threadsafe(
                lambda: asyncio.create_task(
                    publish_scan(application, changed_paths)
                )
            )

        watcher = ProjectWatcher(
            output_paths.project_root,
            schedule_scan,
            debounce_seconds=watcher_debounce_seconds,
        )
        application.state.watcher = watcher
        if watcher_enabled:
            watcher.start()
        try:
            yield
        finally:
            if watcher_enabled:
                watcher.stop()

    application = FastAPI(
        title="VibeGraph Local API",
        description="Local-first codebase analysis runtime.",
        version="0.1.0",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @application.get("/api/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="vibegraph-backend",
            mode="local",
        )

    @application.get("/api/project")
    async def project() -> dict[str, object]:
        service: ProjectGraphService = application.state.graph_service
        return {
            "projectRoot": str(service.project_root),
            "projectName": service.project_root.name,
            "stats": service.document.to_dict()["stats"],
        }

    @application.get("/api/graph")
    async def graph() -> dict[str, object]:
        service: ProjectGraphService = application.state.graph_service
        return service.document.to_dict()

    @application.get("/api/files/{file_path:path}")
    async def file_detail(file_path: str) -> dict[str, object]:
        service: ProjectGraphService = application.state.graph_service
        detail = service.file_detail(file_path)
        if detail is None:
            raise HTTPException(status_code=404, detail="File not found in graph.")
        return detail

    @application.get("/api/warnings")
    async def warnings() -> list[dict[str, object]]:
        service: ProjectGraphService = application.state.graph_service
        return [warning.to_dict() for warning in service.warnings]

    @application.post("/api/rescan")
    async def rescan() -> dict[str, object]:
        await publish_scan(application, ("manual-rescan",))
        service: ProjectGraphService = application.state.graph_service
        return service.document.to_dict()

    @application.post("/api/context-pack")
    async def context_pack(request: ContextPackRequest) -> dict[str, object]:
        service: ContextPackService = application.state.context_service
        result = await service.generate(
            request.task,
            ContextPackOptions(
                max_files=request.max_files,
                max_depth=request.max_depth,
                include_tests=request.include_tests,
                include_config=request.include_config,
                include_docs=request.include_docs,
            ),
        )
        return result.to_dict()

    @application.post("/api/readme")
    async def readme(request: ReadmeRequest) -> dict[str, object]:
        service: ReadmeService = application.state.readme_service
        result = await service.generate(request.description)
        return result.to_dict()

    @application.websocket("/ws/events")
    async def events(websocket: WebSocket) -> None:
        broker: EventBroker = application.state.event_broker
        await broker.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            broker.disconnect(websocket)

    if selected_frontend_root is not None:
        frontend_index = selected_frontend_root / "index.html"
        if not frontend_index.is_file():
            raise RuntimeError(
                f"VibeGraph frontend index was not found: {frontend_index}"
            )
        application.mount(
            "/",
            StaticFiles(directory=selected_frontend_root, html=True),
            name="frontend",
        )

    return application


app = create_app()


async def publish_scan(
    application: FastAPI,
    changed_paths: tuple[str, ...],
) -> None:
    lock: asyncio.Lock = application.state.scan_lock
    async with lock:
        service: ProjectGraphService = application.state.graph_service
        previous_warning_keys = {warning.key for warning in service.warnings}
        document = await asyncio.to_thread(service.scan)
        warnings = [warning.to_dict() for warning in service.warnings]
        broker: EventBroker = application.state.event_broker
        await broker.broadcast(
            {
                "type": "graph_updated",
                "changedPaths": list(changed_paths),
                "graph": document.to_dict(),
                "warnings": warnings,
            }
        )
        for warning in service.warnings:
            if warning.key not in previous_warning_keys:
                await broker.broadcast(
                    {
                        "type": "warning_created",
                        "warning": warning.to_dict(),
                    }
                )
