import asyncio
import json
from collections.abc import Mapping
from dataclasses import dataclass

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.domain.context_models import (
    ContextEnhancement,
    ContextRecommendation,
)
from app.domain.graph_models import GraphLink, GraphNode
from app.domain.graph_models import GraphDocument
from app.domain.readme_models import ReadmeEnhancement, ReadmeModule


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "deepseek/deepseek-v4-flash"


class ProviderReason(BaseModel):
    path: str
    reason: str


class ProviderEnhancement(BaseModel):
    rationale: str = Field(min_length=1, max_length=400)
    prompt: str = Field(min_length=1, max_length=4000)
    reasons: list[ProviderReason] = Field(default_factory=list, max_length=20)


class ProviderMessage(BaseModel):
    content: str


class ProviderChoice(BaseModel):
    message: ProviderMessage


class ProviderResponse(BaseModel):
    choices: list[ProviderChoice] = Field(min_length=1)


class ProviderModuleSummary(BaseModel):
    name: str
    summary: str = Field(min_length=1, max_length=400)


class ProviderReadmeEnhancement(BaseModel):
    rationale: str = Field(min_length=1, max_length=400)
    overview: str = Field(min_length=1, max_length=1200)
    architecture: str = Field(min_length=1, max_length=1200)
    modules: list[ProviderModuleSummary] = Field(
        default_factory=list, max_length=10
    )


