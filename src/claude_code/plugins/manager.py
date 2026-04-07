"""Plugin manager for plugin lifecycle, errors, and built-in plugin registry.

Provides:
- PluginError: Discriminated union of all plugin error types
- PluginLoadResult: Result of loading plugins
- BuiltinPluginDefinition: Definition for built-in plugins
- BuiltinPluginRegistry: Registry for built-in plugins
- Manifest parsing and validation helpers

TypeScript equivalent: src/types/plugin.ts, src/plugins/builtinPlugins.ts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    pass


# =============================================================================
# Constants
# =============================================================================

BUILTIN_MARKETPLACE_NAME = "builtin"


# =============================================================================
# Plugin Component
# =============================================================================


class PluginComponent:
    """Plugin component types that can fail to load."""

    COMMANDS = "commands"
    AGENTS = "agents"
    SKILLS = "skills"
    HOOKS = "hooks"
    OUTPUT_STYLES = "output-styles"


# =============================================================================
# Plugin Error Types (Discriminated Union via TypedDict)
# =============================================================================


class PluginErrorPathNotFound(TypedDict):
    """Path not found error."""

    type: str
    source: str
    plugin: str | None
    path: str
    component: str


class PluginErrorGitAuthFailed(TypedDict):
    """Git authentication failed error."""

    type: str
    source: str
    plugin: str | None
    git_url: str
    auth_type: str  # 'ssh' | 'https'


class PluginErrorGitTimeout(TypedDict):
    """Git operation timeout error."""

    type: str
    source: str
    plugin: str | None
    git_url: str
    operation: str  # 'clone' | 'pull'


class PluginErrorNetworkError(TypedDict):
    """Network error."""

    type: str
    source: str
    plugin: str | None
    url: str
    details: str | None


class PluginErrorManifestParseError(TypedDict):
    """Manifest parse error."""

    type: str
    source: str
    plugin: str | None
    manifest_path: str
    parse_error: str


class PluginErrorManifestValidationError(TypedDict):
    """Manifest validation error."""

    type: str
    source: str
    plugin: str | None
    manifest_path: str
    validation_errors: list[str]


class PluginErrorPluginNotFound(TypedDict):
    """Plugin not found in marketplace."""

    type: str
    source: str
    plugin: str | None
    plugin_id: str
    marketplace: str


class PluginErrorMarketplaceNotFound(TypedDict):
    """Marketplace not found."""

    type: str
    source: str
    plugin: str | None
    marketplace: str
    available_marketplaces: list[str]


class PluginErrorMarketplaceLoadFailed(TypedDict):
    """Marketplace load failed."""

    type: str
    source: str
    plugin: str | None
    marketplace: str
    reason: str


class PluginErrorMcpConfigInvalid(TypedDict):
    """MCP server configuration invalid."""

    type: str
    source: str
    plugin: str
    server_name: str
    validation_error: str


class PluginErrorMcpServerSuppressedDuplicate(TypedDict):
    """MCP server duplicate suppressed."""

    type: str
    source: str
    plugin: str
    server_name: str
    duplicate_of: str


class PluginErrorLspConfigInvalid(TypedDict):
    """LSP server configuration invalid."""

    type: str
    source: str
    plugin: str
    server_name: str
    validation_error: str


class PluginErrorLspServerStartFailed(TypedDict):
    """LSP server failed to start."""

    type: str
    source: str
    plugin: str
    server_name: str
    reason: str


class PluginErrorLspServerCrashed(TypedDict):
    """LSP server crashed."""

    type: str
    source: str
    plugin: str
    server_name: str
    exit_code: int | None
    signal: str | None


class PluginErrorLspRequestTimeout(TypedDict):
    """LSP request timed out."""

    type: str
    source: str
    plugin: str
    server_name: str
    method: str
    timeout_ms: int


class PluginErrorLspRequestFailed(TypedDict):
    """LSP request failed."""

    type: str
    source: str
    plugin: str
    server_name: str
    method: str
    error: str


class PluginErrorHookLoadFailed(TypedDict):
    """Hook load failed."""

    type: str
    source: str
    plugin: str
    hook_path: str
    reason: str


class PluginErrorComponentLoadFailed(TypedDict):
    """Component load failed."""

    type: str
    source: str
    plugin: str
    component: str
    path: str
    reason: str


class PluginErrorMcpbDownloadFailed(TypedDict):
    """MCPB download failed."""

    type: str
    source: str
    plugin: str
    url: str
    reason: str


class PluginErrorMcpbExtractFailed(TypedDict):
    """MCPB extract failed."""

    type: str
    source: str
    plugin: str
    mcpb_path: str
    reason: str


class PluginErrorMcpbInvalidManifest(TypedDict):
    """MCPB invalid manifest."""

    type: str
    source: str
    plugin: str
    mcpb_path: str
    validation_error: str


class PluginErrorMarketplaceBlockedByPolicy(TypedDict):
    """Marketplace blocked by enterprise policy."""

    type: str
    source: str
    plugin: str | None
    marketplace: str
    blocked_by_blocklist: bool | None
    allowed_sources: list[str]


class PluginErrorDependencyUnsatisfied(TypedDict):
    """Dependency not satisfied."""

    type: str
    source: str
    plugin: str
    dependency: str
    reason: str  # 'not-enabled' | 'not-found'


class PluginErrorPluginCacheMiss(TypedDict):
    """Plugin not cached."""

    type: str
    source: str
    plugin: str
    install_path: str


class PluginErrorGeneric(TypedDict):
    """Generic plugin error."""

    type: str
    source: str
    plugin: str | None
    error: str


# Union type alias for all plugin errors
PluginError = (
    PluginErrorPathNotFound
    | PluginErrorGitAuthFailed
    | PluginErrorGitTimeout
    | PluginErrorNetworkError
    | PluginErrorManifestParseError
    | PluginErrorManifestValidationError
    | PluginErrorPluginNotFound
    | PluginErrorMarketplaceNotFound
    | PluginErrorMarketplaceLoadFailed
    | PluginErrorMcpConfigInvalid
    | PluginErrorMcpServerSuppressedDuplicate
    | PluginErrorLspConfigInvalid
    | PluginErrorLspServerStartFailed
    | PluginErrorLspServerCrashed
    | PluginErrorLspRequestTimeout
    | PluginErrorLspRequestFailed
    | PluginErrorHookLoadFailed
    | PluginErrorComponentLoadFailed
    | PluginErrorMcpbDownloadFailed
    | PluginErrorMcpbExtractFailed
    | PluginErrorMcpbInvalidManifest
    | PluginErrorMarketplaceBlockedByPolicy
    | PluginErrorDependencyUnsatisfied
    | PluginErrorPluginCacheMiss
    | PluginErrorGeneric
)


def get_plugin_error_message(error: PluginError) -> str:
    """Get a display message from any PluginError.

    Args:
        error: The plugin error.

    Returns:
        Human-readable error message.
    """
    etype = error["type"]

    if etype == "generic-error":
        return error["error"]
    if etype == "path-not-found":
        return f"Path not found: {error['path']} ({error['component']})"
    if etype == "git-auth-failed":
        return f"Git authentication failed ({error['auth_type']}): {error['git_url']}"
    if etype == "git-timeout":
        return f"Git {error['operation']} timeout: {error['git_url']}"
    if etype == "network-error":
        details = f" - {error['details']}" if error.get("details") else ""
        return f"Network error: {error['url']}{details}"
    if etype == "manifest-parse-error":
        return f"Manifest parse error: {error['parse_error']}"
    if etype == "manifest-validation-error":
        return f"Manifest validation failed: {', '.join(error['validation_errors'])}"
    if etype == "plugin-not-found":
        return f"Plugin {error['plugin_id']} not found in marketplace {error['marketplace']}"
    if etype == "marketplace-not-found":
        return f"Marketplace {error['marketplace']} not found"
    if etype == "marketplace-load-failed":
        return f"Marketplace {error['marketplace']} failed to load: {error['reason']}"
    if etype == "mcp-config-invalid":
        return f"MCP server {error['server_name']} invalid: {error['validation_error']}"
    if etype == "mcp-server-suppressed-duplicate":
        dup = error["duplicate_of"]
        if dup.startswith("plugin:"):
            parts = dup.split(":", 1)
            dup = f'server provided by plugin "{parts[1] if len(parts) > 1 else "?"}"'
        else:
            dup = f'already-configured "{dup}"'
        return f'MCP server "{error["server_name"]}" skipped — same command/URL as {dup}'
    if etype == "hook-load-failed":
        return f"Hook load failed: {error['reason']}"
    if etype == "component-load-failed":
        return f"{error['component']} load failed from {error['path']}: {error['reason']}"
    if etype == "mcpb-download-failed":
        return f"Failed to download MCPB from {error['url']}: {error['reason']}"
    if etype == "mcpb-extract-failed":
        return f"Failed to extract MCPB {error['mcpb_path']}: {error['reason']}"
    if etype == "mcpb-invalid-manifest":
        return f"MCPB manifest invalid at {error['mcpb_path']}: {error['validation_error']}"
    if etype == "lsp-config-invalid":
        return f'Plugin "{error["plugin"]}" has invalid LSP server config for "{error["server_name"]}": {error["validation_error"]}'
    if etype == "lsp-server-start-failed":
        return f'Plugin "{error["plugin"]}" failed to start LSP server "{error["server_name"]}": {error["reason"]}'
    if etype == "lsp-server-crashed":
        sig = error.get("signal")
        if sig:
            return f'Plugin "{error["plugin"]}" LSP server "{error["server_name"]}" crashed with signal {sig}'
        code = error.get("exit_code")
        return f'Plugin "{error["plugin"]}" LSP server "{error["server_name"]}" crashed with exit code {code if code is not None else "unknown"}'
    if etype == "lsp-request-timeout":
        return f'Plugin "{error["plugin"]}" LSP server "{error["server_name"]}" timed out on {error["method"]} request after {error["timeout_ms"]}ms'
    if etype == "lsp-request-failed":
        return f'Plugin "{error["plugin"]}" LSP server "{error["server_name"]}" {error["method"]} request failed: {error["error"]}'
    if etype == "marketplace-blocked-by-policy":
        if error.get("blocked_by_blocklist"):
            return f"Marketplace '{error['marketplace']}' is blocked by enterprise policy"
        return f"Marketplace '{error['marketplace']}' is not in the allowed marketplace list"
    if etype == "dependency-unsatisfied":
        if error["reason"] == "not-enabled":
            hint = "disabled — enable it or remove the dependency"
        else:
            hint = "not found in any configured marketplace"
        return f'Dependency "{error["dependency"]}" is {hint}'
    if etype == "plugin-cache-miss":
        return f'Plugin "{error["plugin"]}" not cached at {error["install_path"]} — run /plugins to refresh'

    # Fallback for unknown error types
    return f"Plugin error [{etype}]: {error['source']}"


# =============================================================================
# Plugin Repository
# =============================================================================


@dataclass
class PluginRepository:
    """Repository metadata for a plugin source."""

    url: str
    branch: str
    last_updated: str | None = None
    commit_sha: str | None = None


# =============================================================================
# Plugin Config
# =============================================================================


@dataclass
class PluginConfig:
    """Plugin configuration containing marketplace sources."""

    repositories: dict[str, PluginRepository] = field(default_factory=dict)


# =============================================================================
# Plugin Load Result
# =============================================================================


@dataclass
class PluginLoadResult:
    """Result of loading plugins from all sources.

    Attributes:
        enabled: Plugins that are currently enabled.
        disabled: Plugins that are registered but disabled.
        errors: Errors encountered during plugin loading.
    """

    enabled: list[Any] = field(default_factory=list)  # list[LoadedPlugin]
    disabled: list[Any] = field(default_factory=list)  # list[LoadedPlugin]
    errors: list[PluginError] = field(default_factory=list)


# =============================================================================
# Builtin Plugin Definition
# =============================================================================


@dataclass
class BuiltinPluginDefinition:
    """Definition for a built-in plugin that ships with the CLI.

    Built-in plugins appear in the /plugin UI and can be enabled/disabled
    by users (persisted to user settings).

    Attributes:
        name: Plugin name (used in `{name}@builtin` identifier).
        description: Description shown in the /plugin UI.
        version: Optional version string.
        skills: Skills provided by this plugin.
        hooks: Hooks provided by this plugin.
        mcp_servers: MCP servers provided by this plugin.
        is_available: Whether this plugin is available (e.g. based on system
            capabilities). Unavailable plugins are hidden entirely.
        default_enabled: Default enabled state before the user sets a preference.
    """

    name: str
    description: str = ""
    version: str | None = None
    skills: list[Any] | None = None  # list[BundledSkillDefinition]
    hooks: dict[str, Any] | None = None  # HooksSettings
    mcp_servers: dict[str, Any] | None = None  # dict[str, McpServerConfig]
    is_available: Any = None  # Callable[[], bool] | None
    default_enabled: bool = True


# =============================================================================
# Builtin Plugin Registry
# =============================================================================

# Builtin plugins registry — module-level storage
_BUILTIN_PLUGINS: dict[str, BuiltinPluginDefinition] = {}


def register_builtin_plugin(definition: BuiltinPluginDefinition) -> None:
    """Register a built-in plugin.

    Args:
        definition: The built-in plugin definition.
    """
    _BUILTIN_PLUGINS[definition.name] = definition


def is_builtin_plugin_id(plugin_id: str) -> bool:
    """Check if a plugin ID represents a built-in plugin (ends with @builtin).

    Args:
        plugin_id: The plugin identifier.

    Returns:
        True if the plugin is built-in.
    """
    return plugin_id.endswith(f"@{BUILTIN_MARKETPLACE_NAME}")


def get_builtin_plugin_definition(name: str) -> BuiltinPluginDefinition | None:
    """Get a specific built-in plugin definition by name.

    Args:
        name: The plugin name.

    Returns:
        The plugin definition, or None if not found.
    """
    return _BUILTIN_PLUGINS.get(name)


def get_builtin_plugins() -> tuple[list[Any], list[Any]]:
    """Get all registered built-in plugins split into enabled/disabled.

    Built-in plugins whose is_available() returns false are omitted entirely.

    Returns:
        Tuple of (enabled, disabled) lists of LoadedPlugin objects.
    """
    # Import here to avoid circular imports
    from .base import LoadedPlugin, PluginManifest

    enabled: list[Any] = []
    disabled: list[Any] = []

    for name, definition in _BUILTIN_PLUGINS.items():
        # Check availability
        if definition.is_available is not None:
            try:
                if not definition.is_available():
                    continue
            except Exception:
                continue

        plugin_id = f"{name}@{BUILTIN_MARKETPLACE_NAME}"

        # Determine enabled state — user settings would override default_enabled
        is_enabled = definition.default_enabled

        manifest = PluginManifest(
            name=name,
            description=definition.description,
            version=definition.version or "1.0.0",
        )

        plugin: LoadedPlugin = LoadedPlugin(
            name=name,
            manifest=manifest,
            path=BUILTIN_MARKETPLACE_NAME,  # sentinel — no filesystem path
            source=plugin_id,
            repository=plugin_id,
            enabled=is_enabled,
            is_builtin=True,
            hooks_config=definition.hooks,
            mcp_servers=definition.mcp_servers,
        )

        if is_enabled:
            enabled.append(plugin)
        else:
            disabled.append(plugin)

    return enabled, disabled


def builtin_plugins_count() -> int:
    """Return the number of registered built-in plugins."""
    return len(_BUILTIN_PLUGINS)


def _clear_builtin_plugins() -> None:
    """Clear all built-in plugins. For testing only."""
    _BUILTIN_PLUGINS.clear()
