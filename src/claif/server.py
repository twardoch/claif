"""MCP server implementation for Claif."""

from typing import Any

import anyio
from fastmcp import FastMCP
from mcp.server import Server
from pydantic import BaseModel

from claif.client import query, query_all, query_random
from claif.common import ClaifOptions, Config, Provider, logger


# Pydantic models for MCP
class QueryRequest(BaseModel):
    """Request model for query endpoint."""

    prompt: str
    provider: str | None = None
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    system_prompt: str | None = None
    timeout: int | None = None
    cache: bool = True


class QueryResponse(BaseModel):
    """Response model for query endpoint."""

    messages: list[dict[str, Any]]
    provider: str
    model: str | None = None
    error: str | None = None


class ProviderInfo(BaseModel):
    """Provider information model."""

    name: str
    enabled: bool
    default_model: str | None = None


# Create FastMCP server
mcp = FastMCP("Claif MCP Server")


@mcp.tool()
async def claif_query(request: QueryRequest) -> QueryResponse:
    """Query a specific LLM provider through Claif.

    Args:
        request: Query request with prompt and options

    Returns:
        Response with messages from the provider
    """
    try:
        # Parse provider
        provider_enum = None
        if request.provider:
            try:
                provider_enum = Provider(request.provider.lower())
            except ValueError:
                return QueryResponse(
                    messages=[],
                    provider=request.provider or "unknown",
                    error=f"Unknown provider: {request.provider}",
                )

        # Create options
        options = ClaifOptions(
            provider=provider_enum,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt,
            timeout=request.timeout,
            cache=request.cache,
        )

        # Execute query
        messages = []
        async for message in query(request.prompt, options):
            messages.append(
                {
                    "role": message.role.value,
                    "content": message.content if isinstance(message.content, str) else str(message.content),
                }
            )

        return QueryResponse(
            messages=messages,
            provider=provider_enum.value if provider_enum else "default",
            model=request.model,
        )

    except Exception as e:
        logger.error(f"Query error: {e}")
        return QueryResponse(
            messages=[],
            provider=request.provider or "unknown",
            error=str(e),
        )


@mcp.tool()
async def claif_query_random(request: QueryRequest) -> QueryResponse:
    """Query a random LLM provider through Claif.

    Args:
        request: Query request with prompt and options

    Returns:
        Response with messages from a randomly selected provider
    """
    try:
        # Create options (without provider)
        options = ClaifOptions(
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt,
            timeout=request.timeout,
            cache=request.cache,
        )

        # Track selected provider
        selected_provider = None

        # Execute random query
        messages = []
        async for message in query_random(request.prompt, options):
            messages.append(
                {
                    "role": message.role.value,
                    "content": message.content if isinstance(message.content, str) else str(message.content),
                }
            )
            # Get the selected provider from options
            if options.provider and not selected_provider:
                selected_provider = options.provider.value

        return QueryResponse(
            messages=messages,
            provider=selected_provider or "unknown",
            model=request.model,
        )

    except Exception as e:
        logger.error(f"Random query error: {e}")
        return QueryResponse(
            messages=[],
            provider="unknown",
            error=str(e),
        )


@mcp.tool()
async def claif_query_all(request: QueryRequest) -> dict[str, QueryResponse]:
    """Query all LLM providers in parallel through Claif.

    Args:
        request: Query request with prompt and options

    Returns:
        Dictionary mapping provider names to their responses
    """
    try:
        # Create options
        options = ClaifOptions(
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt,
            timeout=request.timeout,
            cache=request.cache,
        )

        # Execute parallel query
        results = {}
        async for provider_results in query_all(request.prompt, options):
            for provider, messages in provider_results.items():
                message_dicts = []
                for message in messages:
                    message_dicts.append(
                        {
                            "role": message.role.value,
                            "content": message.content if isinstance(message.content, str) else str(message.content),
                        }
                    )

                results[provider.value] = QueryResponse(
                    messages=message_dicts,
                    provider=provider.value,
                    model=request.model,
                )

        return results

    except Exception as e:
        logger.error(f"Parallel query error: {e}")
        return {
            "error": QueryResponse(
                messages=[],
                provider="all",
                error=str(e),
            )
        }


@mcp.tool()
async def claif_list_providers() -> list[ProviderInfo]:
    """List all available LLM providers in Claif.

    Returns:
        List of provider information
    """
    providers = []

    for provider in Provider:
        # Get provider config from global config if available
        providers.append(
            ProviderInfo(
                name=provider.value,
                enabled=True,  # All providers are enabled by default
                default_model=None,  # Could be enhanced with config lookup
            )
        )

    return providers


@mcp.tool()
async def claif_health_check(provider: str | None = None) -> dict[str, bool]:
    """Check health of Claif providers.

    Args:
        provider: Specific provider to check, or None for all

    Returns:
        Dictionary mapping provider names to health status
    """

    async def check_provider(prov: Provider) -> tuple[str, bool]:
        try:
            options = ClaifOptions(
                provider=prov,
                max_tokens=10,
                timeout=5,
            )
            message_count = 0
            async for _ in query("Hello", options):
                message_count += 1
                if message_count > 0:
                    break
            return prov.value, message_count > 0
        except Exception:
            return prov.value, False

    if provider:
        try:
            provider_enum = Provider(provider.lower())
            name, healthy = await check_provider(provider_enum)
            return {name: healthy}
        except ValueError:
            return {provider: False}
    else:
        # Check all providers
        tasks = [check_provider(p) for p in Provider]
        results = await asyncio.gather(*tasks)
        return dict(results)


def start_mcp_server(
    host: str = "localhost",
    port: int = 8000,
    reload: bool = False,
    config: Config | None = None,
) -> None:
    """Start the FastMCP server.

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload
        config:Claif configuration
    """
    # Store config globally if provided
    if config:
        # Could be used to enhance provider info
        logger.info(f"Using config with default provider: {config.default_provider}")

    # Run the server
    import uvicorn

    uvicorn.run(
        mcp,
        host=host,
        port=port,
        reload=reload,
        log_level="info" if logger.level <= 20 else "warning",
    )


def main():
    """Main entry point for the MCP server."""
    import fire

    fire.Fire(start_mcp_server)