@dataclass(frozen=True, slots=True)
class OpenRouterClient:
    api_key: str
    model: str = DEFAULT_MODEL
    timeout_seconds: float = 25.0
    transport: httpx.AsyncBaseTransport | None = None

    async def enhance(
        self,
        *,
        task: str,
        recommendations: tuple[ContextRecommendation, ...],
        nodes: dict[str, GraphNode],
        links: list[GraphLink],
        prompt: str,
    ) -> ContextEnhancement:
        selected = {item.path for item in recommendations}
        structured_context = {
            "task": task,
            "rankedFiles": [
                {
                    "path": item.path,
                    "reason": item.reason,
                    "score": item.score,
                    "language": nodes[item.path].language,
                    "type": nodes[item.path].type,
                    "exports": nodes[item.path].exports,
                    "inDegree": nodes[item.path].in_degree,
                    "outDegree": nodes[item.path].out_degree,
                }
                for item in recommendations
                if item.path in nodes
            ],
            "relationships": [
                {
                    "source": link.source,
                    "target": link.target,
                    "type": link.type,
                    "symbols": list(link.symbols),
                }
                for link in links
                if link.source in selected and link.target in selected
            ],
            "deterministicPrompt": prompt,
        }
        request_body = {
            "model": self.model,
            "temperature": 0.2,
            "max_tokens": 1200,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "context_pack_enhancement",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["rationale", "prompt", "reasons"],
                        "properties": {
                            "rationale": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 400,
                            },
                            "prompt": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 4000,
                            },
                            "reasons": {
                                "type": "array",
                                "maxItems": 8,
                                "items": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["path", "reason"],
                                    "properties": {
                                        "path": {"type": "string"},
                                        "reason": {
                                            "type": "string",
                                            "minLength": 1,
                                            "maxLength": 220,
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You improve wording for a graph-ranked code context "
                        "pack. Do not add files, claim to edit code, or imply "
                        "that source contents were provided. Return JSON with "
                        "rationale, prompt, and reasons as an array of "
                        "{path, reason} for the supplied ranked files. Keep "
                        "rationale under 250 characters, prompt under 2,500 "
                        "characters, and every reason under 180 characters. "
                        "Be concise and do not use markdown headings."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(structured_context),
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://127.0.0.1",
            "X-OpenRouter-Title": "VibeGraph",
        }
        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
            transport=self.transport,
        ) as client:
            async with asyncio.timeout(self.timeout_seconds):
                response = await client.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=request_body,
                )
            response.raise_for_status()

        try:
            provider_response = ProviderResponse.model_validate(response.json())
            content = provider_response.choices[0].message.content
            enhancement = ProviderEnhancement.model_validate_json(content)
        except (IndexError, json.JSONDecodeError, ValidationError) as error:
            raise ValueError("OpenRouter returned an invalid enhancement.") from error

        allowed_paths = {item.path for item in recommendations}
        return ContextEnhancement(
            rationale=enhancement.rationale,
            prompt=enhancement.prompt,
            reasons={
                item.path: item.reason
                for item in enhancement.reasons
                if item.path in allowed_paths
            },
        )

    async def enhance_readme(
        self,
        *,
        project_name: str,
        description: str,
        document: GraphDocument,
        modules: tuple[ReadmeModule, ...],
        entrypoints: tuple[str, ...],
        key_files: tuple[str, ...],
        commands: tuple[str, ...],
        warnings: tuple[str, ...],
    ) -> ReadmeEnhancement:
        structured_context = {
            "projectName": project_name,
            "userDescription": description,
            "stats": {
                "filesScanned": document.stats.files_scanned,
                "edgesFound": document.stats.edges_found,
                "warnings": document.stats.warnings,
                "languages": list(document.stats.languages),
            },
            "entrypoints": list(entrypoints),
            "keyFiles": list(key_files),
            "commands": list(commands),
            "warnings": list(warnings),
            "modules": [
                {
                    "name": module.name,
                    "files": list(module.files),
                    "entrypoints": list(module.entrypoints),
                }
                for module in modules
            ],
            "relationships": [
                {
                    "source": link.source,
                    "target": link.target,
                    "type": link.type,
                }
                for link in document.links
                if link.status == "healthy"
                and link.source in key_files
                and link.target in key_files
            ][:14],
        }
        request_body = {
            "model": self.model,
            "temperature": 0.2,
            "max_tokens": 1400,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "readme_prose_enhancement",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "rationale",
                            "overview",
                            "architecture",
                            "modules",
                        ],
                        "properties": {
                            "rationale": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 400,
                            },
                            "overview": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 1200,
                            },
                            "architecture": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 1200,
                            },
                            "modules": {
                                "type": "array",
                                "maxItems": 6,
                                "items": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["name", "summary"],
                                    "properties": {
                                        "name": {"type": "string"},
                                        "summary": {
                                            "type": "string",
                                            "minLength": 1,
                                            "maxLength": 400,
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Improve concise README prose from structured code-graph "
                        "metadata. Do not add modules, files, commands, warnings, "
                        "or architecture relationships. Source contents were not "
                        "provided. Return JSON only. Keep overview and "
                        "architecture factual and each module summary concise."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(structured_context),
                },
            ],
        }
        response = await self._post(request_body)
        try:
            content = response.choices[0].message.content
            enhancement = ProviderReadmeEnhancement.model_validate_json(content)
        except (IndexError, json.JSONDecodeError, ValidationError) as error:
            raise ValueError(
                "OpenRouter returned an invalid README enhancement."
            ) from error

        allowed_modules = {module.name for module in modules}
        return ReadmeEnhancement(
            rationale=enhancement.rationale,
            overview=enhancement.overview,
            architecture=enhancement.architecture,
            module_summaries={
                module.name: module.summary
                for module in enhancement.modules
                if module.name in allowed_modules
            },
        )

    async def _post(self, request_body: dict[str, object]) -> ProviderResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://127.0.0.1",
            "X-OpenRouter-Title": "VibeGraph",
        }
        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
            transport=self.transport,
        ) as client:
            async with asyncio.timeout(self.timeout_seconds):
                response = await client.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=request_body,
                )
            response.raise_for_status()
        try:
            return ProviderResponse.model_validate(response.json())
        except ValidationError as error:
            raise ValueError("OpenRouter returned an invalid response.") from error


def create_openrouter_client(
    environment: Mapping[str, str],
) -> OpenRouterClient | None:
    api_key = environment.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return None
    model = environment.get("VIBEGRAPH_MODEL", DEFAULT_MODEL).strip()
    return OpenRouterClient(api_key=api_key, model=model or DEFAULT_MODEL)
