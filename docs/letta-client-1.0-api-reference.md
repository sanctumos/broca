# letta-client 1.0+ Complete API Reference

**Version:** 1.7.0

> Complete reference documentation for all endpoints, methods, and resources in letta-client 1.0+

## Table of Contents

- [Installation](#installation)
- [Client Initialization](#client-initialization)
- [Resources](#resources)
  - [Agents](#agents)
  - [Blocks](#blocks)
  - [Identities](#identities)
- [Exception Classes](#exception-classes)

## Installation

```bash
pip install letta-client
```

## Client Initialization

```python
from letta_client import Letta

client = Letta(
    api_key='your-api-key',
    base_url='https://api.letta.ai'  # or your self-hosted URL
)
```

### Constructor Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | str | None | No | None | |
| `project_id` | str | None | No | None | |
| `project` | str | None | No | None | |
| `environment` | Literal['cloud', 'local'] | NotGiven | No | NOT_GIVEN | |
| `base_url` | str | httpx.URL | None | NotGiven | No | NOT_GIVEN | |
| `timeout` | float | Timeout | None | NotGiven | No | NOT_GIVEN | |
| `max_retries` | int | No | 2 | |
| `default_headers` | Mapping[str, str] | None | No | None | |
| `default_query` | Mapping[str, object] | None | No | None | |
| `http_client` | httpx.Client | None | No | None | |
| `_strict_response_validation` | bool | No | False | |

### Breaking Changes from v0.x

- **`token` → `api_key`**: The `token` parameter has been renamed to `api_key`
- **Constructor changes**: The constructor signature has changed significantly
- **Method signatures**: Some method signatures may have changed

---

## Resources

### Agents

Access via `client.agents`

#### create()

Create an agent.

Args:
  agent_type: The type of agent.

  base_template_id: Deprecated: No longer used. The base template id of the agent.

  block_ids: The ids of the blocks used by the agent.

  compaction_settings: Configuration for conversation compaction / summarization.

      `model` is the only required user-facing field – it specifies the summarizer
      model handle (e.g. `"openai/gpt-4o-mini"`). Per-model settings (temperature, max
      tokens, etc.) are derived from the default configuration for that handle.

  context_window_limit: The context window limit used by the agent.

  description: The description of the agent.

  embedding: The embedding model handle used by the agent (format: provider/model-name).

  embedding_chunk_size: Deprecated: No longer used. The embedding chunk size used by the agent.

  embedding_config: Configuration for embedding model connection and processing parameters.

  enable_reasoner: Deprecated: Use `model` field to configure reasoning instead. Whether to enable
      internal extended thinking step for a reasoner model.

  enable_sleeptime: If set to True, memory management will move to a background agent thread.

  folder_ids: The ids of the folders used by the agent.

  from_template: Deprecated: please use the 'create agents from a template' endpoint instead.

  hidden: Deprecated: No longer used. If set to True, the agent will be hidden.

  identity_ids: The ids of the identities associated with this agent.

  include_base_tool_rules: If true, attaches the Letta base tool rules (e.g. deny all tools not explicitly
      allowed).

  include_base_tools: If true, attaches the Letta core tools (e.g. core_memory related functions).

  include_default_source: If true, automatically creates and attaches a default data source for this
      agent.

  include_multi_agent_tools: If true, attaches the Letta multi-agent tools (e.g. sending a message to another
      agent).

  initial_message_sequence: The initial set of messages to put in the agent's in-context memory.

  llm_config: Configuration for Language Model (LLM) connection and generation parameters.

      .. deprecated:: LLMConfig is deprecated and should not be used as an input or
      return type in API calls. Use the schemas in letta.schemas.model (ModelSettings,
      OpenAIModelSettings, etc.) instead. For conversion, use the \__to_model() method
      or Model.\__from_llm_config() method.

  max_files_open: Maximum number of files that can be open at once for this agent. Setting this
      too high may exceed the context window, which will break the agent.

  max_reasoning_tokens: Deprecated: Use `model` field to configure reasoning tokens instead. The maximum
      number of tokens to generate for reasoning step.

  max_tokens: Deprecated: Use `model` field to configure max output tokens instead. The
      maximum number of tokens to generate, including reasoning step.

  memory_blocks: The blocks to create in the agent's in-context memory.

  memory_variables: Deprecated: Only relevant for creating agents from a template. Use the 'create
      agents from a template' endpoint instead.

  message_buffer_autoclear: If set to True, the agent will not remember previous messages (though the agent
      will still retain state via core memory blocks and archival/recall memory). Not
      recommended unless you have an advanced use case.

  metadata: The metadata of the agent.

  model: The model handle for the agent to use (format: provider/model-name).

  model_settings: The model settings for the agent.

  name: The name of the agent.

  parallel_tool_calls: Deprecated: Use `model_settings` to configure parallel tool calls instead. If
      set to True, enables parallel tool calling.

  per_file_view_window_char_limit: The per-file view window character limit for this agent. Setting this too high
      may exceed the context window, which will break the agent.

  project: Deprecated: Project should now be passed via the X-Project header instead of in
      the request body. If using the SDK, this can be done via the x_project
      parameter.

  project_id: Deprecated: No longer used. The id of the project the agent belongs to.

  reasoning: Deprecated: Use `model` field to configure reasoning instead. Whether to enable
      reasoning for this agent.

  response_format: Deprecated: Use `model_settings` field to configure response format instead. The
      response format for the agent.

  secrets: The environment variables for tool execution specific to this agent.

  source_ids: Deprecated: Use `folder_ids` field instead. The ids of the sources used by the
      agent.

  system: The system prompt used by the agent.

  tags: The tags associated with the agent.

  template: Deprecated: No longer used.

  template_id: Deprecated: No longer used. The id of the template the agent belongs to.

  timezone: The timezone of the agent (IANA format).

  tool_exec_environment_variables: Deprecated: Use `secrets` field instead. Environment variables for tool
      execution.

  tool_ids: The ids of the tools used by the agent.

  tool_rules: The tool rules governing the agent.

  tools: The tools used by the agent.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
create(
    agent_type: AgentType | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    compaction_settings: Optional[agent_create_params.CompactionSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    context_window_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    embedding_chunk_size: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    enable_reasoner: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    enable_sleeptime: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    folder_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    from_template: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    identity_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    include_base_tool_rules: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    include_base_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    include_default_source: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    include_multi_agent_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    initial_message_sequence: Optional[Iterable[MessageCreateParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    llm_config: Optional[LlmConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    max_files_open: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    max_reasoning_tokens: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    max_tokens: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    memory_blocks: Optional[Iterable[CreateBlockParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    memory_variables: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    message_buffer_autoclear: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    model: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    model_settings: Optional[agent_create_params.ModelSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    parallel_tool_calls: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    per_file_view_window_char_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    reasoning: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    response_format: Optional[agent_create_params.ResponseFormat] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    secrets: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    source_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    system: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    template: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    timezone: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tool_exec_environment_variables: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tool_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tool_rules: Optional[Iterable[agent_create_params.ToolRule]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tools: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> AgentState
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `agent_type` | AgentType | Omit | No | <letta_client.Omit object at 0x000002... |
| `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `compaction_settings` | Optional[agent_create_params.CompactionSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
| `context_window_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `embedding_chunk_size` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
| `enable_reasoner` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `enable_sleeptime` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `folder_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `from_template` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `identity_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `include_base_tool_rules` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `include_base_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `include_default_source` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `include_multi_agent_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `initial_message_sequence` | Optional[Iterable[MessageCreateParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `llm_config` | Optional[LlmConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
| `max_files_open` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `max_reasoning_tokens` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `max_tokens` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `memory_blocks` | Optional[Iterable[CreateBlockParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `memory_variables` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `message_buffer_autoclear` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `model` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `model_settings` | Optional[agent_create_params.ModelSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
| `parallel_tool_calls` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `per_file_view_window_char_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `reasoning` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `response_format` | Optional[agent_create_params.ResponseFormat] | Omit | No | <letta_client.Omit object at 0x000002... |
| `secrets` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `source_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `system` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `template` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `timezone` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tool_exec_environment_variables` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tool_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tool_rules` | Optional[Iterable[agent_create_params.ToolRule]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tools` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### delete()

Delete an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
delete(
    agent_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> object
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `agent_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### export_file()

Export the serialized JSON representation of an agent, formatted with
indentation.

Args:
  use_legacy_format: If True, exports using the legacy single-agent 'v1' format with inline
      tools/blocks. If False, exports using the new multi-entity 'v2' format, with
      separate agents, tools, blocks, files, etc.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
export_file(
    agent_id: str  # required,
    max_steps: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    use_legacy_format: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> str
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `agent_id` | str | Yes | - |
| `max_steps` | int | Omit | No | <letta_client.Omit object at 0x000002... |
| `use_legacy_format` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### import_file()

Import a serialized agent file and recreate the agent(s) in the system.

Returns
the IDs of all imported agents.

Args:
  append_copy_suffix: If set to True, appends "\__copy" to the end of the agent name.

  embedding: Embedding handle to override with.

  env_vars_json: Environment variables as a JSON string to pass to the agent for tool execution.
      Use 'secrets' instead.

  name: If provided, overrides the agent name with this value.

  override_embedding_handle: Override import with specific embedding handle. Use 'embedding' instead.

  override_existing_tools: If set to True, existing tools can get their source code overwritten by the
      uploaded tool definitions. Note that Letta core tools can never be updated
      externally.

  override_name: If provided, overrides the agent name with this value. Use 'name' instead.

  project_id: The project ID to associate the uploaded agent with. This is now passed via
      headers.

  secrets: Secrets as a JSON string to pass to the agent for tool execution.

  strip_messages: If set to True, strips all messages from the agent before importing.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
import_file(
    file: FileTypes  # required,
    append_copy_suffix: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    env_vars_json: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    override_embedding_handle: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    override_existing_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    override_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    secrets: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    strip_messages: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    x_override_embedding_model: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> AgentImportFileResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `file` | FileTypes | Yes | - |
| `append_copy_suffix` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `env_vars_json` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `override_embedding_handle` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `override_existing_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `override_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `secrets` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `strip_messages` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `x_override_embedding_model` | str | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### list()

Get a list of all agents.

Args:
  after: Cursor for pagination

  ascending: Whether to sort agents oldest to newest (True) or newest to oldest (False,
      default)

  base_template_id: Search agents by base template ID

  before: Cursor for pagination

  identifier_keys: Search agents by identifier keys

  identity_id: Search agents by identity ID

  include: Specify which relational fields to include in the response. No relationships are
      included by default.

  include_relationships: Specify which relational fields (e.g., 'tools', 'sources', 'memory') to include
      in the response. If not provided, all relationships are loaded by default. Using
      this can optimize performance by reducing unnecessary joins.This is a legacy
      parameter, and no longer supported after 1.0.0 SDK versions.

  last_stop_reason: Filter agents by their last stop reason.

  limit: Limit for pagination

  match_all_tags: If True, only returns agents that match ALL given tags. Otherwise, return agents
      that have ANY of the passed-in tags.

  name: Name of the agent

  order: Sort order for agents by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  project_id: Search agents by project ID - this will default to your default project on cloud

  query_text: Search agents by name

  sort_by: Field to sort by. Options: 'created_at' (default), 'last_run_completion'

  tags: List of tags to filter agents by

  template_id: Search agents by template ID

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    ascending: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    identifier_keys: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    identity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    include: List[Literal['agent.blocks', 'agent.identities', 'agent.managed_group', 'agent.pending_approval', 'agent.secrets', 'agent.sources', 'agent.tags', 'agent.tools']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    include_relationships: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    last_stop_reason: Optional[StopReasonType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    match_all_tags: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order_by: Literal['created_at', 'last_run_completion'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    query_text: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    sort_by: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> SyncArrayPage[AgentState]
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `ascending` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `identifier_keys` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `identity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `include` | List[Literal['agent.blocks', 'agent.identities', 'agent.m... | No | <letta_client.Omit object at 0x000002... |
| `include_relationships` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `last_stop_reason` | Optional[StopReasonType] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `match_all_tags` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order_by` | Literal['created_at', 'last_run_completion'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `query_text` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `sort_by` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### retrieve()

Get the state of the agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  include: Specify which relational fields to include in the response. No relationships are
      included by default.

  include_relationships: Specify which relational fields (e.g., 'tools', 'sources', 'memory') to include
      in the response. If not provided, all relationships are loaded by default. Using
      this can optimize performance by reducing unnecessary joins.This is a legacy
      parameter, and no longer supported after 1.0.0 SDK versions.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
retrieve(
    agent_id: str  # required,
    include: List[Literal['agent.blocks', 'agent.identities', 'agent.managed_group', 'agent.pending_approval', 'agent.secrets', 'agent.sources', 'agent.tags', 'agent.tools']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    include_relationships: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> AgentState
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `agent_id` | str | Yes | - |
| `include` | List[Literal['agent.blocks', 'agent.identities', 'agent.m... | No | <letta_client.Omit object at 0x000002... |
| `include_relationships` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### update()

Update an existing agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  base_template_id: The base template id of the agent.

  block_ids: The ids of the blocks used by the agent.

  compaction_settings: Configuration for conversation compaction / summarization.

      `model` is the only required user-facing field – it specifies the summarizer
      model handle (e.g. `"openai/gpt-4o-mini"`). Per-model settings (temperature, max
      tokens, etc.) are derived from the default configuration for that handle.

  context_window_limit: The context window limit used by the agent.

  description: The description of the agent.

  embedding: The embedding model handle used by the agent (format: provider/model-name).

  embedding_config: Configuration for embedding model connection and processing parameters.

  enable_sleeptime: If set to True, memory management will move to a background agent thread.

  folder_ids: The ids of the folders used by the agent.

  hidden: If set to True, the agent will be hidden.

  identity_ids: The ids of the identities associated with this agent.

  last_run_completion: The timestamp when the agent last completed a run.

  last_run_duration_ms: The duration in milliseconds of the agent's last run.

  last_stop_reason: The stop reason from the agent's last run.

  llm_config: Configuration for Language Model (LLM) connection and generation parameters.

      .. deprecated:: LLMConfig is deprecated and should not be used as an input or
      return type in API calls. Use the schemas in letta.schemas.model (ModelSettings,
      OpenAIModelSettings, etc.) instead. For conversion, use the \__to_model() method
      or Model.\__from_llm_config() method.

  max_files_open: Maximum number of files that can be open at once for this agent. Setting this
      too high may exceed the context window, which will break the agent.

  max_tokens: Deprecated: Use `model` field to configure max output tokens instead. The
      maximum number of tokens to generate, including reasoning step.

  message_buffer_autoclear: If set to True, the agent will not remember previous messages (though the agent
      will still retain state via core memory blocks and archival/recall memory). Not
      recommended unless you have an advanced use case.

  message_ids: The ids of the messages in the agent's in-context memory.

  metadata: The metadata of the agent.

  model: The model handle used by the agent (format: provider/model-name).

  model_settings: The model settings for the agent.

  name: The name of the agent.

  parallel_tool_calls: Deprecated: Use `model_settings` to configure parallel tool calls instead. If
      set to True, enables parallel tool calling.

  per_file_view_window_char_limit: The per-file view window character limit for this agent. Setting this too high
      may exceed the context window, which will break the agent.

  project_id: The id of the project the agent belongs to.

  reasoning: Deprecated: Use `model` field to configure reasoning instead. Whether to enable
      reasoning for this agent.

  response_format: Deprecated: Use `model_settings` field to configure response format instead. The
      response format for the agent.

  secrets: The environment variables for tool execution specific to this agent.

  source_ids: Deprecated: Use `folder_ids` field instead. The ids of the sources used by the
      agent.

  system: The system prompt used by the agent.

  tags: The tags associated with the agent.

  template_id: The id of the template the agent belongs to.

  timezone: The timezone of the agent (IANA format).

  tool_exec_environment_variables: Deprecated: use `secrets` field instead

  tool_ids: The ids of the tools used by the agent.

  tool_rules: The tool rules governing the agent.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
update(
    agent_id: str  # required,
    base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    compaction_settings: Optional[agent_update_params.CompactionSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    context_window_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    enable_sleeptime: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    folder_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    identity_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    last_run_completion: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    last_run_duration_ms: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    last_stop_reason: Optional[StopReasonType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    llm_config: Optional[LlmConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    max_files_open: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    max_tokens: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    message_buffer_autoclear: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    message_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    model: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    model_settings: Optional[agent_update_params.ModelSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    parallel_tool_calls: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    per_file_view_window_char_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    reasoning: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    response_format: Optional[agent_update_params.ResponseFormat] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    secrets: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    source_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    system: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    timezone: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tool_exec_environment_variables: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tool_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tool_rules: Optional[Iterable[agent_update_params.ToolRule]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> AgentState
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `agent_id` | str | Yes | - |
| `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `compaction_settings` | Optional[agent_update_params.CompactionSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
| `context_window_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
| `enable_sleeptime` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `folder_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `identity_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `last_run_completion` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
| `last_run_duration_ms` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `last_stop_reason` | Optional[StopReasonType] | Omit | No | <letta_client.Omit object at 0x000002... |
| `llm_config` | Optional[LlmConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
| `max_files_open` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `max_tokens` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `message_buffer_autoclear` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `message_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `model` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `model_settings` | Optional[agent_update_params.ModelSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `parallel_tool_calls` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `per_file_view_window_char_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `reasoning` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `response_format` | Optional[agent_update_params.ResponseFormat] | Omit | No | <letta_client.Omit object at 0x000002... |
| `secrets` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `source_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `system` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `timezone` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tool_exec_environment_variables` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tool_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tool_rules` | Optional[Iterable[agent_update_params.ToolRule]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### archives

Sub-resource: `client.agents.archives`

  #### attach()

  Attach an archive to an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  attach(
      archive_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `archive_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### detach()

  Detach an archive from an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  detach(
      archive_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `archive_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### blocks

Sub-resource: `client.agents.blocks`

  #### attach()

  Attach a core memory block to an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  block_id: The ID of the block in the format 'block-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  attach(
      block_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AgentState
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `block_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### detach()

  Detach a core memory block from an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  block_id: The ID of the block in the format 'block-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  detach(
      block_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AgentState
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `block_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Retrieve the core memory blocks of a specific agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  after: Block ID cursor for pagination. Returns blocks that come after this block ID in
      the specified sort order

  before: Block ID cursor for pagination. Returns blocks that come before this block ID in
      the specified sort order

  limit: Maximum number of blocks to return

  order: Sort order for blocks by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      agent_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[BlockResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve a core memory block from an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      block_label: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> BlockResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `block_label` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Updates a core memory block of an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  base_template_id: The base template id of the block.

  deployment_id: The id of the deployment.

  description: Description of the block.

  entity_id: The id of the entity within the template.

  hidden: If set to True, the block will be hidden.

  is_template: Whether the block is a template (e.g. saved human/persona options).

  label: Label of the block (e.g. 'human', 'persona') in the context window.

  limit: Character limit of the block.

  metadata: Metadata of the block.

  preserve_on_migration: Preserve the block on template migration.

  project_id: The associated project id.

  read_only: Whether the agent has read-only access to the block.

  tags: The tags to associate with the block.

  template_id: The id of the template.

  template_name: Name of the block if it is a template.

  value: Value of the block.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      block_label: str  # required,
      agent_id: str  # required,
      base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      deployment_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      entity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      is_template: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      label: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      preserve_on_migration: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      read_only: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      value: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> BlockResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `block_label` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `deployment_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `entity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `is_template` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `label` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `preserve_on_migration` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `read_only` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `value` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### files

Sub-resource: `client.agents.files`

  #### close()

  Closes a specific file for a given agent.

This endpoint marks a specific file as closed in the agent's file state. The
file will be removed from the agent's working memory view.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  file_id: The ID of the file in the format 'file-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  close(
      file_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `file_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### close_all()

  Closes all currently open files for a given agent.

This endpoint updates the file state for the agent so that no files are marked
as open. Typically used to reset the working memory view for the agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  close_all(
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> FileCloseAllResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get the files attached to an agent with their open/closed status.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  after: File ID cursor for pagination. Returns files that come after this file ID in the
      specified sort order

  before: File ID cursor for pagination. Returns files that come before this file ID in
      the specified sort order

  cursor: Pagination cursor from previous response (deprecated, use before/after)

  is_open: Filter by open status (true for open files, false for closed files)

  limit: Maximum number of files to return

  order: Sort order for files by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      agent_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      cursor: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      is_open: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncNextFilesPage[FileListResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `cursor` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `is_open` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### open()

  Opens a specific file for a given agent.

This endpoint marks a specific file as open in the agent's file state. The file
will be included in the agent's working memory view. Returns a list of file
names that were closed due to LRU eviction.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  file_id: The ID of the file in the format 'file-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  open(
      file_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> FileOpenResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `file_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### folders

Sub-resource: `client.agents.folders`

  #### attach()

  Attach a folder to an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  folder_id: The ID of the source in the format 'source-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  attach(
      folder_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Optional[AgentState]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `folder_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### detach()

  Detach a folder from an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  folder_id: The ID of the source in the format 'source-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  detach(
      folder_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Optional[AgentState]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `folder_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get the folders associated with an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  after: Source ID cursor for pagination. Returns sources that come after this source ID
      in the specified sort order

  before: Source ID cursor for pagination. Returns sources that come before this source ID
      in the specified sort order

  limit: Maximum number of sources to return

  order: Sort order for sources by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      agent_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[FolderListResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### groups

Sub-resource: `client.agents.groups`

  #### list()

  Lists the groups for an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  after: Group ID cursor for pagination. Returns groups that come after this group ID in
      the specified sort order

  before: Group ID cursor for pagination. Returns groups that come before this group ID in
      the specified sort order

  limit: Maximum number of groups to return

  manager_type: Manager type to filter groups by

  order: Sort order for groups by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      agent_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      manager_type: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Group]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `manager_type` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### identities

Sub-resource: `client.agents.identities`

  #### attach()

  Attach an identity to an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  attach(
      identity_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identity_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### detach()

  Detach an identity from an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  detach(
      identity_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identity_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### messages

Sub-resource: `client.agents.messages`

  #### cancel()

  Cancel runs associated with an agent.

If run_ids are passed in, cancel those in
particular.

Note to cancel active runs associated with an agent, redis is required.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  run_ids: Optional list of run IDs to cancel

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  cancel(
      agent_id: str  # required,
      run_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> MessageCancelResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `run_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### compact()

  Summarize an agent's conversation history.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  compaction_settings: Configuration for conversation compaction / summarization.

      `model` is the only required user-facing field – it specifies the summarizer
      model handle (e.g. `"openai/gpt-4o-mini"`). Per-model settings (temperature, max
      tokens, etc.) are derived from the default configuration for that handle.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  compact(
      agent_id: str  # required,
      compaction_settings: Optional[message_compact_params.CompactionSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> MessageCompactResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `compaction_settings` | Optional[message_compact_params.CompactionSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### create()

  ```python
  create(
      agent_id: str  # required,
      assistant_message_tool_kwarg: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      assistant_message_tool_name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      background: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      client_tools: Optional[Iterable[message_create_params.ClientTool]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_thinking: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_pings: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_return_message_types: Optional[List[MessageType]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      input: Union[str, Iterable[message_create_params.InputUnionMember1], None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_steps: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      messages: Optional[Iterable[message_create_params.Message]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      stream_tokens: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      streaming: Literal[False] | Literal[True] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      use_assistant_message: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> LettaResponse | Stream[LettaStreamingResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `assistant_message_tool_kwarg` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `assistant_message_tool_name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `background` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `client_tools` | Optional[Iterable[message_create_params.ClientTool]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_thinking` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_pings` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_return_message_types` | Optional[List[MessageType]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `input` | Union[str, Iterable[message_create_params.InputUnionMembe... | No | <letta_client.Omit object at 0x000002... |
  | `max_steps` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `messages` | Optional[Iterable[message_create_params.Message]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `stream_tokens` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `streaming` | Literal[False] | Literal[True] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `use_assistant_message` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### create_async()

  Asynchronously process a user message and return a run object.

The actual
processing happens in the background, and the status can be checked using the
run ID.

This is "asynchronous" in the sense that it's a background run and explicitly
must be fetched by the run ID.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  assistant_message_tool_kwarg: The name of the message argument in the designated message tool. Still supported
      for legacy agent types, but deprecated for letta_v1_agent onward.

  assistant_message_tool_name: The name of the designated message tool. Still supported for legacy agent types,
      but deprecated for letta_v1_agent onward.

  callback_url: Optional callback URL to POST to when the job completes

  client_tools: Client-side tools that the agent can call. When the agent calls a client-side
      tool, execution pauses and returns control to the client to execute the tool and
      provide the result via a ToolReturn.

  enable_thinking: If set to True, enables reasoning before responses or tool calls from the agent.

  include_return_message_types: Only return specified message types in the response. If `None` (default) returns
      all messages.

  input:
      Syntactic sugar for a single user message. Equivalent to messages=[{'role':
      'user', 'content': input}].

  max_steps: Maximum number of steps the agent should take to process the request.

  messages: The messages to be sent to the agent.

  use_assistant_message: Whether the server should parse specific tool call arguments (default
      `send_message`) as `AssistantMessage` objects. Still supported for legacy agent
      types, but deprecated for letta_v1_agent onward.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create_async(
      agent_id: str  # required,
      assistant_message_tool_kwarg: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      assistant_message_tool_name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      callback_url: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      client_tools: Optional[Iterable[message_create_async_params.ClientTool]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_thinking: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_return_message_types: Optional[List[MessageType]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      input: Union[str, Iterable[message_create_async_params.InputUnionMember1], None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_steps: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      messages: Optional[Iterable[message_create_async_params.Message]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      use_assistant_message: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Run
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `assistant_message_tool_kwarg` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `assistant_message_tool_name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `callback_url` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `client_tools` | Optional[Iterable[message_create_async_params.ClientTool]... | No | <letta_client.Omit object at 0x000002... |
  | `enable_thinking` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_return_message_types` | Optional[List[MessageType]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `input` | Union[str, Iterable[message_create_async_params.InputUnio... | No | <letta_client.Omit object at 0x000002... |
  | `max_steps` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `messages` | Optional[Iterable[message_create_async_params.Message]] |... | No | <letta_client.Omit object at 0x000002... |
  | `use_assistant_message` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Retrieve message history for an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  after: Message ID cursor for pagination. Returns messages that come after this message
      ID in the specified sort order

  assistant_message_tool_kwarg: The name of the message argument.

  assistant_message_tool_name: The name of the designated message tool.

  before: Message ID cursor for pagination. Returns messages that come before this message
      ID in the specified sort order

  conversation_id: Conversation ID to filter messages by.

  group_id: Group ID to filter messages by.

  include_err: Whether to include error messages and error statuses. For debugging purposes
      only.

  limit: Maximum number of messages to return

  order: Sort order for messages by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  use_assistant_message: Whether to use assistant messages

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      agent_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      assistant_message_tool_kwarg: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      assistant_message_tool_name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      conversation_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      group_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_err: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      use_assistant_message: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Message]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `assistant_message_tool_kwarg` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `assistant_message_tool_name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `conversation_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `group_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_err` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `use_assistant_message` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### reset()

  Resets the messages for an agent

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  add_default_initial_messages: If true, adds the default initial messages after resetting.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  reset(
      agent_id: str  # required,
      add_default_initial_messages: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Optional[AgentState]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `add_default_initial_messages` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### stream()

  Process a user message and return the agent's response.

Deprecated: Use the `POST /{agent_id}/messages` endpoint with `streaming=true`
in the request body instead.

This endpoint accepts a message from a user and processes it through the agent.
It will stream the steps of the response always, and stream the tokens if
'stream_tokens' is set to True.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  assistant_message_tool_kwarg: The name of the message argument in the designated message tool. Still supported
      for legacy agent types, but deprecated for letta_v1_agent onward.

  assistant_message_tool_name: The name of the designated message tool. Still supported for legacy agent types,
      but deprecated for letta_v1_agent onward.

  background: Whether to process the request in the background (only used when
      streaming=true).

  client_tools: Client-side tools that the agent can call. When the agent calls a client-side
      tool, execution pauses and returns control to the client to execute the tool and
      provide the result via a ToolReturn.

  enable_thinking: If set to True, enables reasoning before responses or tool calls from the agent.

  include_pings: Whether to include periodic keepalive ping messages in the stream to prevent
      connection timeouts (only used when streaming=true).

  include_return_message_types: Only return specified message types in the response. If `None` (default) returns
      all messages.

  input:
      Syntactic sugar for a single user message. Equivalent to messages=[{'role':
      'user', 'content': input}].

  max_steps: Maximum number of steps the agent should take to process the request.

  messages: The messages to be sent to the agent.

  stream_tokens: Flag to determine if individual tokens should be streamed, rather than streaming
      per step (only used when streaming=true).

  streaming: If True, returns a streaming response (Server-Sent Events). If False (default),
      returns a complete response.

  use_assistant_message: Whether the server should parse specific tool call arguments (default
      `send_message`) as `AssistantMessage` objects. Still supported for legacy agent
      types, but deprecated for letta_v1_agent onward.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  stream(
      agent_id: str  # required,
      assistant_message_tool_kwarg: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      assistant_message_tool_name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      background: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      client_tools: Optional[Iterable[message_stream_params.ClientTool]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_thinking: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_pings: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_return_message_types: Optional[List[MessageType]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      input: Union[str, Iterable[message_stream_params.InputUnionMember1], None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_steps: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      messages: Optional[Iterable[message_stream_params.Message]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      stream_tokens: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      streaming: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      use_assistant_message: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Stream[LettaStreamingResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `assistant_message_tool_kwarg` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `assistant_message_tool_name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `background` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `client_tools` | Optional[Iterable[message_stream_params.ClientTool]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_thinking` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_pings` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_return_message_types` | Optional[List[MessageType]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `input` | Union[str, Iterable[message_stream_params.InputUnionMembe... | No | <letta_client.Omit object at 0x000002... |
  | `max_steps` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `messages` | Optional[Iterable[message_stream_params.Message]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `stream_tokens` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `streaming` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `use_assistant_message` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### passages

Sub-resource: `client.agents.passages`

  #### create()

  Insert a memory into an agent's archival memory store.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  text: Text to write to archival memory.

  created_at: Optional timestamp for the memory (defaults to current UTC time).

  tags: Optional list of tags to attach to the memory.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      agent_id: str  # required,
      text: str  # required,
      created_at: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> PassageCreateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `text` | str | Yes | - |
  | `created_at` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete a memory from an agent's archival memory store.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      memory_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `memory_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Retrieve the memories in an agent's archival memory store (paginated query).

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  after: Unique ID of the memory to start the query range at.

  ascending: Whether to sort passages oldest to newest (True, default) or newest to oldest
      (False)

  before: Unique ID of the memory to end the query range at.

  limit: How many results to include in the response.

  search: Search passages by text

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      agent_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      ascending: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> PassageListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `ascending` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### search()

  Search archival memory using semantic (embedding-based) search with optional
temporal filtering.

This endpoint allows manual triggering of archival memory searches, enabling
users to query an agent's archival memory store directly via the API. The search
uses the same functionality as the agent's archival_memory_search tool but is
accessible for external API usage.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  query: String to search for using semantic similarity

  end_datetime: Filter results to passages created before this datetime

  start_datetime: Filter results to passages created after this datetime

  tag_match_mode: How to match tags - 'any' to match passages with any of the tags, 'all' to match
      only passages with all tags

  tags: Optional list of tags to filter search results

  top_k: Maximum number of results to return. Uses system default if not specified

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  search(
      agent_id: str  # required,
      query: str  # required,
      end_datetime: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      start_datetime: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tag_match_mode: Literal['any', 'all'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      top_k: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> PassageSearchResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `query` | str | Yes | - |
  | `end_datetime` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `start_datetime` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tag_match_mode` | Literal['any', 'all'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `top_k` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### schedule

Sub-resource: `client.agents.schedule`

  #### create()

  Schedule a message to be sent by the agent at a specified time or on a recurring
basis.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      agent_id: str  # required,
      messages: Iterable[schedule_create_params.Message]  # required,
      schedule: schedule_create_params.Schedule  # required,
      callback_url: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_return_message_types: List[Literal['system_message', 'user_message', 'assistant_message', 'reasoning_message', 'hidden_reasoning_message', 'tool_call_message', 'tool_return_message', 'approval_request_message', 'approval_response_message']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_steps: float | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ScheduleCreateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `messages` | Iterable[schedule_create_params.Message] | Yes | - |
  | `schedule` | schedule_create_params.Schedule | Yes | - |
  | `callback_url` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_return_message_types` | List[Literal['system_message', 'user_message', 'assistant... | No | <letta_client.Omit object at 0x000002... |
  | `max_steps` | float | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete a scheduled message by its ID for a specific agent.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      scheduled_message_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ScheduleDeleteResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `scheduled_message_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List all scheduled messages for a specific agent.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      agent_id: str  # required,
      after: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ScheduleListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `after` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve a scheduled message by its ID for a specific agent.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      scheduled_message_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ScheduleRetrieveResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `scheduled_message_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### tools

Sub-resource: `client.agents.tools`

  #### attach()

  Attach a tool to an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  tool_id: The ID of the tool in the format 'tool-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  attach(
      tool_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Optional[AgentState]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `tool_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### detach()

  Detach a tool from an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  tool_id: The ID of the tool in the format 'tool-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  detach(
      tool_id: str  # required,
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Optional[AgentState]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `tool_id` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get tools from an existing agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  after: Tool ID cursor for pagination. Returns tools that come after this tool ID in the
      specified sort order

  before: Tool ID cursor for pagination. Returns tools that come before this tool ID in
      the specified sort order

  limit: Maximum number of tools to return

  order: Sort order for tools by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      agent_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Tool]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### run()

  Trigger a tool by name on a specific agent, providing the necessary arguments.

This endpoint executes a tool that is attached to the agent, using the agent's
state and environment variables for execution context.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  args: Arguments to pass to the tool

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  run(
      tool_name: str  # required,
      agent_id: str  # required,
      args: Dict[str, object] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ToolExecutionResult
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `tool_name` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `args` | Dict[str, object] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update_approval()

  Modify the approval requirement for a tool attached to an agent.

Accepts requires_approval via request body (preferred) or query parameter
(deprecated).

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  body_requires_approval: Whether the tool requires approval before execution

  query_requires_approval: Whether the tool requires approval before execution

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update_approval(
      tool_name: str  # required,
      agent_id: str  # required,
      body_requires_approval: bool  # required,
      query_requires_approval: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Optional[AgentState]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `tool_name` | str | Yes | - |
  | `agent_id` | str | Yes | - |
  | `body_requires_approval` | bool | Yes | - |
  | `query_requires_approval` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.agents.with_raw_response`

  #### create()

  Create an agent.

Args:
  agent_type: The type of agent.

  base_template_id: Deprecated: No longer used. The base template id of the agent.

  block_ids: The ids of the blocks used by the agent.

  compaction_settings: Configuration for conversation compaction / summarization.

      `model` is the only required user-facing field – it specifies the summarizer
      model handle (e.g. `"openai/gpt-4o-mini"`). Per-model settings (temperature, max
      tokens, etc.) are derived from the default configuration for that handle.

  context_window_limit: The context window limit used by the agent.

  description: The description of the agent.

  embedding: The embedding model handle used by the agent (format: provider/model-name).

  embedding_chunk_size: Deprecated: No longer used. The embedding chunk size used by the agent.

  embedding_config: Configuration for embedding model connection and processing parameters.

  enable_reasoner: Deprecated: Use `model` field to configure reasoning instead. Whether to enable
      internal extended thinking step for a reasoner model.

  enable_sleeptime: If set to True, memory management will move to a background agent thread.

  folder_ids: The ids of the folders used by the agent.

  from_template: Deprecated: please use the 'create agents from a template' endpoint instead.

  hidden: Deprecated: No longer used. If set to True, the agent will be hidden.

  identity_ids: The ids of the identities associated with this agent.

  include_base_tool_rules: If true, attaches the Letta base tool rules (e.g. deny all tools not explicitly
      allowed).

  include_base_tools: If true, attaches the Letta core tools (e.g. core_memory related functions).

  include_default_source: If true, automatically creates and attaches a default data source for this
      agent.

  include_multi_agent_tools: If true, attaches the Letta multi-agent tools (e.g. sending a message to another
      agent).

  initial_message_sequence: The initial set of messages to put in the agent's in-context memory.

  llm_config: Configuration for Language Model (LLM) connection and generation parameters.

      .. deprecated:: LLMConfig is deprecated and should not be used as an input or
      return type in API calls. Use the schemas in letta.schemas.model (ModelSettings,
      OpenAIModelSettings, etc.) instead. For conversion, use the \__to_model() method
      or Model.\__from_llm_config() method.

  max_files_open: Maximum number of files that can be open at once for this agent. Setting this
      too high may exceed the context window, which will break the agent.

  max_reasoning_tokens: Deprecated: Use `model` field to configure reasoning tokens instead. The maximum
      number of tokens to generate for reasoning step.

  max_tokens: Deprecated: Use `model` field to configure max output tokens instead. The
      maximum number of tokens to generate, including reasoning step.

  memory_blocks: The blocks to create in the agent's in-context memory.

  memory_variables: Deprecated: Only relevant for creating agents from a template. Use the 'create
      agents from a template' endpoint instead.

  message_buffer_autoclear: If set to True, the agent will not remember previous messages (though the agent
      will still retain state via core memory blocks and archival/recall memory). Not
      recommended unless you have an advanced use case.

  metadata: The metadata of the agent.

  model: The model handle for the agent to use (format: provider/model-name).

  model_settings: The model settings for the agent.

  name: The name of the agent.

  parallel_tool_calls: Deprecated: Use `model_settings` to configure parallel tool calls instead. If
      set to True, enables parallel tool calling.

  per_file_view_window_char_limit: The per-file view window character limit for this agent. Setting this too high
      may exceed the context window, which will break the agent.

  project: Deprecated: Project should now be passed via the X-Project header instead of in
      the request body. If using the SDK, this can be done via the x_project
      parameter.

  project_id: Deprecated: No longer used. The id of the project the agent belongs to.

  reasoning: Deprecated: Use `model` field to configure reasoning instead. Whether to enable
      reasoning for this agent.

  response_format: Deprecated: Use `model_settings` field to configure response format instead. The
      response format for the agent.

  secrets: The environment variables for tool execution specific to this agent.

  source_ids: Deprecated: Use `folder_ids` field instead. The ids of the sources used by the
      agent.

  system: The system prompt used by the agent.

  tags: The tags associated with the agent.

  template: Deprecated: No longer used.

  template_id: Deprecated: No longer used. The id of the template the agent belongs to.

  timezone: The timezone of the agent (IANA format).

  tool_exec_environment_variables: Deprecated: Use `secrets` field instead. Environment variables for tool
      execution.

  tool_ids: The ids of the tools used by the agent.

  tool_rules: The tool rules governing the agent.

  tools: The tools used by the agent.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      agent_type: AgentType | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      compaction_settings: Optional[agent_create_params.CompactionSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      context_window_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_chunk_size: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_reasoner: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_sleeptime: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      folder_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      from_template: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_base_tool_rules: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_base_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_default_source: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_multi_agent_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      initial_message_sequence: Optional[Iterable[MessageCreateParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      llm_config: Optional[LlmConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_files_open: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_reasoning_tokens: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_tokens: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      memory_blocks: Optional[Iterable[CreateBlockParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      memory_variables: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      message_buffer_autoclear: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      model: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      model_settings: Optional[agent_create_params.ModelSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      parallel_tool_calls: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      per_file_view_window_char_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      reasoning: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      response_format: Optional[agent_create_params.ResponseFormat] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      secrets: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      source_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      system: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      timezone: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_exec_environment_variables: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_rules: Optional[Iterable[agent_create_params.ToolRule]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tools: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AgentState
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_type` | AgentType | Omit | No | <letta_client.Omit object at 0x000002... |
  | `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `compaction_settings` | Optional[agent_create_params.CompactionSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `context_window_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_chunk_size` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_reasoner` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_sleeptime` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `folder_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `from_template` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_base_tool_rules` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_base_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_default_source` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_multi_agent_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `initial_message_sequence` | Optional[Iterable[MessageCreateParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `llm_config` | Optional[LlmConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `max_files_open` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `max_reasoning_tokens` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `max_tokens` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `memory_blocks` | Optional[Iterable[CreateBlockParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `memory_variables` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `message_buffer_autoclear` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `model` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `model_settings` | Optional[agent_create_params.ModelSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `parallel_tool_calls` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `per_file_view_window_char_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `reasoning` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `response_format` | Optional[agent_create_params.ResponseFormat] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `secrets` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `source_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `system` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `timezone` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_exec_environment_variables` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_rules` | Optional[Iterable[agent_create_params.ToolRule]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tools` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### export_file()

  Export the serialized JSON representation of an agent, formatted with
indentation.

Args:
  use_legacy_format: If True, exports using the legacy single-agent 'v1' format with inline
      tools/blocks. If False, exports using the new multi-entity 'v2' format, with
      separate agents, tools, blocks, files, etc.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  export_file(
      agent_id: str  # required,
      max_steps: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      use_legacy_format: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> str
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `max_steps` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `use_legacy_format` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### import_file()

  Import a serialized agent file and recreate the agent(s) in the system.

Returns
the IDs of all imported agents.

Args:
  append_copy_suffix: If set to True, appends "\__copy" to the end of the agent name.

  embedding: Embedding handle to override with.

  env_vars_json: Environment variables as a JSON string to pass to the agent for tool execution.
      Use 'secrets' instead.

  name: If provided, overrides the agent name with this value.

  override_embedding_handle: Override import with specific embedding handle. Use 'embedding' instead.

  override_existing_tools: If set to True, existing tools can get their source code overwritten by the
      uploaded tool definitions. Note that Letta core tools can never be updated
      externally.

  override_name: If provided, overrides the agent name with this value. Use 'name' instead.

  project_id: The project ID to associate the uploaded agent with. This is now passed via
      headers.

  secrets: Secrets as a JSON string to pass to the agent for tool execution.

  strip_messages: If set to True, strips all messages from the agent before importing.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  import_file(
      file: FileTypes  # required,
      append_copy_suffix: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      env_vars_json: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      override_embedding_handle: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      override_existing_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      override_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      secrets: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      strip_messages: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      x_override_embedding_model: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AgentImportFileResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `file` | FileTypes | Yes | - |
  | `append_copy_suffix` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `env_vars_json` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `override_embedding_handle` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `override_existing_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `override_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `secrets` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `strip_messages` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `x_override_embedding_model` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get a list of all agents.

Args:
  after: Cursor for pagination

  ascending: Whether to sort agents oldest to newest (True) or newest to oldest (False,
      default)

  base_template_id: Search agents by base template ID

  before: Cursor for pagination

  identifier_keys: Search agents by identifier keys

  identity_id: Search agents by identity ID

  include: Specify which relational fields to include in the response. No relationships are
      included by default.

  include_relationships: Specify which relational fields (e.g., 'tools', 'sources', 'memory') to include
      in the response. If not provided, all relationships are loaded by default. Using
      this can optimize performance by reducing unnecessary joins.This is a legacy
      parameter, and no longer supported after 1.0.0 SDK versions.

  last_stop_reason: Filter agents by their last stop reason.

  limit: Limit for pagination

  match_all_tags: If True, only returns agents that match ALL given tags. Otherwise, return agents
      that have ANY of the passed-in tags.

  name: Name of the agent

  order: Sort order for agents by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  project_id: Search agents by project ID - this will default to your default project on cloud

  query_text: Search agents by name

  sort_by: Field to sort by. Options: 'created_at' (default), 'last_run_completion'

  tags: List of tags to filter agents by

  template_id: Search agents by template ID

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      ascending: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identifier_keys: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include: List[Literal['agent.blocks', 'agent.identities', 'agent.managed_group', 'agent.pending_approval', 'agent.secrets', 'agent.sources', 'agent.tags', 'agent.tools']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_relationships: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      last_stop_reason: Optional[StopReasonType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      match_all_tags: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at', 'last_run_completion'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      query_text: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      sort_by: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[AgentState]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `ascending` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identifier_keys` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include` | List[Literal['agent.blocks', 'agent.identities', 'agent.m... | No | <letta_client.Omit object at 0x000002... |
  | `include_relationships` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `last_stop_reason` | Optional[StopReasonType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `match_all_tags` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at', 'last_run_completion'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `query_text` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `sort_by` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get the state of the agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  include: Specify which relational fields to include in the response. No relationships are
      included by default.

  include_relationships: Specify which relational fields (e.g., 'tools', 'sources', 'memory') to include
      in the response. If not provided, all relationships are loaded by default. Using
      this can optimize performance by reducing unnecessary joins.This is a legacy
      parameter, and no longer supported after 1.0.0 SDK versions.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      agent_id: str  # required,
      include: List[Literal['agent.blocks', 'agent.identities', 'agent.managed_group', 'agent.pending_approval', 'agent.secrets', 'agent.sources', 'agent.tags', 'agent.tools']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_relationships: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AgentState
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `include` | List[Literal['agent.blocks', 'agent.identities', 'agent.m... | No | <letta_client.Omit object at 0x000002... |
  | `include_relationships` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update an existing agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  base_template_id: The base template id of the agent.

  block_ids: The ids of the blocks used by the agent.

  compaction_settings: Configuration for conversation compaction / summarization.

      `model` is the only required user-facing field – it specifies the summarizer
      model handle (e.g. `"openai/gpt-4o-mini"`). Per-model settings (temperature, max
      tokens, etc.) are derived from the default configuration for that handle.

  context_window_limit: The context window limit used by the agent.

  description: The description of the agent.

  embedding: The embedding model handle used by the agent (format: provider/model-name).

  embedding_config: Configuration for embedding model connection and processing parameters.

  enable_sleeptime: If set to True, memory management will move to a background agent thread.

  folder_ids: The ids of the folders used by the agent.

  hidden: If set to True, the agent will be hidden.

  identity_ids: The ids of the identities associated with this agent.

  last_run_completion: The timestamp when the agent last completed a run.

  last_run_duration_ms: The duration in milliseconds of the agent's last run.

  last_stop_reason: The stop reason from the agent's last run.

  llm_config: Configuration for Language Model (LLM) connection and generation parameters.

      .. deprecated:: LLMConfig is deprecated and should not be used as an input or
      return type in API calls. Use the schemas in letta.schemas.model (ModelSettings,
      OpenAIModelSettings, etc.) instead. For conversion, use the \__to_model() method
      or Model.\__from_llm_config() method.

  max_files_open: Maximum number of files that can be open at once for this agent. Setting this
      too high may exceed the context window, which will break the agent.

  max_tokens: Deprecated: Use `model` field to configure max output tokens instead. The
      maximum number of tokens to generate, including reasoning step.

  message_buffer_autoclear: If set to True, the agent will not remember previous messages (though the agent
      will still retain state via core memory blocks and archival/recall memory). Not
      recommended unless you have an advanced use case.

  message_ids: The ids of the messages in the agent's in-context memory.

  metadata: The metadata of the agent.

  model: The model handle used by the agent (format: provider/model-name).

  model_settings: The model settings for the agent.

  name: The name of the agent.

  parallel_tool_calls: Deprecated: Use `model_settings` to configure parallel tool calls instead. If
      set to True, enables parallel tool calling.

  per_file_view_window_char_limit: The per-file view window character limit for this agent. Setting this too high
      may exceed the context window, which will break the agent.

  project_id: The id of the project the agent belongs to.

  reasoning: Deprecated: Use `model` field to configure reasoning instead. Whether to enable
      reasoning for this agent.

  response_format: Deprecated: Use `model_settings` field to configure response format instead. The
      response format for the agent.

  secrets: The environment variables for tool execution specific to this agent.

  source_ids: Deprecated: Use `folder_ids` field instead. The ids of the sources used by the
      agent.

  system: The system prompt used by the agent.

  tags: The tags associated with the agent.

  template_id: The id of the template the agent belongs to.

  timezone: The timezone of the agent (IANA format).

  tool_exec_environment_variables: Deprecated: use `secrets` field instead

  tool_ids: The ids of the tools used by the agent.

  tool_rules: The tool rules governing the agent.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      agent_id: str  # required,
      base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      compaction_settings: Optional[agent_update_params.CompactionSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      context_window_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_sleeptime: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      folder_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      last_run_completion: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      last_run_duration_ms: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      last_stop_reason: Optional[StopReasonType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      llm_config: Optional[LlmConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_files_open: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_tokens: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      message_buffer_autoclear: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      message_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      model: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      model_settings: Optional[agent_update_params.ModelSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      parallel_tool_calls: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      per_file_view_window_char_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      reasoning: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      response_format: Optional[agent_update_params.ResponseFormat] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      secrets: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      source_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      system: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      timezone: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_exec_environment_variables: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_rules: Optional[Iterable[agent_update_params.ToolRule]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AgentState
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `compaction_settings` | Optional[agent_update_params.CompactionSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `context_window_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_sleeptime` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `folder_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `last_run_completion` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `last_run_duration_ms` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `last_stop_reason` | Optional[StopReasonType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `llm_config` | Optional[LlmConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `max_files_open` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `max_tokens` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `message_buffer_autoclear` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `message_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `model` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `model_settings` | Optional[agent_update_params.ModelSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `parallel_tool_calls` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `per_file_view_window_char_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `reasoning` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `response_format` | Optional[agent_update_params.ResponseFormat] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `secrets` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `source_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `system` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `timezone` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_exec_environment_variables` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_rules` | Optional[Iterable[agent_update_params.ToolRule]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.agents.with_streaming_response`

  #### create()

  Create an agent.

Args:
  agent_type: The type of agent.

  base_template_id: Deprecated: No longer used. The base template id of the agent.

  block_ids: The ids of the blocks used by the agent.

  compaction_settings: Configuration for conversation compaction / summarization.

      `model` is the only required user-facing field – it specifies the summarizer
      model handle (e.g. `"openai/gpt-4o-mini"`). Per-model settings (temperature, max
      tokens, etc.) are derived from the default configuration for that handle.

  context_window_limit: The context window limit used by the agent.

  description: The description of the agent.

  embedding: The embedding model handle used by the agent (format: provider/model-name).

  embedding_chunk_size: Deprecated: No longer used. The embedding chunk size used by the agent.

  embedding_config: Configuration for embedding model connection and processing parameters.

  enable_reasoner: Deprecated: Use `model` field to configure reasoning instead. Whether to enable
      internal extended thinking step for a reasoner model.

  enable_sleeptime: If set to True, memory management will move to a background agent thread.

  folder_ids: The ids of the folders used by the agent.

  from_template: Deprecated: please use the 'create agents from a template' endpoint instead.

  hidden: Deprecated: No longer used. If set to True, the agent will be hidden.

  identity_ids: The ids of the identities associated with this agent.

  include_base_tool_rules: If true, attaches the Letta base tool rules (e.g. deny all tools not explicitly
      allowed).

  include_base_tools: If true, attaches the Letta core tools (e.g. core_memory related functions).

  include_default_source: If true, automatically creates and attaches a default data source for this
      agent.

  include_multi_agent_tools: If true, attaches the Letta multi-agent tools (e.g. sending a message to another
      agent).

  initial_message_sequence: The initial set of messages to put in the agent's in-context memory.

  llm_config: Configuration for Language Model (LLM) connection and generation parameters.

      .. deprecated:: LLMConfig is deprecated and should not be used as an input or
      return type in API calls. Use the schemas in letta.schemas.model (ModelSettings,
      OpenAIModelSettings, etc.) instead. For conversion, use the \__to_model() method
      or Model.\__from_llm_config() method.

  max_files_open: Maximum number of files that can be open at once for this agent. Setting this
      too high may exceed the context window, which will break the agent.

  max_reasoning_tokens: Deprecated: Use `model` field to configure reasoning tokens instead. The maximum
      number of tokens to generate for reasoning step.

  max_tokens: Deprecated: Use `model` field to configure max output tokens instead. The
      maximum number of tokens to generate, including reasoning step.

  memory_blocks: The blocks to create in the agent's in-context memory.

  memory_variables: Deprecated: Only relevant for creating agents from a template. Use the 'create
      agents from a template' endpoint instead.

  message_buffer_autoclear: If set to True, the agent will not remember previous messages (though the agent
      will still retain state via core memory blocks and archival/recall memory). Not
      recommended unless you have an advanced use case.

  metadata: The metadata of the agent.

  model: The model handle for the agent to use (format: provider/model-name).

  model_settings: The model settings for the agent.

  name: The name of the agent.

  parallel_tool_calls: Deprecated: Use `model_settings` to configure parallel tool calls instead. If
      set to True, enables parallel tool calling.

  per_file_view_window_char_limit: The per-file view window character limit for this agent. Setting this too high
      may exceed the context window, which will break the agent.

  project: Deprecated: Project should now be passed via the X-Project header instead of in
      the request body. If using the SDK, this can be done via the x_project
      parameter.

  project_id: Deprecated: No longer used. The id of the project the agent belongs to.

  reasoning: Deprecated: Use `model` field to configure reasoning instead. Whether to enable
      reasoning for this agent.

  response_format: Deprecated: Use `model_settings` field to configure response format instead. The
      response format for the agent.

  secrets: The environment variables for tool execution specific to this agent.

  source_ids: Deprecated: Use `folder_ids` field instead. The ids of the sources used by the
      agent.

  system: The system prompt used by the agent.

  tags: The tags associated with the agent.

  template: Deprecated: No longer used.

  template_id: Deprecated: No longer used. The id of the template the agent belongs to.

  timezone: The timezone of the agent (IANA format).

  tool_exec_environment_variables: Deprecated: Use `secrets` field instead. Environment variables for tool
      execution.

  tool_ids: The ids of the tools used by the agent.

  tool_rules: The tool rules governing the agent.

  tools: The tools used by the agent.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      agent_type: AgentType | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      compaction_settings: Optional[agent_create_params.CompactionSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      context_window_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_chunk_size: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_reasoner: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_sleeptime: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      folder_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      from_template: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_base_tool_rules: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_base_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_default_source: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_multi_agent_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      initial_message_sequence: Optional[Iterable[MessageCreateParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      llm_config: Optional[LlmConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_files_open: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_reasoning_tokens: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_tokens: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      memory_blocks: Optional[Iterable[CreateBlockParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      memory_variables: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      message_buffer_autoclear: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      model: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      model_settings: Optional[agent_create_params.ModelSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      parallel_tool_calls: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      per_file_view_window_char_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      reasoning: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      response_format: Optional[agent_create_params.ResponseFormat] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      secrets: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      source_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      system: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      timezone: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_exec_environment_variables: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_rules: Optional[Iterable[agent_create_params.ToolRule]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tools: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AgentState
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_type` | AgentType | Omit | No | <letta_client.Omit object at 0x000002... |
  | `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `compaction_settings` | Optional[agent_create_params.CompactionSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `context_window_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_chunk_size` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_reasoner` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_sleeptime` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `folder_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `from_template` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_base_tool_rules` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_base_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_default_source` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_multi_agent_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `initial_message_sequence` | Optional[Iterable[MessageCreateParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `llm_config` | Optional[LlmConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `max_files_open` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `max_reasoning_tokens` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `max_tokens` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `memory_blocks` | Optional[Iterable[CreateBlockParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `memory_variables` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `message_buffer_autoclear` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `model` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `model_settings` | Optional[agent_create_params.ModelSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `parallel_tool_calls` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `per_file_view_window_char_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `reasoning` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `response_format` | Optional[agent_create_params.ResponseFormat] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `secrets` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `source_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `system` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `timezone` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_exec_environment_variables` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_rules` | Optional[Iterable[agent_create_params.ToolRule]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tools` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete an agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      agent_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### export_file()

  Export the serialized JSON representation of an agent, formatted with
indentation.

Args:
  use_legacy_format: If True, exports using the legacy single-agent 'v1' format with inline
      tools/blocks. If False, exports using the new multi-entity 'v2' format, with
      separate agents, tools, blocks, files, etc.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  export_file(
      agent_id: str  # required,
      max_steps: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      use_legacy_format: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> str
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `max_steps` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `use_legacy_format` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### import_file()

  Import a serialized agent file and recreate the agent(s) in the system.

Returns
the IDs of all imported agents.

Args:
  append_copy_suffix: If set to True, appends "\__copy" to the end of the agent name.

  embedding: Embedding handle to override with.

  env_vars_json: Environment variables as a JSON string to pass to the agent for tool execution.
      Use 'secrets' instead.

  name: If provided, overrides the agent name with this value.

  override_embedding_handle: Override import with specific embedding handle. Use 'embedding' instead.

  override_existing_tools: If set to True, existing tools can get their source code overwritten by the
      uploaded tool definitions. Note that Letta core tools can never be updated
      externally.

  override_name: If provided, overrides the agent name with this value. Use 'name' instead.

  project_id: The project ID to associate the uploaded agent with. This is now passed via
      headers.

  secrets: Secrets as a JSON string to pass to the agent for tool execution.

  strip_messages: If set to True, strips all messages from the agent before importing.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  import_file(
      file: FileTypes  # required,
      append_copy_suffix: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      env_vars_json: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      override_embedding_handle: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      override_existing_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      override_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      secrets: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      strip_messages: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      x_override_embedding_model: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AgentImportFileResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `file` | FileTypes | Yes | - |
  | `append_copy_suffix` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `env_vars_json` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `override_embedding_handle` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `override_existing_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `override_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `secrets` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `strip_messages` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `x_override_embedding_model` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get a list of all agents.

Args:
  after: Cursor for pagination

  ascending: Whether to sort agents oldest to newest (True) or newest to oldest (False,
      default)

  base_template_id: Search agents by base template ID

  before: Cursor for pagination

  identifier_keys: Search agents by identifier keys

  identity_id: Search agents by identity ID

  include: Specify which relational fields to include in the response. No relationships are
      included by default.

  include_relationships: Specify which relational fields (e.g., 'tools', 'sources', 'memory') to include
      in the response. If not provided, all relationships are loaded by default. Using
      this can optimize performance by reducing unnecessary joins.This is a legacy
      parameter, and no longer supported after 1.0.0 SDK versions.

  last_stop_reason: Filter agents by their last stop reason.

  limit: Limit for pagination

  match_all_tags: If True, only returns agents that match ALL given tags. Otherwise, return agents
      that have ANY of the passed-in tags.

  name: Name of the agent

  order: Sort order for agents by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  project_id: Search agents by project ID - this will default to your default project on cloud

  query_text: Search agents by name

  sort_by: Field to sort by. Options: 'created_at' (default), 'last_run_completion'

  tags: List of tags to filter agents by

  template_id: Search agents by template ID

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      ascending: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identifier_keys: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include: List[Literal['agent.blocks', 'agent.identities', 'agent.managed_group', 'agent.pending_approval', 'agent.secrets', 'agent.sources', 'agent.tags', 'agent.tools']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_relationships: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      last_stop_reason: Optional[StopReasonType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      match_all_tags: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at', 'last_run_completion'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      query_text: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      sort_by: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[AgentState]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `ascending` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identifier_keys` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include` | List[Literal['agent.blocks', 'agent.identities', 'agent.m... | No | <letta_client.Omit object at 0x000002... |
  | `include_relationships` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `last_stop_reason` | Optional[StopReasonType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `match_all_tags` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at', 'last_run_completion'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `query_text` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `sort_by` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get the state of the agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  include: Specify which relational fields to include in the response. No relationships are
      included by default.

  include_relationships: Specify which relational fields (e.g., 'tools', 'sources', 'memory') to include
      in the response. If not provided, all relationships are loaded by default. Using
      this can optimize performance by reducing unnecessary joins.This is a legacy
      parameter, and no longer supported after 1.0.0 SDK versions.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      agent_id: str  # required,
      include: List[Literal['agent.blocks', 'agent.identities', 'agent.managed_group', 'agent.pending_approval', 'agent.secrets', 'agent.sources', 'agent.tags', 'agent.tools']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_relationships: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AgentState
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `include` | List[Literal['agent.blocks', 'agent.identities', 'agent.m... | No | <letta_client.Omit object at 0x000002... |
  | `include_relationships` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update an existing agent.

Args:
  agent_id: The ID of the agent in the format 'agent-<uuid4>'

  base_template_id: The base template id of the agent.

  block_ids: The ids of the blocks used by the agent.

  compaction_settings: Configuration for conversation compaction / summarization.

      `model` is the only required user-facing field – it specifies the summarizer
      model handle (e.g. `"openai/gpt-4o-mini"`). Per-model settings (temperature, max
      tokens, etc.) are derived from the default configuration for that handle.

  context_window_limit: The context window limit used by the agent.

  description: The description of the agent.

  embedding: The embedding model handle used by the agent (format: provider/model-name).

  embedding_config: Configuration for embedding model connection and processing parameters.

  enable_sleeptime: If set to True, memory management will move to a background agent thread.

  folder_ids: The ids of the folders used by the agent.

  hidden: If set to True, the agent will be hidden.

  identity_ids: The ids of the identities associated with this agent.

  last_run_completion: The timestamp when the agent last completed a run.

  last_run_duration_ms: The duration in milliseconds of the agent's last run.

  last_stop_reason: The stop reason from the agent's last run.

  llm_config: Configuration for Language Model (LLM) connection and generation parameters.

      .. deprecated:: LLMConfig is deprecated and should not be used as an input or
      return type in API calls. Use the schemas in letta.schemas.model (ModelSettings,
      OpenAIModelSettings, etc.) instead. For conversion, use the \__to_model() method
      or Model.\__from_llm_config() method.

  max_files_open: Maximum number of files that can be open at once for this agent. Setting this
      too high may exceed the context window, which will break the agent.

  max_tokens: Deprecated: Use `model` field to configure max output tokens instead. The
      maximum number of tokens to generate, including reasoning step.

  message_buffer_autoclear: If set to True, the agent will not remember previous messages (though the agent
      will still retain state via core memory blocks and archival/recall memory). Not
      recommended unless you have an advanced use case.

  message_ids: The ids of the messages in the agent's in-context memory.

  metadata: The metadata of the agent.

  model: The model handle used by the agent (format: provider/model-name).

  model_settings: The model settings for the agent.

  name: The name of the agent.

  parallel_tool_calls: Deprecated: Use `model_settings` to configure parallel tool calls instead. If
      set to True, enables parallel tool calling.

  per_file_view_window_char_limit: The per-file view window character limit for this agent. Setting this too high
      may exceed the context window, which will break the agent.

  project_id: The id of the project the agent belongs to.

  reasoning: Deprecated: Use `model` field to configure reasoning instead. Whether to enable
      reasoning for this agent.

  response_format: Deprecated: Use `model_settings` field to configure response format instead. The
      response format for the agent.

  secrets: The environment variables for tool execution specific to this agent.

  source_ids: Deprecated: Use `folder_ids` field instead. The ids of the sources used by the
      agent.

  system: The system prompt used by the agent.

  tags: The tags associated with the agent.

  template_id: The id of the template the agent belongs to.

  timezone: The timezone of the agent (IANA format).

  tool_exec_environment_variables: Deprecated: use `secrets` field instead

  tool_ids: The ids of the tools used by the agent.

  tool_rules: The tool rules governing the agent.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      agent_id: str  # required,
      base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      compaction_settings: Optional[agent_update_params.CompactionSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      context_window_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_sleeptime: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      folder_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      last_run_completion: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      last_run_duration_ms: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      last_stop_reason: Optional[StopReasonType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      llm_config: Optional[LlmConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_files_open: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_tokens: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      message_buffer_autoclear: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      message_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      model: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      model_settings: Optional[agent_update_params.ModelSettings] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      parallel_tool_calls: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      per_file_view_window_char_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      reasoning: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      response_format: Optional[agent_update_params.ResponseFormat] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      secrets: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      source_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      system: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      timezone: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_exec_environment_variables: Optional[Dict[str, str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_rules: Optional[Iterable[agent_update_params.ToolRule]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AgentState
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `compaction_settings` | Optional[agent_update_params.CompactionSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `context_window_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_sleeptime` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `folder_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `last_run_completion` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `last_run_duration_ms` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `last_stop_reason` | Optional[StopReasonType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `llm_config` | Optional[LlmConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `max_files_open` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `max_tokens` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `message_buffer_autoclear` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `message_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `model` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `model_settings` | Optional[agent_update_params.ModelSettings] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `parallel_tool_calls` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `per_file_view_window_char_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `reasoning` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `response_format` | Optional[agent_update_params.ResponseFormat] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `secrets` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `source_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `system` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `timezone` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_exec_environment_variables` | Optional[Dict[str, str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_rules` | Optional[Iterable[agent_update_params.ToolRule]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Blocks

Access via `client.blocks`

#### create()

Create Block

Args:
  label: Label of the block.

  value: Value of the block.

  base_template_id: The base template id of the block.

  deployment_id: The id of the deployment.

  description: Description of the block.

  entity_id: The id of the entity within the template.

  hidden: If set to True, the block will be hidden.

  limit: Character limit of the block.

  metadata: Metadata of the block.

  preserve_on_migration: Preserve the block on template migration.

  project_id: The associated project id.

  read_only: Whether the agent has read-only access to the block.

  tags: The tags to associate with the block.

  template_id: The id of the template.

  template_name: Name of the block if it is a template.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
create(
    label: str  # required,
    value: str  # required,
    base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    deployment_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    entity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    is_template: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    preserve_on_migration: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    read_only: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    template_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> BlockResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `label` | str | Yes | - |
| `value` | str | Yes | - |
| `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `deployment_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `entity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `is_template` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
| `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `preserve_on_migration` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `read_only` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `template_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### delete()

Delete Block

Args:
  block_id: The ID of the block in the format 'block-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
delete(
    block_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> object
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `block_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### list()

List Blocks

Args:
  after: Block ID cursor for pagination.

Returns blocks that come after this block ID in
      the specified sort order

  before: Block ID cursor for pagination. Returns blocks that come before this block ID in
      the specified sort order

  connected_to_agents_count_eq: Filter blocks by the exact number of connected agents. If provided, returns
      blocks that have exactly this number of connected agents.

  connected_to_agents_count_gt: Filter blocks by the number of connected agents. If provided, returns blocks
      that have more than this number of connected agents.

  connected_to_agents_count_lt: Filter blocks by the number of connected agents. If provided, returns blocks
      that have less than this number of connected agents.

  description_search: Search blocks by description. If provided, returns blocks whose description
      matches the search query. This is a full-text search on block descriptions.

  identifier_keys: Search agents by identifier keys

  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  label: Label to include (alphanumeric, hyphens, underscores, forward slashes)

  label_search: Search blocks by label. If provided, returns blocks whose label matches the
      search query. This is a full-text search on block labels.

  limit: Number of blocks to return

  match_all_tags: If True, only returns blocks that match ALL given tags. Otherwise, return blocks
      that have ANY of the passed-in tags.

  name: Name filter (alphanumeric, spaces, hyphens, underscores)

  order: Sort order for blocks by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  project_id: Search blocks by project id

  tags: List of tags to filter blocks by

  templates_only: Whether to include only templates

  value_search: Search blocks by value. If provided, returns blocks whose value matches the
      search query. This is a full-text search on block values.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    connected_to_agents_count_eq: Optional[Iterable[int]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    connected_to_agents_count_gt: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    connected_to_agents_count_lt: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    description_search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    identifier_keys: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    identity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    label: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    label_search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    match_all_tags: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    templates_only: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    value_search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> SyncArrayPage[BlockResponse]
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `connected_to_agents_count_eq` | Optional[Iterable[int]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `connected_to_agents_count_gt` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `connected_to_agents_count_lt` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `description_search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `identifier_keys` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `identity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `label` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `label_search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `match_all_tags` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `templates_only` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `value_search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### retrieve()

Retrieve Block

Args:
  block_id: The ID of the block in the format 'block-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
retrieve(
    block_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> BlockResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `block_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### update()

Update Block

Args:
  block_id: The ID of the block in the format 'block-<uuid4>'

  base_template_id: The base template id of the block.

  deployment_id: The id of the deployment.

  description: Description of the block.

  entity_id: The id of the entity within the template.

  hidden: If set to True, the block will be hidden.

  is_template: Whether the block is a template (e.g. saved human/persona options).

  label: Label of the block (e.g. 'human', 'persona') in the context window.

  limit: Character limit of the block.

  metadata: Metadata of the block.

  preserve_on_migration: Preserve the block on template migration.

  project_id: The associated project id.

  read_only: Whether the agent has read-only access to the block.

  tags: The tags to associate with the block.

  template_id: The id of the template.

  template_name: Name of the block if it is a template.

  value: Value of the block.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
update(
    block_id: str  # required,
    base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    deployment_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    entity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    is_template: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    label: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    preserve_on_migration: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    read_only: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    template_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    value: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> BlockResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `block_id` | str | Yes | - |
| `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `deployment_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `entity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `is_template` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `label` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `preserve_on_migration` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `read_only` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `template_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `value` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### agents

Sub-resource: `client.blocks.agents`

  #### list()

  Retrieves all agents associated with the specified block.

Raises a 404 if the
block does not exist.

Args:
  block_id: The ID of the block in the format 'block-<uuid4>'

  after: Agent ID cursor for pagination. Returns agents that come after this agent ID in
      the specified sort order

  before: Agent ID cursor for pagination. Returns agents that come before this agent ID in
      the specified sort order

  include: Specify which relational fields to include in the response. No relationships are
      included by default.

  include_relationships: Specify which relational fields (e.g., 'tools', 'sources', 'memory') to include
      in the response. If not provided, all relationships are loaded by default. Using
      this can optimize performance by reducing unnecessary joins.This is a legacy
      parameter, and no longer supported after 1.0.0 SDK versions.

  limit: Maximum number of agents to return

  order: Sort order for agents by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      block_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include: List[Literal['agent.blocks', 'agent.identities', 'agent.managed_group', 'agent.pending_approval', 'agent.secrets', 'agent.sources', 'agent.tags', 'agent.tools']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_relationships: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[AgentState]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `block_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include` | List[Literal['agent.blocks', 'agent.identities', 'agent.m... | No | <letta_client.Omit object at 0x000002... |
  | `include_relationships` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.blocks.with_raw_response`

  #### create()

  Create Block

Args:
  label: Label of the block.

  value: Value of the block.

  base_template_id: The base template id of the block.

  deployment_id: The id of the deployment.

  description: Description of the block.

  entity_id: The id of the entity within the template.

  hidden: If set to True, the block will be hidden.

  limit: Character limit of the block.

  metadata: Metadata of the block.

  preserve_on_migration: Preserve the block on template migration.

  project_id: The associated project id.

  read_only: Whether the agent has read-only access to the block.

  tags: The tags to associate with the block.

  template_id: The id of the template.

  template_name: Name of the block if it is a template.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      label: str  # required,
      value: str  # required,
      base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      deployment_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      entity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      is_template: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      preserve_on_migration: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      read_only: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> BlockResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `label` | str | Yes | - |
  | `value` | str | Yes | - |
  | `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `deployment_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `entity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `is_template` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `preserve_on_migration` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `read_only` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete Block

Args:
  block_id: The ID of the block in the format 'block-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      block_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `block_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List Blocks

Args:
  after: Block ID cursor for pagination.

Returns blocks that come after this block ID in
      the specified sort order

  before: Block ID cursor for pagination. Returns blocks that come before this block ID in
      the specified sort order

  connected_to_agents_count_eq: Filter blocks by the exact number of connected agents. If provided, returns
      blocks that have exactly this number of connected agents.

  connected_to_agents_count_gt: Filter blocks by the number of connected agents. If provided, returns blocks
      that have more than this number of connected agents.

  connected_to_agents_count_lt: Filter blocks by the number of connected agents. If provided, returns blocks
      that have less than this number of connected agents.

  description_search: Search blocks by description. If provided, returns blocks whose description
      matches the search query. This is a full-text search on block descriptions.

  identifier_keys: Search agents by identifier keys

  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  label: Label to include (alphanumeric, hyphens, underscores, forward slashes)

  label_search: Search blocks by label. If provided, returns blocks whose label matches the
      search query. This is a full-text search on block labels.

  limit: Number of blocks to return

  match_all_tags: If True, only returns blocks that match ALL given tags. Otherwise, return blocks
      that have ANY of the passed-in tags.

  name: Name filter (alphanumeric, spaces, hyphens, underscores)

  order: Sort order for blocks by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  project_id: Search blocks by project id

  tags: List of tags to filter blocks by

  templates_only: Whether to include only templates

  value_search: Search blocks by value. If provided, returns blocks whose value matches the
      search query. This is a full-text search on block values.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      connected_to_agents_count_eq: Optional[Iterable[int]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      connected_to_agents_count_gt: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      connected_to_agents_count_lt: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description_search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identifier_keys: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      label: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      label_search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      match_all_tags: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      templates_only: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      value_search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[BlockResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `connected_to_agents_count_eq` | Optional[Iterable[int]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `connected_to_agents_count_gt` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `connected_to_agents_count_lt` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description_search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identifier_keys` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `label` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `label_search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `match_all_tags` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `templates_only` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `value_search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve Block

Args:
  block_id: The ID of the block in the format 'block-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      block_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> BlockResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `block_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update Block

Args:
  block_id: The ID of the block in the format 'block-<uuid4>'

  base_template_id: The base template id of the block.

  deployment_id: The id of the deployment.

  description: Description of the block.

  entity_id: The id of the entity within the template.

  hidden: If set to True, the block will be hidden.

  is_template: Whether the block is a template (e.g. saved human/persona options).

  label: Label of the block (e.g. 'human', 'persona') in the context window.

  limit: Character limit of the block.

  metadata: Metadata of the block.

  preserve_on_migration: Preserve the block on template migration.

  project_id: The associated project id.

  read_only: Whether the agent has read-only access to the block.

  tags: The tags to associate with the block.

  template_id: The id of the template.

  template_name: Name of the block if it is a template.

  value: Value of the block.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      block_id: str  # required,
      base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      deployment_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      entity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      is_template: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      label: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      preserve_on_migration: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      read_only: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      value: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> BlockResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `block_id` | str | Yes | - |
  | `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `deployment_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `entity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `is_template` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `label` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `preserve_on_migration` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `read_only` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `value` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.blocks.with_streaming_response`

  #### create()

  Create Block

Args:
  label: Label of the block.

  value: Value of the block.

  base_template_id: The base template id of the block.

  deployment_id: The id of the deployment.

  description: Description of the block.

  entity_id: The id of the entity within the template.

  hidden: If set to True, the block will be hidden.

  limit: Character limit of the block.

  metadata: Metadata of the block.

  preserve_on_migration: Preserve the block on template migration.

  project_id: The associated project id.

  read_only: Whether the agent has read-only access to the block.

  tags: The tags to associate with the block.

  template_id: The id of the template.

  template_name: Name of the block if it is a template.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      label: str  # required,
      value: str  # required,
      base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      deployment_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      entity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      is_template: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      preserve_on_migration: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      read_only: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> BlockResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `label` | str | Yes | - |
  | `value` | str | Yes | - |
  | `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `deployment_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `entity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `is_template` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `preserve_on_migration` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `read_only` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete Block

Args:
  block_id: The ID of the block in the format 'block-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      block_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `block_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List Blocks

Args:
  after: Block ID cursor for pagination.

Returns blocks that come after this block ID in
      the specified sort order

  before: Block ID cursor for pagination. Returns blocks that come before this block ID in
      the specified sort order

  connected_to_agents_count_eq: Filter blocks by the exact number of connected agents. If provided, returns
      blocks that have exactly this number of connected agents.

  connected_to_agents_count_gt: Filter blocks by the number of connected agents. If provided, returns blocks
      that have more than this number of connected agents.

  connected_to_agents_count_lt: Filter blocks by the number of connected agents. If provided, returns blocks
      that have less than this number of connected agents.

  description_search: Search blocks by description. If provided, returns blocks whose description
      matches the search query. This is a full-text search on block descriptions.

  identifier_keys: Search agents by identifier keys

  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  label: Label to include (alphanumeric, hyphens, underscores, forward slashes)

  label_search: Search blocks by label. If provided, returns blocks whose label matches the
      search query. This is a full-text search on block labels.

  limit: Number of blocks to return

  match_all_tags: If True, only returns blocks that match ALL given tags. Otherwise, return blocks
      that have ANY of the passed-in tags.

  name: Name filter (alphanumeric, spaces, hyphens, underscores)

  order: Sort order for blocks by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  project_id: Search blocks by project id

  tags: List of tags to filter blocks by

  templates_only: Whether to include only templates

  value_search: Search blocks by value. If provided, returns blocks whose value matches the
      search query. This is a full-text search on block values.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      connected_to_agents_count_eq: Optional[Iterable[int]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      connected_to_agents_count_gt: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      connected_to_agents_count_lt: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description_search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identifier_keys: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      label: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      label_search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      match_all_tags: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      templates_only: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      value_search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[BlockResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `connected_to_agents_count_eq` | Optional[Iterable[int]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `connected_to_agents_count_gt` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `connected_to_agents_count_lt` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description_search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identifier_keys` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `label` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `label_search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `match_all_tags` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `templates_only` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `value_search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve Block

Args:
  block_id: The ID of the block in the format 'block-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      block_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> BlockResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `block_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update Block

Args:
  block_id: The ID of the block in the format 'block-<uuid4>'

  base_template_id: The base template id of the block.

  deployment_id: The id of the deployment.

  description: Description of the block.

  entity_id: The id of the entity within the template.

  hidden: If set to True, the block will be hidden.

  is_template: Whether the block is a template (e.g. saved human/persona options).

  label: Label of the block (e.g. 'human', 'persona') in the context window.

  limit: Character limit of the block.

  metadata: Metadata of the block.

  preserve_on_migration: Preserve the block on template migration.

  project_id: The associated project id.

  read_only: Whether the agent has read-only access to the block.

  tags: The tags to associate with the block.

  template_id: The id of the template.

  template_name: Name of the block if it is a template.

  value: Value of the block.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      block_id: str  # required,
      base_template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      deployment_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      entity_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      is_template: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      label: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      preserve_on_migration: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      read_only: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      template_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      value: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> BlockResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `block_id` | str | Yes | - |
  | `base_template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `deployment_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `entity_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `is_template` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `label` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `preserve_on_migration` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `read_only` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `template_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `value` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Identities

Access via `client.identities`

#### create()

Create Identity

Args:
  identifier_key: External, user-generated identifier key of the identity.

  identity_type: The type of the identity.

  name: The name of the identity.

  agent_ids: The agent ids that are associated with the identity.

  block_ids: The IDs of the blocks associated with the identity.

  project_id: The project id of the identity, if applicable.

  properties: List of properties associated with the identity.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
create(
    identifier_key: str  # required,
    identity_type: IdentityType  # required,
    name: str  # required,
    agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    properties: Optional[Iterable[IdentityPropertyParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Identity
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `identifier_key` | str | Yes | - |
| `identity_type` | IdentityType | Yes | - |
| `name` | str | Yes | - |
| `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `properties` | Optional[Iterable[IdentityPropertyParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### delete()

Delete an identity by its identifier key

Args:
  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
delete(
    identity_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> object
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `identity_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### list()

Get a list of all identities in the database

Args:
  after: Identity ID cursor for pagination. Returns identities that come after this
      identity ID in the specified sort order

  before: Identity ID cursor for pagination. Returns identities that come before this
      identity ID in the specified sort order

  identity_type: Enum to represent the type of the identity.

  limit: Maximum number of identities to return

  order: Sort order for identities by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  project_id: [DEPRECATED: Use X-Project-Id header instead] Filter identities by project ID

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    identifier_key: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    identity_type: Optional[IdentityType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> SyncArrayPage[Identity]
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `identifier_key` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `identity_type` | Optional[IdentityType] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### retrieve()

Retrieve Identity

Args:
  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
retrieve(
    identity_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Identity
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `identity_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### update()

Update Identity

Args:
  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  agent_ids: The agent ids that are associated with the identity.

  block_ids: The IDs of the blocks associated with the identity.

  identifier_key: External, user-generated identifier key of the identity.

  identity_type: Enum to represent the type of the identity.

  name: The name of the identity.

  properties: List of properties associated with the identity.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
update(
    identity_id: str  # required,
    agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    identifier_key: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    identity_type: Optional[IdentityType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    properties: Optional[Iterable[IdentityPropertyParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Identity
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `identity_id` | str | Yes | - |
| `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `identifier_key` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `identity_type` | Optional[IdentityType] | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `properties` | Optional[Iterable[IdentityPropertyParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### upsert()

Upsert Identity

Args:
  identifier_key: External, user-generated identifier key of the identity.

  identity_type: The type of the identity.

  name: The name of the identity.

  agent_ids: The agent ids that are associated with the identity.

  block_ids: The IDs of the blocks associated with the identity.

  project_id: The project id of the identity, if applicable.

  properties: List of properties associated with the identity.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
upsert(
    identifier_key: str  # required,
    identity_type: IdentityType  # required,
    name: str  # required,
    agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    properties: Optional[Iterable[IdentityPropertyParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Identity
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `identifier_key` | str | Yes | - |
| `identity_type` | IdentityType | Yes | - |
| `name` | str | Yes | - |
| `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `properties` | Optional[Iterable[IdentityPropertyParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### agents

Sub-resource: `client.identities.agents`

  #### list()

  Get all agents associated with the specified identity.

Args:
  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  after: Agent ID cursor for pagination. Returns agents that come after this agent ID in
      the specified sort order

  before: Agent ID cursor for pagination. Returns agents that come before this agent ID in
      the specified sort order

  include: Specify which relational fields to include in the response. No relationships are
      included by default.

  limit: Maximum number of agents to return

  order: Sort order for agents by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      identity_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include: List[Literal['agent.blocks', 'agent.identities', 'agent.managed_group', 'agent.pending_approval', 'agent.secrets', 'agent.sources', 'agent.tags', 'agent.tools']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[AgentState]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identity_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include` | List[Literal['agent.blocks', 'agent.identities', 'agent.m... | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### blocks

Sub-resource: `client.identities.blocks`

  #### list()

  Get all blocks associated with the specified identity.

Args:
  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  after: Block ID cursor for pagination. Returns blocks that come after this block ID in
      the specified sort order

  before: Block ID cursor for pagination. Returns blocks that come before this block ID in
      the specified sort order

  limit: Maximum number of blocks to return

  order: Sort order for blocks by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      identity_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[BlockResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identity_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### properties

Sub-resource: `client.identities.properties`

  #### upsert()

  Upsert Properties For Identity

Args:
  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  upsert(
      identity_id: str  # required,
      body: Iterable[IdentityPropertyParam]  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identity_id` | str | Yes | - |
  | `body` | Iterable[IdentityPropertyParam] | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.identities.with_raw_response`

  #### create()

  Create Identity

Args:
  identifier_key: External, user-generated identifier key of the identity.

  identity_type: The type of the identity.

  name: The name of the identity.

  agent_ids: The agent ids that are associated with the identity.

  block_ids: The IDs of the blocks associated with the identity.

  project_id: The project id of the identity, if applicable.

  properties: List of properties associated with the identity.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      identifier_key: str  # required,
      identity_type: IdentityType  # required,
      name: str  # required,
      agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      properties: Optional[Iterable[IdentityPropertyParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Identity
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identifier_key` | str | Yes | - |
  | `identity_type` | IdentityType | Yes | - |
  | `name` | str | Yes | - |
  | `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `properties` | Optional[Iterable[IdentityPropertyParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete an identity by its identifier key

Args:
  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      identity_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identity_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get a list of all identities in the database

Args:
  after: Identity ID cursor for pagination. Returns identities that come after this
      identity ID in the specified sort order

  before: Identity ID cursor for pagination. Returns identities that come before this
      identity ID in the specified sort order

  identity_type: Enum to represent the type of the identity.

  limit: Maximum number of identities to return

  order: Sort order for identities by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  project_id: [DEPRECATED: Use X-Project-Id header instead] Filter identities by project ID

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identifier_key: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_type: Optional[IdentityType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Identity]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identifier_key` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_type` | Optional[IdentityType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve Identity

Args:
  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      identity_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Identity
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identity_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update Identity

Args:
  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  agent_ids: The agent ids that are associated with the identity.

  block_ids: The IDs of the blocks associated with the identity.

  identifier_key: External, user-generated identifier key of the identity.

  identity_type: Enum to represent the type of the identity.

  name: The name of the identity.

  properties: List of properties associated with the identity.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      identity_id: str  # required,
      agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identifier_key: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_type: Optional[IdentityType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      properties: Optional[Iterable[IdentityPropertyParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Identity
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identity_id` | str | Yes | - |
  | `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identifier_key` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_type` | Optional[IdentityType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `properties` | Optional[Iterable[IdentityPropertyParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### upsert()

  Upsert Identity

Args:
  identifier_key: External, user-generated identifier key of the identity.

  identity_type: The type of the identity.

  name: The name of the identity.

  agent_ids: The agent ids that are associated with the identity.

  block_ids: The IDs of the blocks associated with the identity.

  project_id: The project id of the identity, if applicable.

  properties: List of properties associated with the identity.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  upsert(
      identifier_key: str  # required,
      identity_type: IdentityType  # required,
      name: str  # required,
      agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      properties: Optional[Iterable[IdentityPropertyParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Identity
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identifier_key` | str | Yes | - |
  | `identity_type` | IdentityType | Yes | - |
  | `name` | str | Yes | - |
  | `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `properties` | Optional[Iterable[IdentityPropertyParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.identities.with_streaming_response`

  #### create()

  Create Identity

Args:
  identifier_key: External, user-generated identifier key of the identity.

  identity_type: The type of the identity.

  name: The name of the identity.

  agent_ids: The agent ids that are associated with the identity.

  block_ids: The IDs of the blocks associated with the identity.

  project_id: The project id of the identity, if applicable.

  properties: List of properties associated with the identity.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      identifier_key: str  # required,
      identity_type: IdentityType  # required,
      name: str  # required,
      agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      properties: Optional[Iterable[IdentityPropertyParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Identity
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identifier_key` | str | Yes | - |
  | `identity_type` | IdentityType | Yes | - |
  | `name` | str | Yes | - |
  | `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `properties` | Optional[Iterable[IdentityPropertyParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete an identity by its identifier key

Args:
  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      identity_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identity_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get a list of all identities in the database

Args:
  after: Identity ID cursor for pagination. Returns identities that come after this
      identity ID in the specified sort order

  before: Identity ID cursor for pagination. Returns identities that come before this
      identity ID in the specified sort order

  identity_type: Enum to represent the type of the identity.

  limit: Maximum number of identities to return

  order: Sort order for identities by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  project_id: [DEPRECATED: Use X-Project-Id header instead] Filter identities by project ID

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identifier_key: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_type: Optional[IdentityType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Identity]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identifier_key` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_type` | Optional[IdentityType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve Identity

Args:
  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      identity_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Identity
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identity_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update Identity

Args:
  identity_id: The ID of the identity in the format 'identity-<uuid4>'

  agent_ids: The agent ids that are associated with the identity.

  block_ids: The IDs of the blocks associated with the identity.

  identifier_key: External, user-generated identifier key of the identity.

  identity_type: Enum to represent the type of the identity.

  name: The name of the identity.

  properties: List of properties associated with the identity.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      identity_id: str  # required,
      agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identifier_key: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_type: Optional[IdentityType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      properties: Optional[Iterable[IdentityPropertyParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Identity
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identity_id` | str | Yes | - |
  | `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identifier_key` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_type` | Optional[IdentityType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `properties` | Optional[Iterable[IdentityPropertyParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### upsert()

  Upsert Identity

Args:
  identifier_key: External, user-generated identifier key of the identity.

  identity_type: The type of the identity.

  name: The name of the identity.

  agent_ids: The agent ids that are associated with the identity.

  block_ids: The IDs of the blocks associated with the identity.

  project_id: The project id of the identity, if applicable.

  properties: List of properties associated with the identity.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  upsert(
      identifier_key: str  # required,
      identity_type: IdentityType  # required,
      name: str  # required,
      agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      properties: Optional[Iterable[IdentityPropertyParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Identity
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `identifier_key` | str | Yes | - |
  | `identity_type` | IdentityType | Yes | - |
  | `name` | str | Yes | - |
  | `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `properties` | Optional[Iterable[IdentityPropertyParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Access_tokens

Access via `client.access_tokens`

#### create()

Create a new client side access token with the specified configuration.

Args:
  hostname: The hostname of the client side application. Please specify the full URL
      including the protocol (http or https).

  expires_at: The expiration date of the token. If not provided, the token will expire in 5
      minutes

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
create(
    hostname: str  # required,
    policy: Iterable[access_token_create_params.Policy]  # required,
    expires_at: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> AccessTokenCreateResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `hostname` | str | Yes | - |
| `policy` | Iterable[access_token_create_params.Policy] | Yes | - |
| `expires_at` | str | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### delete()

Delete a client side access token.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
delete(
    token: str  # required,
    body: object | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> object
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `token` | str | Yes | - |
| `body` | object | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### list()

List all client side access tokens for the current account.

This is only
available for cloud users.

Args:
  agent_id: The agent ID to filter tokens by. If provided, only tokens for this agent will
      be returned.

  limit: The number of tokens to return per page. Defaults to 10.

  offset: The offset for pagination. Defaults to 0.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    agent_id: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: float | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    offset: float | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> AccessTokenListResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `agent_id` | str | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | float | Omit | No | <letta_client.Omit object at 0x000002... |
| `offset` | float | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.access_tokens.with_raw_response`

  #### create()

  Create a new client side access token with the specified configuration.

Args:
  hostname: The hostname of the client side application. Please specify the full URL
      including the protocol (http or https).

  expires_at: The expiration date of the token. If not provided, the token will expire in 5
      minutes

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      hostname: str  # required,
      policy: Iterable[access_token_create_params.Policy]  # required,
      expires_at: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AccessTokenCreateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `hostname` | str | Yes | - |
  | `policy` | Iterable[access_token_create_params.Policy] | Yes | - |
  | `expires_at` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete a client side access token.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      token: str  # required,
      body: object | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `token` | str | Yes | - |
  | `body` | object | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List all client side access tokens for the current account.

This is only
available for cloud users.

Args:
  agent_id: The agent ID to filter tokens by. If provided, only tokens for this agent will
      be returned.

  limit: The number of tokens to return per page. Defaults to 10.

  offset: The offset for pagination. Defaults to 0.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      agent_id: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: float | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      offset: float | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AccessTokenListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | float | Omit | No | <letta_client.Omit object at 0x000002... |
  | `offset` | float | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.access_tokens.with_streaming_response`

  #### create()

  Create a new client side access token with the specified configuration.

Args:
  hostname: The hostname of the client side application. Please specify the full URL
      including the protocol (http or https).

  expires_at: The expiration date of the token. If not provided, the token will expire in 5
      minutes

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      hostname: str  # required,
      policy: Iterable[access_token_create_params.Policy]  # required,
      expires_at: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AccessTokenCreateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `hostname` | str | Yes | - |
  | `policy` | Iterable[access_token_create_params.Policy] | Yes | - |
  | `expires_at` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete a client side access token.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      token: str  # required,
      body: object | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `token` | str | Yes | - |
  | `body` | object | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List all client side access tokens for the current account.

This is only
available for cloud users.

Args:
  agent_id: The agent ID to filter tokens by. If provided, only tokens for this agent will
      be returned.

  limit: The number of tokens to return per page. Defaults to 10.

  offset: The offset for pagination. Defaults to 0.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      agent_id: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: float | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      offset: float | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AccessTokenListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | float | Omit | No | <letta_client.Omit object at 0x000002... |
  | `offset` | float | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Archives

Access via `client.archives`

#### create()

Create a new archive.

Args:
  embedding: Embedding model handle for the archive

  embedding_config: Configuration for embedding model connection and processing parameters.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
create(
    name: str  # required,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Archive
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `name` | str | Yes | - |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### delete()

Delete an archive by its ID.

Args:
  archive_id: The ID of the archive in the format 'archive-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
delete(
    archive_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> None
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `archive_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### list()

Get a list of all archives for the current organization with optional filters
and pagination.

Args:
  after: Archive ID cursor for pagination. Returns archives that come after this archive
      ID in the specified sort order

  agent_id: Only archives attached to this agent ID

  before: Archive ID cursor for pagination. Returns archives that come before this archive
      ID in the specified sort order

  limit: Maximum number of archives to return

  name: Filter by archive name (exact match)

  order: Sort order for archives by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> SyncArrayPage[Archive]
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### retrieve()

Get a single archive by its ID.

Args:
  archive_id: The ID of the archive in the format 'archive-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
retrieve(
    archive_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Archive
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `archive_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### update()

Update an existing archive's name and/or description.

Args:
  archive_id: The ID of the archive in the format 'archive-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
update(
    archive_id: str  # required,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Archive
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `archive_id` | str | Yes | - |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### passages

Sub-resource: `client.archives.passages`

  #### create()

  Create a new passage in an archive.

This adds a passage to the archive and creates embeddings for vector storage.

Args:
  archive_id: The ID of the archive in the format 'archive-<uuid4>'

  text: The text content of the passage

  metadata: Optional metadata for the passage

  tags: Optional tags for categorizing the passage

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      archive_id: str  # required,
      text: str  # required,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Passage
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `archive_id` | str | Yes | - |
  | `text` | str | Yes | - |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete a passage from an archive.

This permanently removes the passage from both the database and vector storage
(if applicable).

Args:
  archive_id: The ID of the archive in the format 'archive-<uuid4>'

  passage_id: The ID of the passage in the format 'passage-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      passage_id: str  # required,
      archive_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> None
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `passage_id` | str | Yes | - |
  | `archive_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.archives.with_raw_response`

  #### create()

  Create a new archive.

Args:
  embedding: Embedding model handle for the archive

  embedding_config: Configuration for embedding model connection and processing parameters.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      name: str  # required,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Archive
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `name` | str | Yes | - |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete an archive by its ID.

Args:
  archive_id: The ID of the archive in the format 'archive-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      archive_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> None
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `archive_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get a list of all archives for the current organization with optional filters
and pagination.

Args:
  after: Archive ID cursor for pagination. Returns archives that come after this archive
      ID in the specified sort order

  agent_id: Only archives attached to this agent ID

  before: Archive ID cursor for pagination. Returns archives that come before this archive
      ID in the specified sort order

  limit: Maximum number of archives to return

  name: Filter by archive name (exact match)

  order: Sort order for archives by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Archive]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get a single archive by its ID.

Args:
  archive_id: The ID of the archive in the format 'archive-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      archive_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Archive
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `archive_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update an existing archive's name and/or description.

Args:
  archive_id: The ID of the archive in the format 'archive-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      archive_id: str  # required,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Archive
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `archive_id` | str | Yes | - |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.archives.with_streaming_response`

  #### create()

  Create a new archive.

Args:
  embedding: Embedding model handle for the archive

  embedding_config: Configuration for embedding model connection and processing parameters.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      name: str  # required,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Archive
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `name` | str | Yes | - |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete an archive by its ID.

Args:
  archive_id: The ID of the archive in the format 'archive-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      archive_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> None
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `archive_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get a list of all archives for the current organization with optional filters
and pagination.

Args:
  after: Archive ID cursor for pagination. Returns archives that come after this archive
      ID in the specified sort order

  agent_id: Only archives attached to this agent ID

  before: Archive ID cursor for pagination. Returns archives that come before this archive
      ID in the specified sort order

  limit: Maximum number of archives to return

  name: Filter by archive name (exact match)

  order: Sort order for archives by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Archive]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get a single archive by its ID.

Args:
  archive_id: The ID of the archive in the format 'archive-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      archive_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Archive
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `archive_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update an existing archive's name and/or description.

Args:
  archive_id: The ID of the archive in the format 'archive-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      archive_id: str  # required,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Archive
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `archive_id` | str | Yes | - |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Batches

Access via `client.batches`

#### cancel()

Cancel a batch run.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
cancel(
    batch_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> object
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `batch_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### create()

Submit a batch of agent runs for asynchronous processing.

Creates a job that will fan out messages to all listed agents and process them
in parallel. The request will be rejected if it exceeds 256MB.

Args:
  requests: List of requests to be processed in batch.

  callback_url: Optional URL to call via POST when the batch completes. The callback payload
      will be a JSON object with the following fields: {'job_id': string, 'status':
      string, 'completed_at': string}. Where 'job_id' is the unique batch job
      identifier, 'status' is the final batch status (e.g., 'completed', 'failed'),
      and 'completed_at' is an ISO 8601 timestamp indicating when the batch job
      completed.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
create(
    requests: Iterable[batch_create_params.Request]  # required,
    callback_url: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> BatchJob
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `requests` | Iterable[batch_create_params.Request] | Yes | - |
| `callback_url` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### list()

List all batch runs.

Args:
  after: Job ID cursor for pagination.

Returns jobs that come after this job ID in the
      specified sort order

  before: Job ID cursor for pagination. Returns jobs that come before this job ID in the
      specified sort order

  limit: Maximum number of jobs to return

  order: Sort order for jobs by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> SyncArrayPage[BatchJob]
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### retrieve()

Retrieve the status and details of a batch run.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
retrieve(
    batch_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> BatchJob
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `batch_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### messages

Sub-resource: `client.batches.messages`

  #### list()

  Get response messages for a specific batch job.

Args:
  after: Message ID cursor for pagination. Returns messages that come after this message
      ID in the specified sort order

  agent_id: Filter messages by agent ID

  before: Message ID cursor for pagination. Returns messages that come before this message
      ID in the specified sort order

  limit: Maximum number of messages to return

  order: Sort order for messages by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      batch_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncObjectPage[InternalMessage]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `batch_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.batches.with_raw_response`

  #### cancel()

  Cancel a batch run.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  cancel(
      batch_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `batch_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### create()

  Submit a batch of agent runs for asynchronous processing.

Creates a job that will fan out messages to all listed agents and process them
in parallel. The request will be rejected if it exceeds 256MB.

Args:
  requests: List of requests to be processed in batch.

  callback_url: Optional URL to call via POST when the batch completes. The callback payload
      will be a JSON object with the following fields: {'job_id': string, 'status':
      string, 'completed_at': string}. Where 'job_id' is the unique batch job
      identifier, 'status' is the final batch status (e.g., 'completed', 'failed'),
      and 'completed_at' is an ISO 8601 timestamp indicating when the batch job
      completed.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      requests: Iterable[batch_create_params.Request]  # required,
      callback_url: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> BatchJob
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `requests` | Iterable[batch_create_params.Request] | Yes | - |
  | `callback_url` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List all batch runs.

Args:
  after: Job ID cursor for pagination.

Returns jobs that come after this job ID in the
      specified sort order

  before: Job ID cursor for pagination. Returns jobs that come before this job ID in the
      specified sort order

  limit: Maximum number of jobs to return

  order: Sort order for jobs by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[BatchJob]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve the status and details of a batch run.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      batch_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> BatchJob
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `batch_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.batches.with_streaming_response`

  #### cancel()

  Cancel a batch run.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  cancel(
      batch_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `batch_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### create()

  Submit a batch of agent runs for asynchronous processing.

Creates a job that will fan out messages to all listed agents and process them
in parallel. The request will be rejected if it exceeds 256MB.

Args:
  requests: List of requests to be processed in batch.

  callback_url: Optional URL to call via POST when the batch completes. The callback payload
      will be a JSON object with the following fields: {'job_id': string, 'status':
      string, 'completed_at': string}. Where 'job_id' is the unique batch job
      identifier, 'status' is the final batch status (e.g., 'completed', 'failed'),
      and 'completed_at' is an ISO 8601 timestamp indicating when the batch job
      completed.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      requests: Iterable[batch_create_params.Request]  # required,
      callback_url: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> BatchJob
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `requests` | Iterable[batch_create_params.Request] | Yes | - |
  | `callback_url` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List all batch runs.

Args:
  after: Job ID cursor for pagination.

Returns jobs that come after this job ID in the
      specified sort order

  before: Job ID cursor for pagination. Returns jobs that come before this job ID in the
      specified sort order

  limit: Maximum number of jobs to return

  order: Sort order for jobs by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[BatchJob]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve the status and details of a batch run.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      batch_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> BatchJob
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `batch_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Conversations

Access via `client.conversations`

#### create()

Create a new conversation for an agent.

Args:
  agent_id: The agent ID to create a conversation for

  isolated_block_labels: List of block labels that should be isolated (conversation-specific) rather than
      shared across conversations. New blocks will be created as copies of the agent's
      blocks with these labels.

  summary: A summary of the conversation.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
create(
    agent_id: str  # required,
    isolated_block_labels: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    summary: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Conversation
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `agent_id` | str | Yes | - |
| `isolated_block_labels` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `summary` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### list()

List all conversations for an agent.

Args:
  agent_id: The agent ID to list conversations for

  after: Cursor for pagination (conversation ID)

  limit: Maximum number of conversations to return

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    agent_id: str  # required,
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> ConversationListResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `agent_id` | str | Yes | - |
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### retrieve()

Retrieve a specific conversation.

Args:
  conversation_id: The ID of the conv in the format 'conv-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
retrieve(
    conversation_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Conversation
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `conversation_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### messages

Sub-resource: `client.conversations.messages`

  #### create()

  Send a message to a conversation and get a streaming response.

This endpoint sends a message to an existing conversation and streams the
agent's response back.

Args:
  conversation_id: The ID of the conv in the format 'conv-<uuid4>'

  assistant_message_tool_kwarg: The name of the message argument in the designated message tool. Still supported
      for legacy agent types, but deprecated for letta_v1_agent onward.

  assistant_message_tool_name: The name of the designated message tool. Still supported for legacy agent types,
      but deprecated for letta_v1_agent onward.

  background: Whether to process the request in the background (only used when
      streaming=true).

  client_tools: Client-side tools that the agent can call. When the agent calls a client-side
      tool, execution pauses and returns control to the client to execute the tool and
      provide the result via a ToolReturn.

  enable_thinking: If set to True, enables reasoning before responses or tool calls from the agent.

  include_pings: Whether to include periodic keepalive ping messages in the stream to prevent
      connection timeouts (only used when streaming=true).

  include_return_message_types: Only return specified message types in the response. If `None` (default) returns
      all messages.

  input:
      Syntactic sugar for a single user message. Equivalent to messages=[{'role':
      'user', 'content': input}].

  max_steps: Maximum number of steps the agent should take to process the request.

  messages: The messages to be sent to the agent.

  stream_tokens: Flag to determine if individual tokens should be streamed, rather than streaming
      per step (only used when streaming=true).

  streaming: If True, returns a streaming response (Server-Sent Events). If False (default),
      returns a complete response.

  use_assistant_message: Whether the server should parse specific tool call arguments (default
      `send_message`) as `AssistantMessage` objects. Still supported for legacy agent
      types, but deprecated for letta_v1_agent onward.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      conversation_id: str  # required,
      assistant_message_tool_kwarg: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      assistant_message_tool_name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      background: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      client_tools: Optional[Iterable[message_create_params.ClientTool]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_thinking: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_pings: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_return_message_types: Optional[List[MessageType]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      input: Union[str, Iterable[message_create_params.InputUnionMember1], None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_steps: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      messages: Optional[Iterable[message_create_params.Message]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      stream_tokens: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      streaming: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      use_assistant_message: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Stream[LettaStreamingResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `conversation_id` | str | Yes | - |
  | `assistant_message_tool_kwarg` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `assistant_message_tool_name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `background` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `client_tools` | Optional[Iterable[message_create_params.ClientTool]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_thinking` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_pings` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_return_message_types` | Optional[List[MessageType]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `input` | Union[str, Iterable[message_create_params.InputUnionMembe... | No | <letta_client.Omit object at 0x000002... |
  | `max_steps` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `messages` | Optional[Iterable[message_create_params.Message]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `stream_tokens` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `streaming` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `use_assistant_message` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List all messages in a conversation.

Returns LettaMessage objects (UserMessage, AssistantMessage, etc.) for all
messages in the conversation, ordered by position (oldest first), with support
for cursor-based pagination.

Args:
  conversation_id: The ID of the conv in the format 'conv-<uuid4>'

  after: Message ID cursor for pagination. Returns messages that come after this message
      ID in the conversation

  before: Message ID cursor for pagination. Returns messages that come before this message
      ID in the conversation

  limit: Maximum number of messages to return

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      conversation_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> MessageListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `conversation_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### stream()

  Resume the stream for the most recent active run in a conversation.

This endpoint allows you to reconnect to an active background stream for a
conversation, enabling recovery from network interruptions.

Args:
  conversation_id: The ID of the conv in the format 'conv-<uuid4>'

  batch_size: Number of entries to read per batch.

  include_pings: Whether to include periodic keepalive ping messages in the stream to prevent
      connection timeouts.

  poll_interval: Seconds to wait between polls when no new data.

  starting_after: Sequence id to use as a cursor for pagination. Response will start streaming
      after this chunk sequence id

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  stream(
      conversation_id: str  # required,
      batch_size: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_pings: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      poll_interval: Optional[float] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      starting_after: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Stream[LettaStreamingResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `conversation_id` | str | Yes | - |
  | `batch_size` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_pings` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `poll_interval` | Optional[float] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `starting_after` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.conversations.with_raw_response`

  #### create()

  Create a new conversation for an agent.

Args:
  agent_id: The agent ID to create a conversation for

  isolated_block_labels: List of block labels that should be isolated (conversation-specific) rather than
      shared across conversations. New blocks will be created as copies of the agent's
      blocks with these labels.

  summary: A summary of the conversation.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      agent_id: str  # required,
      isolated_block_labels: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      summary: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Conversation
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `isolated_block_labels` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `summary` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List all conversations for an agent.

Args:
  agent_id: The agent ID to list conversations for

  after: Cursor for pagination (conversation ID)

  limit: Maximum number of conversations to return

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      agent_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ConversationListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve a specific conversation.

Args:
  conversation_id: The ID of the conv in the format 'conv-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      conversation_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Conversation
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `conversation_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.conversations.with_streaming_response`

  #### create()

  Create a new conversation for an agent.

Args:
  agent_id: The agent ID to create a conversation for

  isolated_block_labels: List of block labels that should be isolated (conversation-specific) rather than
      shared across conversations. New blocks will be created as copies of the agent's
      blocks with these labels.

  summary: A summary of the conversation.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      agent_id: str  # required,
      isolated_block_labels: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      summary: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Conversation
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `isolated_block_labels` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `summary` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List all conversations for an agent.

Args:
  agent_id: The agent ID to list conversations for

  after: Cursor for pagination (conversation ID)

  limit: Maximum number of conversations to return

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      agent_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ConversationListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve a specific conversation.

Args:
  conversation_id: The ID of the conv in the format 'conv-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      conversation_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Conversation
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `conversation_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Folders

Access via `client.folders`

#### create()

Create a new data folder.

Args:
  name: The name of the source.

  description: The description of the source.

  embedding: The handle for the embedding config used by the source.

  embedding_chunk_size: The chunk size of the embedding.

  embedding_config: Configuration for embedding model connection and processing parameters.

  instructions: Instructions for how to use the source.

  metadata: Metadata associated with the source.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
create(
    name: str  # required,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    embedding_chunk_size: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    instructions: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Folder
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `name` | str | Yes | - |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `embedding_chunk_size` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
| `instructions` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### delete()

Delete a data folder.

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
delete(
    folder_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> object
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `folder_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### list()

List all data folders created by a user.

Args:
  after: Folder ID cursor for pagination. Returns folders that come after this folder ID
      in the specified sort order

  before: Folder ID cursor for pagination. Returns folders that come before this folder ID
      in the specified sort order

  limit: Maximum number of folders to return

  name: Folder name to filter by

  order: Sort order for folders by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> SyncArrayPage[Folder]
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### retrieve()

Get a folder by ID

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
retrieve(
    folder_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Folder
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `folder_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### update()

Update the name or documentation of an existing data folder.

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  description: The description of the source.

  embedding_config: Configuration for embedding model connection and processing parameters.

  instructions: Instructions for how to use the source.

  metadata: Metadata associated with the source.

  name: The name of the source.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
update(
    folder_id: str  # required,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    instructions: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Folder
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `folder_id` | str | Yes | - |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
| `instructions` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### agents

Sub-resource: `client.folders.agents`

  #### list()

  Get all agent IDs that have the specified folder attached.

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  after: Agent ID cursor for pagination. Returns agents that come after this agent ID in
      the specified sort order

  before: Agent ID cursor for pagination. Returns agents that come before this agent ID in
      the specified sort order

  limit: Maximum number of agents to return

  order: Sort order for agents by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      folder_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AgentListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `folder_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### files

Sub-resource: `client.folders.files`

  #### delete()

  Delete a file from a folder.

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  file_id: The ID of the file in the format 'file-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      file_id: str  # required,
      folder_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> None
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `file_id` | str | Yes | - |
  | `folder_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List paginated files associated with a data folder.

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  after: File ID cursor for pagination. Returns files that come after this file ID in the
      specified sort order

  before: File ID cursor for pagination. Returns files that come before this file ID in
      the specified sort order

  include_content: Whether to include full file content

  limit: Maximum number of files to return

  order: Sort order for files by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      folder_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_content: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[FileListResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `folder_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_content` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve a file from a folder by ID.

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  file_id: The ID of the file in the format 'file-<uuid4>'

  include_content: Whether to include full file content

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      file_id: str  # required,
      folder_id: str  # required,
      include_content: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> FileRetrieveResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `file_id` | str | Yes | - |
  | `folder_id` | str | Yes | - |
  | `include_content` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### upload()

  Upload a file to a data folder.

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  duplicate_handling: How to handle duplicate filenames

  name: Optional custom name to override the uploaded file's name

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  upload(
      folder_id: str  # required,
      file: FileTypes  # required,
      duplicate_handling: Literal['skip', 'error', 'suffix', 'replace'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> FileUploadResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `folder_id` | str | Yes | - |
  | `file` | FileTypes | Yes | - |
  | `duplicate_handling` | Literal['skip', 'error', 'suffix', 'replace'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.folders.with_raw_response`

  #### create()

  Create a new data folder.

Args:
  name: The name of the source.

  description: The description of the source.

  embedding: The handle for the embedding config used by the source.

  embedding_chunk_size: The chunk size of the embedding.

  embedding_config: Configuration for embedding model connection and processing parameters.

  instructions: Instructions for how to use the source.

  metadata: Metadata associated with the source.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      name: str  # required,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_chunk_size: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      instructions: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Folder
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `name` | str | Yes | - |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_chunk_size` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `instructions` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete a data folder.

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      folder_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `folder_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List all data folders created by a user.

Args:
  after: Folder ID cursor for pagination. Returns folders that come after this folder ID
      in the specified sort order

  before: Folder ID cursor for pagination. Returns folders that come before this folder ID
      in the specified sort order

  limit: Maximum number of folders to return

  name: Folder name to filter by

  order: Sort order for folders by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Folder]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get a folder by ID

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      folder_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Folder
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `folder_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update the name or documentation of an existing data folder.

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  description: The description of the source.

  embedding_config: Configuration for embedding model connection and processing parameters.

  instructions: Instructions for how to use the source.

  metadata: Metadata associated with the source.

  name: The name of the source.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      folder_id: str  # required,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      instructions: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Folder
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `folder_id` | str | Yes | - |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `instructions` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.folders.with_streaming_response`

  #### create()

  Create a new data folder.

Args:
  name: The name of the source.

  description: The description of the source.

  embedding: The handle for the embedding config used by the source.

  embedding_chunk_size: The chunk size of the embedding.

  embedding_config: Configuration for embedding model connection and processing parameters.

  instructions: Instructions for how to use the source.

  metadata: Metadata associated with the source.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      name: str  # required,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_chunk_size: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      instructions: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Folder
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `name` | str | Yes | - |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_chunk_size` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `instructions` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete a data folder.

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      folder_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `folder_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  List all data folders created by a user.

Args:
  after: Folder ID cursor for pagination. Returns folders that come after this folder ID
      in the specified sort order

  before: Folder ID cursor for pagination. Returns folders that come before this folder ID
      in the specified sort order

  limit: Maximum number of folders to return

  name: Folder name to filter by

  order: Sort order for folders by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Folder]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get a folder by ID

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      folder_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Folder
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `folder_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update the name or documentation of an existing data folder.

Args:
  folder_id: The ID of the source in the format 'source-<uuid4>'

  description: The description of the source.

  embedding_config: Configuration for embedding model connection and processing parameters.

  instructions: Instructions for how to use the source.

  metadata: Metadata associated with the source.

  name: The name of the source.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      folder_id: str  # required,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      embedding_config: Optional[EmbeddingConfigParam] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      instructions: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Folder
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `folder_id` | str | Yes | - |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `embedding_config` | Optional[EmbeddingConfigParam] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `instructions` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Groups

Access via `client.groups`

#### create()

Create a new multi-agent group with the specified configuration.

Args:
  agent_ids

  description

  hidden: If set to True, the group will be hidden.

  manager_config

  project_id: The associated project id.

  shared_block_ids

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
create(
    agent_ids: SequenceNotStr[str]  # required,
    description: str  # required,
    hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    manager_config: group_create_params.ManagerConfig | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    shared_block_ids: SequenceNotStr[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Group
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `agent_ids` | SequenceNotStr[str] | Yes | - |
| `description` | str | Yes | - |
| `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `manager_config` | group_create_params.ManagerConfig | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `shared_block_ids` | SequenceNotStr[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### delete()

Delete a multi-agent group.

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
delete(
    group_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> object
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `group_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### list()

Fetch all multi-agent groups matching query.

Args:
  after: Group ID cursor for pagination. Returns groups that come after this group ID in
      the specified sort order

  before: Group ID cursor for pagination. Returns groups that come before this group ID in
      the specified sort order

  limit: Maximum number of groups to return

  manager_type: Search groups by manager type

  order: Sort order for groups by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  project_id: Search groups by project id

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    manager_type: Optional[ManagerType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> SyncArrayPage[Group]
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `manager_type` | Optional[ManagerType] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### retrieve()

Retrieve the group by id.

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
retrieve(
    group_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Group
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `group_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### update()

Create a new multi-agent group with the specified configuration.

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  agent_ids

  description

  manager_config

  project_id: The associated project id.

  shared_block_ids

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
update(
    group_id: str  # required,
    agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    manager_config: Optional[group_update_params.ManagerConfig] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    shared_block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Group
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `group_id` | str | Yes | - |
| `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `manager_config` | Optional[group_update_params.ManagerConfig] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `shared_block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### messages

Sub-resource: `client.groups.messages`

  #### create()

  Process a user message and return the group's response.

This endpoint accepts a
message from a user and processes it through through agents in the group based
on the specified pattern

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  assistant_message_tool_kwarg: The name of the message argument in the designated message tool. Still supported
      for legacy agent types, but deprecated for letta_v1_agent onward.

  assistant_message_tool_name: The name of the designated message tool. Still supported for legacy agent types,
      but deprecated for letta_v1_agent onward.

  client_tools: Client-side tools that the agent can call. When the agent calls a client-side
      tool, execution pauses and returns control to the client to execute the tool and
      provide the result via a ToolReturn.

  enable_thinking: If set to True, enables reasoning before responses or tool calls from the agent.

  include_return_message_types: Only return specified message types in the response. If `None` (default) returns
      all messages.

  input:
      Syntactic sugar for a single user message. Equivalent to messages=[{'role':
      'user', 'content': input}].

  max_steps: Maximum number of steps the agent should take to process the request.

  messages: The messages to be sent to the agent.

  use_assistant_message: Whether the server should parse specific tool call arguments (default
      `send_message`) as `AssistantMessage` objects. Still supported for legacy agent
      types, but deprecated for letta_v1_agent onward.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      group_id: str  # required,
      assistant_message_tool_kwarg: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      assistant_message_tool_name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      client_tools: Optional[Iterable[message_create_params.ClientTool]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_thinking: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_return_message_types: Optional[List[MessageType]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      input: Union[str, Iterable[message_create_params.InputUnionMember1], None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_steps: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      messages: Optional[Iterable[message_create_params.Message]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      use_assistant_message: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> LettaResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `group_id` | str | Yes | - |
  | `assistant_message_tool_kwarg` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `assistant_message_tool_name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `client_tools` | Optional[Iterable[message_create_params.ClientTool]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_thinking` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_return_message_types` | Optional[List[MessageType]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `input` | Union[str, Iterable[message_create_params.InputUnionMembe... | No | <letta_client.Omit object at 0x000002... |
  | `max_steps` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `messages` | Optional[Iterable[message_create_params.Message]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `use_assistant_message` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Retrieve message history for an agent.

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  after: Message ID cursor for pagination. Returns messages that come after this message
      ID in the specified sort order

  assistant_message_tool_kwarg: The name of the message argument.

  assistant_message_tool_name: The name of the designated message tool.

  before: Message ID cursor for pagination. Returns messages that come before this message
      ID in the specified sort order

  limit: Maximum number of messages to retrieve

  order: Sort order for messages by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  use_assistant_message: Whether to use assistant messages

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      group_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      assistant_message_tool_kwarg: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      assistant_message_tool_name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      use_assistant_message: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Message]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `group_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `assistant_message_tool_kwarg` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `assistant_message_tool_name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `use_assistant_message` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### reset()

  Delete the group messages for all agents that are part of the multi-agent group.

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  reset(
      group_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `group_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### stream()

  Process a user message and return the group's responses.

This endpoint accepts a
message from a user and processes it through agents in the group based on the
specified pattern. It will stream the steps of the response always, and stream
the tokens if 'stream_tokens' is set to True.

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  assistant_message_tool_kwarg: The name of the message argument in the designated message tool. Still supported
      for legacy agent types, but deprecated for letta_v1_agent onward.

  assistant_message_tool_name: The name of the designated message tool. Still supported for legacy agent types,
      but deprecated for letta_v1_agent onward.

  background: Whether to process the request in the background (only used when
      streaming=true).

  client_tools: Client-side tools that the agent can call. When the agent calls a client-side
      tool, execution pauses and returns control to the client to execute the tool and
      provide the result via a ToolReturn.

  enable_thinking: If set to True, enables reasoning before responses or tool calls from the agent.

  include_pings: Whether to include periodic keepalive ping messages in the stream to prevent
      connection timeouts (only used when streaming=true).

  include_return_message_types: Only return specified message types in the response. If `None` (default) returns
      all messages.

  input:
      Syntactic sugar for a single user message. Equivalent to messages=[{'role':
      'user', 'content': input}].

  max_steps: Maximum number of steps the agent should take to process the request.

  messages: The messages to be sent to the agent.

  stream_tokens: Flag to determine if individual tokens should be streamed, rather than streaming
      per step (only used when streaming=true).

  streaming: If True, returns a streaming response (Server-Sent Events). If False (default),
      returns a complete response.

  use_assistant_message: Whether the server should parse specific tool call arguments (default
      `send_message`) as `AssistantMessage` objects. Still supported for legacy agent
      types, but deprecated for letta_v1_agent onward.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  stream(
      group_id: str  # required,
      assistant_message_tool_kwarg: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      assistant_message_tool_name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      background: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      client_tools: Optional[Iterable[message_stream_params.ClientTool]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_thinking: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_pings: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_return_message_types: Optional[List[MessageType]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      input: Union[str, Iterable[message_stream_params.InputUnionMember1], None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      max_steps: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      messages: Optional[Iterable[message_stream_params.Message]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      stream_tokens: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      streaming: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      use_assistant_message: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Stream[LettaStreamingResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `group_id` | str | Yes | - |
  | `assistant_message_tool_kwarg` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `assistant_message_tool_name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `background` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `client_tools` | Optional[Iterable[message_stream_params.ClientTool]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_thinking` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_pings` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_return_message_types` | Optional[List[MessageType]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `input` | Union[str, Iterable[message_stream_params.InputUnionMembe... | No | <letta_client.Omit object at 0x000002... |
  | `max_steps` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `messages` | Optional[Iterable[message_stream_params.Message]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `stream_tokens` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `streaming` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `use_assistant_message` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  ```python
  update(
      message_id: str  # required,
      group_id: str  # required,
      content: str | Union[Iterable[LettaUserMessageContentUnionParam], str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      message_type: Literal['system_message'] | Literal['user_message'] | Literal['reasoning_message'] | Literal['assistant_message'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      reasoning: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> MessageUpdateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `message_id` | str | Yes | - |
  | `group_id` | str | Yes | - |
  | `content` | str | Union[Iterable[LettaUserMessageContentUnionParam], ... | No | <letta_client.Omit object at 0x000002... |
  | `message_type` | Literal['system_message'] | Literal['user_message'] | Lit... | No | <letta_client.Omit object at 0x000002... |
  | `reasoning` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.groups.with_raw_response`

  #### create()

  Create a new multi-agent group with the specified configuration.

Args:
  agent_ids

  description

  hidden: If set to True, the group will be hidden.

  manager_config

  project_id: The associated project id.

  shared_block_ids

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      agent_ids: SequenceNotStr[str]  # required,
      description: str  # required,
      hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      manager_config: group_create_params.ManagerConfig | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      shared_block_ids: SequenceNotStr[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Group
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_ids` | SequenceNotStr[str] | Yes | - |
  | `description` | str | Yes | - |
  | `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `manager_config` | group_create_params.ManagerConfig | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `shared_block_ids` | SequenceNotStr[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete a multi-agent group.

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      group_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `group_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Fetch all multi-agent groups matching query.

Args:
  after: Group ID cursor for pagination. Returns groups that come after this group ID in
      the specified sort order

  before: Group ID cursor for pagination. Returns groups that come before this group ID in
      the specified sort order

  limit: Maximum number of groups to return

  manager_type: Search groups by manager type

  order: Sort order for groups by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  project_id: Search groups by project id

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      manager_type: Optional[ManagerType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Group]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `manager_type` | Optional[ManagerType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve the group by id.

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      group_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Group
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `group_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Create a new multi-agent group with the specified configuration.

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  agent_ids

  description

  manager_config

  project_id: The associated project id.

  shared_block_ids

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      group_id: str  # required,
      agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      manager_config: Optional[group_update_params.ManagerConfig] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      shared_block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Group
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `group_id` | str | Yes | - |
  | `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `manager_config` | Optional[group_update_params.ManagerConfig] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `shared_block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.groups.with_streaming_response`

  #### create()

  Create a new multi-agent group with the specified configuration.

Args:
  agent_ids

  description

  hidden: If set to True, the group will be hidden.

  manager_config

  project_id: The associated project id.

  shared_block_ids

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      agent_ids: SequenceNotStr[str]  # required,
      description: str  # required,
      hidden: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      manager_config: group_create_params.ManagerConfig | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      shared_block_ids: SequenceNotStr[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Group
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_ids` | SequenceNotStr[str] | Yes | - |
  | `description` | str | Yes | - |
  | `hidden` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `manager_config` | group_create_params.ManagerConfig | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `shared_block_ids` | SequenceNotStr[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete a multi-agent group.

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      group_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `group_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Fetch all multi-agent groups matching query.

Args:
  after: Group ID cursor for pagination. Returns groups that come after this group ID in
      the specified sort order

  before: Group ID cursor for pagination. Returns groups that come before this group ID in
      the specified sort order

  limit: Maximum number of groups to return

  manager_type: Search groups by manager type

  order: Sort order for groups by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  project_id: Search groups by project id

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      manager_type: Optional[ManagerType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Group]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `manager_type` | Optional[ManagerType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Retrieve the group by id.

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      group_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Group
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `group_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Create a new multi-agent group with the specified configuration.

Args:
  group_id: The ID of the group in the format 'group-<uuid4>'

  agent_ids

  description

  manager_config

  project_id: The associated project id.

  shared_block_ids

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      group_id: str  # required,
      agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      manager_config: Optional[group_update_params.ManagerConfig] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      shared_block_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Group
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `group_id` | str | Yes | - |
  | `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `manager_config` | Optional[group_update_params.ManagerConfig] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `shared_block_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Mcp_servers

Access via `client.mcp_servers`

#### create()

Add a new MCP server to the Letta MCP server config

Args:
  config: The MCP server configuration (Stdio, SSE, or Streamable HTTP)

  server_name: The name of the MCP server

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
create(
    config: mcp_server_create_params.Config  # required,
    server_name: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> McpServerCreateResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `config` | mcp_server_create_params.Config | Yes | - |
| `server_name` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### delete()

Delete an MCP server by its ID

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
delete(
    mcp_server_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> None
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `mcp_server_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### list()

Get a list of all configured MCP servers

```python
list(
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> McpServerListResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### refresh()

Refresh tools for an MCP server by:

1.

Fetching current tools from the MCP server
2. Deleting tools that no longer exist on the server
3. Updating schemas for existing tools
4. Adding new tools from the server

Returns a summary of changes made.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
refresh(
    mcp_server_id: str  # required,
    agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> object
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `mcp_server_id` | str | Yes | - |
| `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### retrieve()

Get a specific MCP server

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
retrieve(
    mcp_server_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> McpServerRetrieveResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `mcp_server_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### update()

Update an existing MCP server configuration

Args:
  config: The MCP server configuration updates (Stdio, SSE, or Streamable HTTP)

  server_name: The name of the MCP server

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
update(
    mcp_server_id: str  # required,
    config: mcp_server_update_params.Config  # required,
    server_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> McpServerUpdateResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `mcp_server_id` | str | Yes | - |
| `config` | mcp_server_update_params.Config | Yes | - |
| `server_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### tools

Sub-resource: `client.mcp_servers.tools`

  #### list()

  Get a list of all tools for a specific MCP server

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      mcp_server_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ToolListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `mcp_server_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get a specific MCP tool by its ID

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      tool_id: str  # required,
      mcp_server_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Tool
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `tool_id` | str | Yes | - |
  | `mcp_server_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### run()

  Execute a specific MCP tool

The request body should contain the tool arguments in the ToolExecuteRequest
format.

Args:
  args: Arguments to pass to the tool

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  run(
      tool_id: str  # required,
      mcp_server_id: str  # required,
      args: Dict[str, object] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ToolExecutionResult
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `tool_id` | str | Yes | - |
  | `mcp_server_id` | str | Yes | - |
  | `args` | Dict[str, object] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.mcp_servers.with_raw_response`

  #### create()

  Add a new MCP server to the Letta MCP server config

Args:
  config: The MCP server configuration (Stdio, SSE, or Streamable HTTP)

  server_name: The name of the MCP server

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      config: mcp_server_create_params.Config  # required,
      server_name: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> McpServerCreateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `config` | mcp_server_create_params.Config | Yes | - |
  | `server_name` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete an MCP server by its ID

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      mcp_server_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> None
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `mcp_server_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get a list of all configured MCP servers

  ```python
  list(
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> McpServerListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### refresh()

  Refresh tools for an MCP server by:

1.

Fetching current tools from the MCP server
2. Deleting tools that no longer exist on the server
3. Updating schemas for existing tools
4. Adding new tools from the server

Returns a summary of changes made.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  refresh(
      mcp_server_id: str  # required,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `mcp_server_id` | str | Yes | - |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get a specific MCP server

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      mcp_server_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> McpServerRetrieveResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `mcp_server_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update an existing MCP server configuration

Args:
  config: The MCP server configuration updates (Stdio, SSE, or Streamable HTTP)

  server_name: The name of the MCP server

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      mcp_server_id: str  # required,
      config: mcp_server_update_params.Config  # required,
      server_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> McpServerUpdateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `mcp_server_id` | str | Yes | - |
  | `config` | mcp_server_update_params.Config | Yes | - |
  | `server_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.mcp_servers.with_streaming_response`

  #### create()

  Add a new MCP server to the Letta MCP server config

Args:
  config: The MCP server configuration (Stdio, SSE, or Streamable HTTP)

  server_name: The name of the MCP server

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      config: mcp_server_create_params.Config  # required,
      server_name: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> McpServerCreateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `config` | mcp_server_create_params.Config | Yes | - |
  | `server_name` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete an MCP server by its ID

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      mcp_server_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> None
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `mcp_server_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get a list of all configured MCP servers

  ```python
  list(
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> McpServerListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### refresh()

  Refresh tools for an MCP server by:

1.

Fetching current tools from the MCP server
2. Deleting tools that no longer exist on the server
3. Updating schemas for existing tools
4. Adding new tools from the server

Returns a summary of changes made.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  refresh(
      mcp_server_id: str  # required,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `mcp_server_id` | str | Yes | - |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get a specific MCP server

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      mcp_server_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> McpServerRetrieveResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `mcp_server_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update an existing MCP server configuration

Args:
  config: The MCP server configuration updates (Stdio, SSE, or Streamable HTTP)

  server_name: The name of the MCP server

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      mcp_server_id: str  # required,
      config: mcp_server_update_params.Config  # required,
      server_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> McpServerUpdateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `mcp_server_id` | str | Yes | - |
  | `config` | mcp_server_update_params.Config | Yes | - |
  | `server_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Messages

Access via `client.messages`

#### list()

List messages across all agents for the current user.

Args:
  after: Message ID cursor for pagination. Returns messages that come after this message
      ID in the specified sort order

  before: Message ID cursor for pagination. Returns messages that come before this message
      ID in the specified sort order

  conversation_id: Conversation ID to filter messages by

  limit: Maximum number of messages to return

  order: Sort order for messages by creation time. 'asc' for oldest first, 'desc' for
      newest first

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    conversation_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> MessageListResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `conversation_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### search()

Search messages across the organization with optional agent filtering.

Returns
messages with FTS/vector ranks and total RRF score.

This is a cloud-only feature.

Args:
  query: Text query for full-text search

  agent_id: Filter messages by agent ID

  conversation_id: Filter messages by conversation ID

  end_date: Filter messages created on or before this date

  limit: Maximum number of results to return

  search_mode: Search mode to use

  start_date: Filter messages created after this date

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
search(
    query: str  # required,
    agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    conversation_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    end_date: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    search_mode: Literal['vector', 'fts', 'hybrid'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    start_date: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> MessageSearchResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `query` | str | Yes | - |
| `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `conversation_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `end_date` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
| `search_mode` | Literal['vector', 'fts', 'hybrid'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `start_date` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.messages.with_raw_response`

  #### list()

  List messages across all agents for the current user.

Args:
  after: Message ID cursor for pagination. Returns messages that come after this message
      ID in the specified sort order

  before: Message ID cursor for pagination. Returns messages that come before this message
      ID in the specified sort order

  conversation_id: Conversation ID to filter messages by

  limit: Maximum number of messages to return

  order: Sort order for messages by creation time. 'asc' for oldest first, 'desc' for
      newest first

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      conversation_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> MessageListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `conversation_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### search()

  Search messages across the organization with optional agent filtering.

Returns
messages with FTS/vector ranks and total RRF score.

This is a cloud-only feature.

Args:
  query: Text query for full-text search

  agent_id: Filter messages by agent ID

  conversation_id: Filter messages by conversation ID

  end_date: Filter messages created on or before this date

  limit: Maximum number of results to return

  search_mode: Search mode to use

  start_date: Filter messages created after this date

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  search(
      query: str  # required,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      conversation_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      end_date: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      search_mode: Literal['vector', 'fts', 'hybrid'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      start_date: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> MessageSearchResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `query` | str | Yes | - |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `conversation_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `end_date` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `search_mode` | Literal['vector', 'fts', 'hybrid'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `start_date` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.messages.with_streaming_response`

  #### list()

  List messages across all agents for the current user.

Args:
  after: Message ID cursor for pagination. Returns messages that come after this message
      ID in the specified sort order

  before: Message ID cursor for pagination. Returns messages that come before this message
      ID in the specified sort order

  conversation_id: Conversation ID to filter messages by

  limit: Maximum number of messages to return

  order: Sort order for messages by creation time. 'asc' for oldest first, 'desc' for
      newest first

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      conversation_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> MessageListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `conversation_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### search()

  Search messages across the organization with optional agent filtering.

Returns
messages with FTS/vector ranks and total RRF score.

This is a cloud-only feature.

Args:
  query: Text query for full-text search

  agent_id: Filter messages by agent ID

  conversation_id: Filter messages by conversation ID

  end_date: Filter messages created on or before this date

  limit: Maximum number of results to return

  search_mode: Search mode to use

  start_date: Filter messages created after this date

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  search(
      query: str  # required,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      conversation_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      end_date: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      search_mode: Literal['vector', 'fts', 'hybrid'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      start_date: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> MessageSearchResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `query` | str | Yes | - |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `conversation_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `end_date` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `search_mode` | Literal['vector', 'fts', 'hybrid'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `start_date` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Models

Access via `client.models`

#### list()

List available LLM models using the asynchronous implementation for improved
performance.

Returns Model format which extends LLMConfig with additional metadata fields.
Legacy LLMConfig fields are marked as deprecated but still available for
backward compatibility.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    provider_category: Optional[List[ProviderCategory]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    provider_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    provider_type: Optional[ProviderType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> ModelListResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `provider_category` | Optional[List[ProviderCategory]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `provider_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `provider_type` | Optional[ProviderType] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### embeddings

Sub-resource: `client.models.embeddings`

  #### list()

  List available embedding models using the asynchronous implementation for
improved performance.

Returns EmbeddingModel format which extends EmbeddingConfig with additional
metadata fields. Legacy EmbeddingConfig fields are marked as deprecated but
still available for backward compatibility.

  ```python
  list(
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> EmbeddingListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.models.with_raw_response`

  #### list()

  List available LLM models using the asynchronous implementation for improved
performance.

Returns Model format which extends LLMConfig with additional metadata fields.
Legacy LLMConfig fields are marked as deprecated but still available for
backward compatibility.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      provider_category: Optional[List[ProviderCategory]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      provider_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      provider_type: Optional[ProviderType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ModelListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `provider_category` | Optional[List[ProviderCategory]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `provider_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `provider_type` | Optional[ProviderType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.models.with_streaming_response`

  #### list()

  List available LLM models using the asynchronous implementation for improved
performance.

Returns Model format which extends LLMConfig with additional metadata fields.
Legacy LLMConfig fields are marked as deprecated but still available for
backward compatibility.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      provider_category: Optional[List[ProviderCategory]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      provider_name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      provider_type: Optional[ProviderType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ModelListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `provider_category` | Optional[List[ProviderCategory]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `provider_name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `provider_type` | Optional[ProviderType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Passages

Access via `client.passages`

#### search()

Search passages across the organization with optional agent and archive
filtering. Returns passages with relevance scores.

This endpoint supports semantic search through passages:

- If neither agent_id nor archive_id is provided, searches ALL passages in the
  organization
- If agent_id is provided, searches passages across all archives attached to
  that agent
- If archive_id is provided, searches passages within that specific archive
- If both are provided, agent_id takes precedence

Args:
  query: Text query for semantic search

  agent_id: Filter passages by agent ID

  archive_id: Filter passages by archive ID

  end_date: Filter results to passages created before this datetime

  limit: Maximum number of results to return

  start_date: Filter results to passages created after this datetime

  tag_match_mode: How to match tags - 'any' to match passages with any of the tags, 'all' to match
      only passages with all tags

  tags: Optional list of tags to filter search results

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
search(
    query: str  # required,
    agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    archive_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    end_date: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    start_date: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tag_match_mode: Literal['any', 'all'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> PassageSearchResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `query` | str | Yes | - |
| `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `archive_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `end_date` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
| `start_date` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tag_match_mode` | Literal['any', 'all'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.passages.with_raw_response`

  #### search()

  Search passages across the organization with optional agent and archive
filtering. Returns passages with relevance scores.

This endpoint supports semantic search through passages:

- If neither agent_id nor archive_id is provided, searches ALL passages in the
  organization
- If agent_id is provided, searches passages across all archives attached to
  that agent
- If archive_id is provided, searches passages within that specific archive
- If both are provided, agent_id takes precedence

Args:
  query: Text query for semantic search

  agent_id: Filter passages by agent ID

  archive_id: Filter passages by archive ID

  end_date: Filter results to passages created before this datetime

  limit: Maximum number of results to return

  start_date: Filter results to passages created after this datetime

  tag_match_mode: How to match tags - 'any' to match passages with any of the tags, 'all' to match
      only passages with all tags

  tags: Optional list of tags to filter search results

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  search(
      query: str  # required,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      archive_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      end_date: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      start_date: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tag_match_mode: Literal['any', 'all'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> PassageSearchResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `query` | str | Yes | - |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `archive_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `end_date` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `start_date` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tag_match_mode` | Literal['any', 'all'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.passages.with_streaming_response`

  #### search()

  Search passages across the organization with optional agent and archive
filtering. Returns passages with relevance scores.

This endpoint supports semantic search through passages:

- If neither agent_id nor archive_id is provided, searches ALL passages in the
  organization
- If agent_id is provided, searches passages across all archives attached to
  that agent
- If archive_id is provided, searches passages within that specific archive
- If both are provided, agent_id takes precedence

Args:
  query: Text query for semantic search

  agent_id: Filter passages by agent ID

  archive_id: Filter passages by archive ID

  end_date: Filter results to passages created before this datetime

  limit: Maximum number of results to return

  start_date: Filter results to passages created after this datetime

  tag_match_mode: How to match tags - 'any' to match passages with any of the tags, 'all' to match
      only passages with all tags

  tags: Optional list of tags to filter search results

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  search(
      query: str  # required,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      archive_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      end_date: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      start_date: Union[str, datetime, None] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tag_match_mode: Literal['any', 'all'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> PassageSearchResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `query` | str | Yes | - |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `archive_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `end_date` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `start_date` | Union[str, datetime, None] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tag_match_mode` | Literal['any', 'all'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Runs

Access via `client.runs`

#### list()

List all runs.

Args:
  active: Filter for active runs.

  after: Run ID cursor for pagination. Returns runs that come after this run ID in the
      specified sort order

  agent_id: The unique identifier of the agent associated with the run.

  agent_ids: The unique identifiers of the agents associated with the run. Deprecated in
      favor of agent_id field.

  ascending: Whether to sort agents oldest to newest (True) or newest to oldest (False,
      default). Deprecated in favor of order field.

  background: If True, filters for runs that were created in background mode.

  before: Run ID cursor for pagination. Returns runs that come before this run ID in the
      specified sort order

  conversation_id: Filter runs by conversation ID.

  limit: Maximum number of runs to return

  order: Sort order for runs by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  statuses: Filter runs by status. Can specify multiple statuses.

  stop_reason: Filter runs by stop reason.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    active: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    ascending: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    background: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    conversation_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    statuses: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    stop_reason: Optional[StopReasonType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> SyncArrayPage[Run]
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `active` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `ascending` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `background` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `conversation_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `statuses` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `stop_reason` | Optional[StopReasonType] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### retrieve()

Get the status of a run.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
retrieve(
    run_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Run
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `run_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### messages

Sub-resource: `client.runs.messages`

  #### list()

  Get response messages associated with a run.

Args:
  after: Message ID cursor for pagination. Returns messages that come after this message
      ID in the specified sort order

  before: Message ID cursor for pagination. Returns messages that come before this message
      ID in the specified sort order

  limit: Maximum number of messages to return

  order: Sort order for messages by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      run_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Message]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `run_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### stream()

  Retrieve Stream For Run

Args:
  batch_size: Number of entries to read per batch.

  include_pings: Whether to include periodic keepalive ping messages in the stream to prevent
      connection timeouts.

  poll_interval: Seconds to wait between polls when no new data.

  starting_after: Sequence id to use as a cursor for pagination. Response will start streaming
      after this chunk sequence id

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  stream(
      run_id: str  # required,
      batch_size: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      include_pings: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      poll_interval: Optional[float] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      starting_after: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Stream[LettaStreamingResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `run_id` | str | Yes | - |
  | `batch_size` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `include_pings` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `poll_interval` | Optional[float] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `starting_after` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### steps

Sub-resource: `client.runs.steps`

  #### list()

  Get steps associated with a run with filtering options.

Args:
  after: Cursor for pagination

  before: Cursor for pagination

  limit: Maximum number of messages to return

  order: Sort order for steps by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      run_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Step]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `run_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### usage

Sub-resource: `client.runs.usage`

  #### retrieve()

  Get usage statistics for a run.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      run_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> UsageRetrieveResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `run_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.runs.with_raw_response`

  #### list()

  List all runs.

Args:
  active: Filter for active runs.

  after: Run ID cursor for pagination. Returns runs that come after this run ID in the
      specified sort order

  agent_id: The unique identifier of the agent associated with the run.

  agent_ids: The unique identifiers of the agents associated with the run. Deprecated in
      favor of agent_id field.

  ascending: Whether to sort agents oldest to newest (True) or newest to oldest (False,
      default). Deprecated in favor of order field.

  background: If True, filters for runs that were created in background mode.

  before: Run ID cursor for pagination. Returns runs that come before this run ID in the
      specified sort order

  conversation_id: Filter runs by conversation ID.

  limit: Maximum number of runs to return

  order: Sort order for runs by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  statuses: Filter runs by status. Can specify multiple statuses.

  stop_reason: Filter runs by stop reason.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      active: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      ascending: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      background: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      conversation_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      statuses: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      stop_reason: Optional[StopReasonType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Run]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `active` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `ascending` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `background` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `conversation_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `statuses` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `stop_reason` | Optional[StopReasonType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get the status of a run.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      run_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Run
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `run_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.runs.with_streaming_response`

  #### list()

  List all runs.

Args:
  active: Filter for active runs.

  after: Run ID cursor for pagination. Returns runs that come after this run ID in the
      specified sort order

  agent_id: The unique identifier of the agent associated with the run.

  agent_ids: The unique identifiers of the agents associated with the run. Deprecated in
      favor of agent_id field.

  ascending: Whether to sort agents oldest to newest (True) or newest to oldest (False,
      default). Deprecated in favor of order field.

  background: If True, filters for runs that were created in background mode.

  before: Run ID cursor for pagination. Returns runs that come before this run ID in the
      specified sort order

  conversation_id: Filter runs by conversation ID.

  limit: Maximum number of runs to return

  order: Sort order for runs by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  statuses: Filter runs by status. Can specify multiple statuses.

  stop_reason: Filter runs by stop reason.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      active: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      agent_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      ascending: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      background: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      conversation_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      statuses: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      stop_reason: Optional[StopReasonType] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Run]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `active` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `agent_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `ascending` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `background` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `conversation_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `statuses` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `stop_reason` | Optional[StopReasonType] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get the status of a run.

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      run_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Run
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `run_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Steps

Access via `client.steps`

#### list()

List steps with optional pagination and date filters.

Args:
  after: Return steps after this step ID

  agent_id: Filter by the ID of the agent that performed the step

  before: Return steps before this step ID

  end_date: Return steps before this ISO datetime (e.g. "2025-01-29T15:01:19-08:00")

  feedback: Filter by feedback

  has_feedback: Filter by whether steps have feedback (true) or not (false)

  limit: Maximum number of steps to return

  model: Filter by the name of the model used for the step

  order: Sort order for steps by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  project_id: Filter by the project ID that is associated with the step (cloud only).

  start_date: Return steps after this ISO datetime (e.g. "2025-01-29T15:01:19-08:00")

  tags: Filter by tags

  trace_ids: Filter by trace ids returned by the server

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    end_date: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    feedback: Optional[Literal['positive', 'negative']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    has_feedback: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    model: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    start_date: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    trace_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> SyncArrayPage[Step]
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `end_date` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `feedback` | Optional[Literal['positive', 'negative']] | Omit | No | <letta_client.Omit object at 0x000002... |
| `has_feedback` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `model` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `start_date` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `trace_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### retrieve()

Get a step by ID.

Args:
  step_id: The ID of the step in the format 'step-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
retrieve(
    step_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Step
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `step_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### feedback

Sub-resource: `client.steps.feedback`

  #### create()

  Modify feedback for a given step.

Args:
  step_id: The ID of the step in the format 'step-<uuid4>'

  feedback: Whether this feedback is positive or negative

  tags: Feedback tags to add to the step

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      step_id: str  # required,
      feedback: Optional[Literal['positive', 'negative']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Step
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `step_id` | str | Yes | - |
  | `feedback` | Optional[Literal['positive', 'negative']] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### messages

Sub-resource: `client.steps.messages`

  #### list()

  List messages for a given step.

Args:
  step_id: The ID of the step in the format 'step-<uuid4>'

  after: Message ID cursor for pagination. Returns messages that come after this message
      ID in the specified sort order

  before: Message ID cursor for pagination. Returns messages that come before this message
      ID in the specified sort order

  limit: Maximum number of messages to return

  order: Sort order for messages by creation time. 'asc' for oldest first, 'desc' for
      newest first

  order_by: Sort by field

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      step_id: str  # required,
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[MessageListResponse]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `step_id` | str | Yes | - |
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### metrics

Sub-resource: `client.steps.metrics`

  #### retrieve()

  Get step metrics by step ID.

Args:
  step_id: The ID of the step in the format 'step-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      step_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> MetricRetrieveResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `step_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### trace

Sub-resource: `client.steps.trace`

  #### retrieve()

  Retrieve Trace For Step

Args:
  step_id: The ID of the step in the format 'step-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      step_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Optional[ProviderTrace]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `step_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.steps.with_raw_response`

  #### list()

  List steps with optional pagination and date filters.

Args:
  after: Return steps after this step ID

  agent_id: Filter by the ID of the agent that performed the step

  before: Return steps before this step ID

  end_date: Return steps before this ISO datetime (e.g. "2025-01-29T15:01:19-08:00")

  feedback: Filter by feedback

  has_feedback: Filter by whether steps have feedback (true) or not (false)

  limit: Maximum number of steps to return

  model: Filter by the name of the model used for the step

  order: Sort order for steps by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  project_id: Filter by the project ID that is associated with the step (cloud only).

  start_date: Return steps after this ISO datetime (e.g. "2025-01-29T15:01:19-08:00")

  tags: Filter by tags

  trace_ids: Filter by trace ids returned by the server

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      end_date: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      feedback: Optional[Literal['positive', 'negative']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      has_feedback: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      model: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      start_date: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      trace_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Step]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `end_date` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `feedback` | Optional[Literal['positive', 'negative']] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `has_feedback` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `model` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `start_date` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `trace_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get a step by ID.

Args:
  step_id: The ID of the step in the format 'step-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      step_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Step
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `step_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.steps.with_streaming_response`

  #### list()

  List steps with optional pagination and date filters.

Args:
  after: Return steps after this step ID

  agent_id: Filter by the ID of the agent that performed the step

  before: Return steps before this step ID

  end_date: Return steps before this ISO datetime (e.g. "2025-01-29T15:01:19-08:00")

  feedback: Filter by feedback

  has_feedback: Filter by whether steps have feedback (true) or not (false)

  limit: Maximum number of steps to return

  model: Filter by the name of the model used for the step

  order: Sort order for steps by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  project_id: Filter by the project ID that is associated with the step (cloud only).

  start_date: Return steps after this ISO datetime (e.g. "2025-01-29T15:01:19-08:00")

  tags: Filter by tags

  trace_ids: Filter by trace ids returned by the server

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      agent_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      end_date: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      feedback: Optional[Literal['positive', 'negative']] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      has_feedback: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      model: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      project_id: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      start_date: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      trace_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Step]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `agent_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `end_date` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `feedback` | Optional[Literal['positive', 'negative']] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `has_feedback` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `model` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `project_id` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `start_date` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `trace_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get a step by ID.

Args:
  step_id: The ID of the step in the format 'step-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      step_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Step
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `step_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Tags

Access via `client.tags`

#### list()

Get the list of all tags (from agents and blocks) that have been created.

Args:
  after: Tag cursor for pagination. Returns tags that come after this tag in the
      specified sort order

  before: Tag cursor for pagination. Returns tags that come before this tag in the
      specified sort order

  limit: Maximum number of tags to return

  name: Filter tags by name

  order: Sort order for tags. 'asc' for alphabetical order, 'desc' for reverse
      alphabetical order

  order_by: Field to sort by

  query_text: Filter tags by text search. Deprecated, please use name field instead

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order_by: Literal['name'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    query_text: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> TagListResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order_by` | Literal['name'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `query_text` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.tags.with_raw_response`

  #### list()

  Get the list of all tags (from agents and blocks) that have been created.

Args:
  after: Tag cursor for pagination. Returns tags that come after this tag in the
      specified sort order

  before: Tag cursor for pagination. Returns tags that come before this tag in the
      specified sort order

  limit: Maximum number of tags to return

  name: Filter tags by name

  order: Sort order for tags. 'asc' for alphabetical order, 'desc' for reverse
      alphabetical order

  order_by: Field to sort by

  query_text: Filter tags by text search. Deprecated, please use name field instead

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['name'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      query_text: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> TagListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['name'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `query_text` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.tags.with_streaming_response`

  #### list()

  Get the list of all tags (from agents and blocks) that have been created.

Args:
  after: Tag cursor for pagination. Returns tags that come after this tag in the
      specified sort order

  before: Tag cursor for pagination. Returns tags that come before this tag in the
      specified sort order

  limit: Maximum number of tags to return

  name: Filter tags by name

  order: Sort order for tags. 'asc' for alphabetical order, 'desc' for reverse
      alphabetical order

  order_by: Field to sort by

  query_text: Filter tags by text search. Deprecated, please use name field instead

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['name'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      query_text: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> TagListResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['name'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `query_text` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Templates

Access via `client.templates`

#### create()

```python
create(
    agent_id: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    type: Literal['agent'] | Literal['agent_file']  # required,
    name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    agent_file: Dict[str, Optional[object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    update_existing_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> TemplateCreateResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `agent_id` | str | Omit | No | <letta_client.Omit object at 0x000002... |
| `type` | Literal['agent'] | Literal['agent_file'] | Yes | - |
| `name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
| `agent_file` | Dict[str, Optional[object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `update_existing_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### delete()

Deletes all versions of a template with the specified name

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
delete(
    template_name: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> TemplateDeleteResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `template_name` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### update()

Updates the current working version of a template from an agent file

Args:
  agent_file_json: The agent file to update the current template version from

  save_existing_changes: If true, Letta will automatically save any changes as a version before updating
      the template

  update_existing_tools: If true, update existing custom tools source_code and json_schema (source_type
      cannot be changed)

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
update(
    template_name: str  # required,
    agent_file_json: Dict[str, Optional[object]]  # required,
    save_existing_changes: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    update_existing_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> TemplateUpdateResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `template_name` | str | Yes | - |
| `agent_file_json` | Dict[str, Optional[object]] | Yes | - |
| `save_existing_changes` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `update_existing_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### agents

Sub-resource: `client.templates.agents`

  #### create()

  Creates an Agent or multiple Agents from a template

Args:
  agent_name: The name of the agent, optional otherwise a random one will be assigned

  identity_ids: The identity ids to assign to the agent

  initial_message_sequence: Set an initial sequence of messages, if not provided, the agent will start with
      the default message sequence, if an empty array is provided, the agent will
      start with no messages

  memory_variables: The memory variables to assign to the agent

  tags: The tags to assign to the agent

  tool_variables: The tool variables to assign to the agent

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      template_version: str  # required,
      agent_name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      identity_ids: SequenceNotStr[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      initial_message_sequence: Iterable[agent_create_params.InitialMessageSequence] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      memory_variables: Dict[str, str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: SequenceNotStr[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_variables: Dict[str, str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> AgentCreateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `template_version` | str | Yes | - |
  | `agent_name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `identity_ids` | SequenceNotStr[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `initial_message_sequence` | Iterable[agent_create_params.InitialMessageSequence] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `memory_variables` | Dict[str, str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | SequenceNotStr[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_variables` | Dict[str, str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.templates.with_raw_response`

  #### create()

  ```python
  create(
      agent_id: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      type: Literal['agent'] | Literal['agent_file']  # required,
      name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      agent_file: Dict[str, Optional[object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      update_existing_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> TemplateCreateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `type` | Literal['agent'] | Literal['agent_file'] | Yes | - |
  | `name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `agent_file` | Dict[str, Optional[object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `update_existing_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Deletes all versions of a template with the specified name

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      template_name: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> TemplateDeleteResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `template_name` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Updates the current working version of a template from an agent file

Args:
  agent_file_json: The agent file to update the current template version from

  save_existing_changes: If true, Letta will automatically save any changes as a version before updating
      the template

  update_existing_tools: If true, update existing custom tools source_code and json_schema (source_type
      cannot be changed)

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      template_name: str  # required,
      agent_file_json: Dict[str, Optional[object]]  # required,
      save_existing_changes: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      update_existing_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> TemplateUpdateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `template_name` | str | Yes | - |
  | `agent_file_json` | Dict[str, Optional[object]] | Yes | - |
  | `save_existing_changes` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `update_existing_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.templates.with_streaming_response`

  #### create()

  ```python
  create(
      agent_id: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      type: Literal['agent'] | Literal['agent_file']  # required,
      name: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      agent_file: Dict[str, Optional[object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      update_existing_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> TemplateCreateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `agent_id` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `type` | Literal['agent'] | Literal['agent_file'] | Yes | - |
  | `name` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `agent_file` | Dict[str, Optional[object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `update_existing_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Deletes all versions of a template with the specified name

Args:
  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      template_name: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> TemplateDeleteResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `template_name` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Updates the current working version of a template from an agent file

Args:
  agent_file_json: The agent file to update the current template version from

  save_existing_changes: If true, Letta will automatically save any changes as a version before updating
      the template

  update_existing_tools: If true, update existing custom tools source_code and json_schema (source_type
      cannot be changed)

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      template_name: str  # required,
      agent_file_json: Dict[str, Optional[object]]  # required,
      save_existing_changes: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      update_existing_tools: bool | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> TemplateUpdateResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `template_name` | str | Yes | - |
  | `agent_file_json` | Dict[str, Optional[object]] | Yes | - |
  | `save_existing_changes` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `update_existing_tools` | bool | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

### Tools

Access via `client.tools`

#### add()

Add a tool to Letta from a custom Tool class

Args:
  tool: The tool object to be added.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

Examples:
from letta_client import Letta

client = Letta(
    token="YOUR_TOKEN",
)

class InventoryItem(BaseModel):
    sku: str  # Unique product identifier
    name: str  # Product name
    price: float  # Current price
    category: str  # Product category (e.g., "Electronics", "Clothing")

class InventoryEntry(BaseModel):
    timestamp: int  # Unix timestamp of the transaction
    item: InventoryItem  # The product being updated
    transaction_id: str  # Unique identifier for this inventory update

class InventoryEntryData(BaseModel):
    data: InventoryEntry
    quantity_change: int  # Change in quantity (positive for additions, negative for removals)

class ManageInventoryTool(BaseTool):
    name: str = "manage_inventory"
    args_schema: Type[BaseModel] = InventoryEntryData
    description: str = "Update inventory catalogue with a new data entry"
    tags: List[str] = ["inventory", "shop"]

    def run(self, data: InventoryEntry, quantity_change: int) -> bool:
        '''
        Implementation of the manage_inventory tool
        '''
        print(f"Updated inventory for {data.item.name} with a quantity change of {quantity_change}")
        return True
        
client.tools.add(
    tool=ManageInventoryTool()
)

```python
add(
    tool: BaseTool  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Tool
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `tool` | BaseTool | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### create()

Create a new tool

Args:
  source_code: The source code of the function.

  args_json_schema: The args JSON schema of the function.

  default_requires_approval: Whether or not to require approval before executing this tool.

  description: The description of the tool.

  enable_parallel_execution: If set to True, then this tool will potentially be executed concurrently with
      other tools. Default False.

  json_schema: The JSON schema of the function (auto-generated from source_code if not
      provided)

  npm_requirements: Optional list of npm packages required by this tool.

  pip_requirements: Optional list of pip packages required by this tool.

  return_char_limit: The maximum number of characters in the response.

  source_type: The source type of the function.

  tags: Metadata tags.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
create(
    source_code: str  # required,
    args_json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    default_requires_approval: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    enable_parallel_execution: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    npm_requirements: Optional[Iterable[NpmRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    pip_requirements: Optional[Iterable[PipRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    return_char_limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    source_type: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Tool
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `source_code` | str | Yes | - |
| `args_json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `default_requires_approval` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `enable_parallel_execution` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `npm_requirements` | Optional[Iterable[NpmRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `pip_requirements` | Optional[Iterable[PipRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `return_char_limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
| `source_type` | str | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### create_from_function()

Create a new tool from a callable

Args:
  func: The callable to create the tool from.

  args_schema: The arguments schema of the function, as a Pydantic model.

  description: The description of the tool.

  tags: Metadata tags.

  source_type: The source type of the function.

  json_schema: The JSON schema of the function (auto-generated from source_code if not
      provided)

  return_char_limit: The maximum number of characters in the response.

  pip_requirements: Optional list of pip packages required by this tool.

  npm_requirements: Optional list of npm packages required by this tool.

  default_requires_approval: Whether or not to require approval before executing this tool.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

Examples:
from letta_client import Letta

client = Letta(
    token="YOUR_TOKEN",
)

def add_two_numbers(a: int, b: int) -> int:
    return a + b

client.tools.create_from_function(
    func=add_two_numbers,
)

class InventoryEntryData(BaseModel):
    data: InventoryEntry
    quantity_change: int

def manage_inventory(data: InventoryEntry, quantity_change: int) -> bool:
    pass

client.tools.create_from_function(
    func=manage_inventory,
    args_schema=InventoryEntryData,
)

```python
create_from_function(
    func: Callable[..., Any]  # required,
    args_schema: Optional[Type[BaseModel]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    source_type: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    return_char_limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    pip_requirements: Optional[Iterable[PipRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    npm_requirements: Optional[Iterable[NpmRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    default_requires_approval: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Tool
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `func` | Callable[..., Any] | Yes | - |
| `args_schema` | Optional[Type[BaseModel]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `source_type` | str | Omit | No | <letta_client.Omit object at 0x000002... |
| `json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `return_char_limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
| `pip_requirements` | Optional[Iterable[PipRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `npm_requirements` | Optional[Iterable[NpmRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `default_requires_approval` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### delete()

Delete a tool by name

Args:
  tool_id: The ID of the tool in the format 'tool-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
delete(
    tool_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> object
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `tool_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### list()

Get a list of all tools available to agents.

Args:
  after: Tool ID cursor for pagination. Returns tools that come after this tool ID in the
      specified sort order

  before: Tool ID cursor for pagination. Returns tools that come before this tool ID in
      the specified sort order

  exclude_tool_types: Tool type(s) to exclude - accepts repeated params or comma-separated values

  limit: Maximum number of tools to return

  name: Filter by single tool name

  names: Filter by specific tool names

  order: Sort order for tools by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  return_only_letta_tools: Return only tools with tool*type starting with 'letta*'

  search: Search tool names (case-insensitive partial match)

  tool_ids: Filter by specific tool IDs - accepts repeated params or comma-separated values

  tool_types: Filter by tool type(s) - accepts repeated params or comma-separated values

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
list(
    after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    exclude_tool_types: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    names: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    return_only_letta_tools: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tool_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tool_types: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> SyncArrayPage[Tool]
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `exclude_tool_types` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `names` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `return_only_letta_tools` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tool_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tool_types` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### retrieve()

Get a tool by ID

Args:
  tool_id: The ID of the tool in the format 'tool-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
retrieve(
    tool_id: str  # required,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Tool
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `tool_id` | str | Yes | - |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### search()

Search tools using semantic search.

Requires tool embedding to be enabled (embed_tools=True). Uses vector search,
full-text search, or hybrid mode to find tools matching the query.

Returns tools ranked by relevance with their search scores.

Args:
  limit: Maximum number of results to return.

  query: Text query for semantic search.

  search_mode: Search mode: vector, fts, or hybrid.

  tags: Filter by tags (match any).

  tool_types: Filter by tool types (e.g., 'custom', 'letta_core').

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
search(
    limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    query: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    search_mode: Literal['vector', 'fts', 'hybrid'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tool_types: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> ToolSearchResponse
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
| `query` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `search_mode` | Literal['vector', 'fts', 'hybrid'] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tool_types` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### update()

Update an existing tool

Args:
  tool_id: The ID of the tool in the format 'tool-<uuid4>'

  args_json_schema: The args JSON schema of the function.

  default_requires_approval: Whether or not to require approval before executing this tool.

  description: The description of the tool.

  enable_parallel_execution: If set to True, then this tool will potentially be executed concurrently with
      other tools. Default False.

  json_schema: The JSON schema of the function (auto-generated from source_code if not
      provided)

  metadata: A dictionary of additional metadata for the tool.

  npm_requirements: Optional list of npm packages required by this tool.

  pip_requirements: Optional list of pip packages required by this tool.

  return_char_limit: The maximum number of characters in the response.

  source_code: The source code of the function.

  source_type: The type of the source code.

  tags: Metadata tags.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
update(
    tool_id: str  # required,
    args_json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    default_requires_approval: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    enable_parallel_execution: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    npm_requirements: Optional[Iterable[NpmRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    pip_requirements: Optional[Iterable[PipRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    return_char_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    source_code: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    source_type: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Tool
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `tool_id` | str | Yes | - |
| `args_json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `default_requires_approval` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `enable_parallel_execution` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `npm_requirements` | Optional[Iterable[NpmRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `pip_requirements` | Optional[Iterable[PipRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `return_char_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
| `source_code` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `source_type` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### upsert()

Create or update a tool

Args:
  source_code: The source code of the function.

  args_json_schema: The args JSON schema of the function.

  default_requires_approval: Whether or not to require approval before executing this tool.

  description: The description of the tool.

  enable_parallel_execution: If set to True, then this tool will potentially be executed concurrently with
      other tools. Default False.

  json_schema: The JSON schema of the function (auto-generated from source_code if not
      provided)

  npm_requirements: Optional list of npm packages required by this tool.

  pip_requirements: Optional list of pip packages required by this tool.

  return_char_limit: The maximum number of characters in the response.

  source_type: The source type of the function.

  tags: Metadata tags.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

```python
upsert(
    source_code: str  # required,
    args_json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    default_requires_approval: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    enable_parallel_execution: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    npm_requirements: Optional[Iterable[NpmRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    pip_requirements: Optional[Iterable[PipRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    return_char_limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    source_type: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Tool
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `source_code` | str | Yes | - |
| `args_json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `default_requires_approval` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `enable_parallel_execution` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `npm_requirements` | Optional[Iterable[NpmRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `pip_requirements` | Optional[Iterable[PipRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `return_char_limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
| `source_type` | str | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### upsert_from_function()

Create or update a tool from a callable

Args:
  func: The callable to create or update the tool from.

  args_schema: The arguments schema of the function, as a Pydantic model.

  description: The description of the tool.

  tags: Metadata tags.

  source_type: The source type of the function.

  json_schema: The JSON schema of the function (auto-generated from source_code if not
      provided)

  return_char_limit: The maximum number of characters in the response.

  pip_requirements: Optional list of pip packages required by this tool.

  npm_requirements: Optional list of npm packages required by this tool.

  default_requires_approval: Whether or not to require approval before executing this tool.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

Examples:
from letta_client import Letta

client = Letta(
    token="YOUR_TOKEN",
)

def add_two_numbers(a: int, b: int) -> int:
    return a + b

client.tools.upsert_from_function(
    func=add_two_numbers,
)

class InventoryEntryData(BaseModel):
    data: InventoryEntry
    quantity_change: int

def manage_inventory(data: InventoryEntry, quantity_change: int) -> bool:
    pass

client.tools.upsert_from_function(
    func=manage_inventory,
    args_schema=InventoryEntryData,
)

```python
upsert_from_function(
    func: Callable[..., Any]  # required,
    args_schema: Optional[Type[BaseModel]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    source_type: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    return_char_limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    pip_requirements: Optional[Iterable[PipRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    npm_requirements: Optional[Iterable[NpmRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    default_requires_approval: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> Tool
```

**Parameters:**

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `func` | Callable[..., Any] | Yes | - |
| `args_schema` | Optional[Type[BaseModel]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
| `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `source_type` | str | Omit | No | <letta_client.Omit object at 0x000002... |
| `json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `return_char_limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
| `pip_requirements` | Optional[Iterable[PipRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `npm_requirements` | Optional[Iterable[NpmRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
| `default_requires_approval` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
| `extra_headers` | Headers | None | No | None |
| `extra_query` | Query | None | No | None |
| `extra_body` | Body | None | No | None |
| `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_raw_response

Sub-resource: `client.tools.with_raw_response`

  #### create()

  Create a new tool

Args:
  source_code: The source code of the function.

  args_json_schema: The args JSON schema of the function.

  default_requires_approval: Whether or not to require approval before executing this tool.

  description: The description of the tool.

  enable_parallel_execution: If set to True, then this tool will potentially be executed concurrently with
      other tools. Default False.

  json_schema: The JSON schema of the function (auto-generated from source_code if not
      provided)

  npm_requirements: Optional list of npm packages required by this tool.

  pip_requirements: Optional list of pip packages required by this tool.

  return_char_limit: The maximum number of characters in the response.

  source_type: The source type of the function.

  tags: Metadata tags.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      source_code: str  # required,
      args_json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      default_requires_approval: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_parallel_execution: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      npm_requirements: Optional[Iterable[NpmRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      pip_requirements: Optional[Iterable[PipRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      return_char_limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      source_type: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Tool
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `source_code` | str | Yes | - |
  | `args_json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `default_requires_approval` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_parallel_execution` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `npm_requirements` | Optional[Iterable[NpmRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `pip_requirements` | Optional[Iterable[PipRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `return_char_limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `source_type` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete a tool by name

Args:
  tool_id: The ID of the tool in the format 'tool-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      tool_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `tool_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get a list of all tools available to agents.

Args:
  after: Tool ID cursor for pagination. Returns tools that come after this tool ID in the
      specified sort order

  before: Tool ID cursor for pagination. Returns tools that come before this tool ID in
      the specified sort order

  exclude_tool_types: Tool type(s) to exclude - accepts repeated params or comma-separated values

  limit: Maximum number of tools to return

  name: Filter by single tool name

  names: Filter by specific tool names

  order: Sort order for tools by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  return_only_letta_tools: Return only tools with tool*type starting with 'letta*'

  search: Search tool names (case-insensitive partial match)

  tool_ids: Filter by specific tool IDs - accepts repeated params or comma-separated values

  tool_types: Filter by tool type(s) - accepts repeated params or comma-separated values

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      exclude_tool_types: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      names: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      return_only_letta_tools: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_types: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Tool]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `exclude_tool_types` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `names` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `return_only_letta_tools` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_types` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get a tool by ID

Args:
  tool_id: The ID of the tool in the format 'tool-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      tool_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Tool
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `tool_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### search()

  Search tools using semantic search.

Requires tool embedding to be enabled (embed_tools=True). Uses vector search,
full-text search, or hybrid mode to find tools matching the query.

Returns tools ranked by relevance with their search scores.

Args:
  limit: Maximum number of results to return.

  query: Text query for semantic search.

  search_mode: Search mode: vector, fts, or hybrid.

  tags: Filter by tags (match any).

  tool_types: Filter by tool types (e.g., 'custom', 'letta_core').

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  search(
      limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      query: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      search_mode: Literal['vector', 'fts', 'hybrid'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_types: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ToolSearchResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `query` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `search_mode` | Literal['vector', 'fts', 'hybrid'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_types` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update an existing tool

Args:
  tool_id: The ID of the tool in the format 'tool-<uuid4>'

  args_json_schema: The args JSON schema of the function.

  default_requires_approval: Whether or not to require approval before executing this tool.

  description: The description of the tool.

  enable_parallel_execution: If set to True, then this tool will potentially be executed concurrently with
      other tools. Default False.

  json_schema: The JSON schema of the function (auto-generated from source_code if not
      provided)

  metadata: A dictionary of additional metadata for the tool.

  npm_requirements: Optional list of npm packages required by this tool.

  pip_requirements: Optional list of pip packages required by this tool.

  return_char_limit: The maximum number of characters in the response.

  source_code: The source code of the function.

  source_type: The type of the source code.

  tags: Metadata tags.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      tool_id: str  # required,
      args_json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      default_requires_approval: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_parallel_execution: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      npm_requirements: Optional[Iterable[NpmRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      pip_requirements: Optional[Iterable[PipRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      return_char_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      source_code: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      source_type: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Tool
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `tool_id` | str | Yes | - |
  | `args_json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `default_requires_approval` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_parallel_execution` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `npm_requirements` | Optional[Iterable[NpmRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `pip_requirements` | Optional[Iterable[PipRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `return_char_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `source_code` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `source_type` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### upsert()

  Create or update a tool

Args:
  source_code: The source code of the function.

  args_json_schema: The args JSON schema of the function.

  default_requires_approval: Whether or not to require approval before executing this tool.

  description: The description of the tool.

  enable_parallel_execution: If set to True, then this tool will potentially be executed concurrently with
      other tools. Default False.

  json_schema: The JSON schema of the function (auto-generated from source_code if not
      provided)

  npm_requirements: Optional list of npm packages required by this tool.

  pip_requirements: Optional list of pip packages required by this tool.

  return_char_limit: The maximum number of characters in the response.

  source_type: The source type of the function.

  tags: Metadata tags.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  upsert(
      source_code: str  # required,
      args_json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      default_requires_approval: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_parallel_execution: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      npm_requirements: Optional[Iterable[NpmRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      pip_requirements: Optional[Iterable[PipRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      return_char_limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      source_type: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Tool
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `source_code` | str | Yes | - |
  | `args_json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `default_requires_approval` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_parallel_execution` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `npm_requirements` | Optional[Iterable[NpmRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `pip_requirements` | Optional[Iterable[PipRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `return_char_limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `source_type` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

#### with_streaming_response

Sub-resource: `client.tools.with_streaming_response`

  #### create()

  Create a new tool

Args:
  source_code: The source code of the function.

  args_json_schema: The args JSON schema of the function.

  default_requires_approval: Whether or not to require approval before executing this tool.

  description: The description of the tool.

  enable_parallel_execution: If set to True, then this tool will potentially be executed concurrently with
      other tools. Default False.

  json_schema: The JSON schema of the function (auto-generated from source_code if not
      provided)

  npm_requirements: Optional list of npm packages required by this tool.

  pip_requirements: Optional list of pip packages required by this tool.

  return_char_limit: The maximum number of characters in the response.

  source_type: The source type of the function.

  tags: Metadata tags.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  create(
      source_code: str  # required,
      args_json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      default_requires_approval: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_parallel_execution: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      npm_requirements: Optional[Iterable[NpmRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      pip_requirements: Optional[Iterable[PipRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      return_char_limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      source_type: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Tool
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `source_code` | str | Yes | - |
  | `args_json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `default_requires_approval` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_parallel_execution` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `npm_requirements` | Optional[Iterable[NpmRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `pip_requirements` | Optional[Iterable[PipRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `return_char_limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `source_type` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### delete()

  Delete a tool by name

Args:
  tool_id: The ID of the tool in the format 'tool-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  delete(
      tool_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> object
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `tool_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### list()

  Get a list of all tools available to agents.

Args:
  after: Tool ID cursor for pagination. Returns tools that come after this tool ID in the
      specified sort order

  before: Tool ID cursor for pagination. Returns tools that come before this tool ID in
      the specified sort order

  exclude_tool_types: Tool type(s) to exclude - accepts repeated params or comma-separated values

  limit: Maximum number of tools to return

  name: Filter by single tool name

  names: Filter by specific tool names

  order: Sort order for tools by creation time. 'asc' for oldest first, 'desc' for newest
      first

  order_by: Field to sort by

  return_only_letta_tools: Return only tools with tool*type starting with 'letta*'

  search: Search tool names (case-insensitive partial match)

  tool_ids: Filter by specific tool IDs - accepts repeated params or comma-separated values

  tool_types: Filter by tool type(s) - accepts repeated params or comma-separated values

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  list(
      after: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      before: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      exclude_tool_types: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      name: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      names: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order: Literal['asc', 'desc'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      order_by: Literal['created_at'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      return_only_letta_tools: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      search: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_ids: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_types: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> SyncArrayPage[Tool]
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `after` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `before` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `exclude_tool_types` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `name` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `names` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order` | Literal['asc', 'desc'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `order_by` | Literal['created_at'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `return_only_letta_tools` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `search` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_ids` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_types` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### retrieve()

  Get a tool by ID

Args:
  tool_id: The ID of the tool in the format 'tool-<uuid4>'

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  retrieve(
      tool_id: str  # required,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Tool
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `tool_id` | str | Yes | - |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### search()

  Search tools using semantic search.

Requires tool embedding to be enabled (embed_tools=True). Uses vector search,
full-text search, or hybrid mode to find tools matching the query.

Returns tools ranked by relevance with their search scores.

Args:
  limit: Maximum number of results to return.

  query: Text query for semantic search.

  search_mode: Search mode: vector, fts, or hybrid.

  tags: Filter by tags (match any).

  tool_types: Filter by tool types (e.g., 'custom', 'letta_core').

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  search(
      limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      query: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      search_mode: Literal['vector', 'fts', 'hybrid'] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tool_types: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> ToolSearchResponse
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `query` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `search_mode` | Literal['vector', 'fts', 'hybrid'] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tool_types` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### update()

  Update an existing tool

Args:
  tool_id: The ID of the tool in the format 'tool-<uuid4>'

  args_json_schema: The args JSON schema of the function.

  default_requires_approval: Whether or not to require approval before executing this tool.

  description: The description of the tool.

  enable_parallel_execution: If set to True, then this tool will potentially be executed concurrently with
      other tools. Default False.

  json_schema: The JSON schema of the function (auto-generated from source_code if not
      provided)

  metadata: A dictionary of additional metadata for the tool.

  npm_requirements: Optional list of npm packages required by this tool.

  pip_requirements: Optional list of pip packages required by this tool.

  return_char_limit: The maximum number of characters in the response.

  source_code: The source code of the function.

  source_type: The type of the source code.

  tags: Metadata tags.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  update(
      tool_id: str  # required,
      args_json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      default_requires_approval: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_parallel_execution: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      metadata: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      npm_requirements: Optional[Iterable[NpmRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      pip_requirements: Optional[Iterable[PipRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      return_char_limit: Optional[int] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      source_code: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      source_type: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Tool
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `tool_id` | str | Yes | - |
  | `args_json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `default_requires_approval` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_parallel_execution` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `metadata` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `npm_requirements` | Optional[Iterable[NpmRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `pip_requirements` | Optional[Iterable[PipRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `return_char_limit` | Optional[int] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `source_code` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `source_type` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |

  #### upsert()

  Create or update a tool

Args:
  source_code: The source code of the function.

  args_json_schema: The args JSON schema of the function.

  default_requires_approval: Whether or not to require approval before executing this tool.

  description: The description of the tool.

  enable_parallel_execution: If set to True, then this tool will potentially be executed concurrently with
      other tools. Default False.

  json_schema: The JSON schema of the function (auto-generated from source_code if not
      provided)

  npm_requirements: Optional list of npm packages required by this tool.

  pip_requirements: Optional list of pip packages required by this tool.

  return_char_limit: The maximum number of characters in the response.

  source_type: The source type of the function.

  tags: Metadata tags.

  extra_headers: Send extra headers

  extra_query: Add additional query parameters to the request

  extra_body: Add additional JSON properties to the request

  timeout: Override the client-level default timeout for this request, in seconds

  ```python
  upsert(
      source_code: str  # required,
      args_json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      default_requires_approval: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      description: Optional[str] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      enable_parallel_execution: Optional[bool] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      json_schema: Optional[Dict[str, object]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      npm_requirements: Optional[Iterable[NpmRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      pip_requirements: Optional[Iterable[PipRequirementParam]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      return_char_limit: int | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      source_type: str | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      tags: Optional[SequenceNotStr[str]] | Omit = <letta_client.Omit object at 0x00000249779A2BA0>,
      extra_headers: Headers | None = None,
      extra_query: Query | None = None,
      extra_body: Body | None = None,
      timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
  ) -> Tool
  ```

  **Parameters:**

  | Parameter | Type | Required | Default |
  |-----------|------|----------|---------|
  | `source_code` | str | Yes | - |
  | `args_json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `default_requires_approval` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `description` | Optional[str] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `enable_parallel_execution` | Optional[bool] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `json_schema` | Optional[Dict[str, object]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `npm_requirements` | Optional[Iterable[NpmRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `pip_requirements` | Optional[Iterable[PipRequirementParam]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `return_char_limit` | int | Omit | No | <letta_client.Omit object at 0x000002... |
  | `source_type` | str | Omit | No | <letta_client.Omit object at 0x000002... |
  | `tags` | Optional[SequenceNotStr[str]] | Omit | No | <letta_client.Omit object at 0x000002... |
  | `extra_headers` | Headers | None | No | None |
  | `extra_query` | Query | None | No | None |
  | `extra_body` | Body | None | No | None |
  | `timeout` | float | httpx.Timeout | None | NotGiven | No | NOT_GIVEN |


---

## Exception Classes

### LettaError

Common base class for all non-exit exceptions.

### APIError

Common base class for all non-exit exceptions.

### APIConnectionError

Common base class for all non-exit exceptions.

### APIStatusError

Raised when an API response has a status code of 4xx or 5xx.

### APITimeoutError

Common base class for all non-exit exceptions.

### AuthenticationError

Raised when an API response has a status code of 4xx or 5xx.

### BadRequestError

Raised when an API response has a status code of 4xx or 5xx.

### ConflictError

Raised when an API response has a status code of 4xx or 5xx.

### InternalServerError

Raised when an API response has a status code of 4xx or 5xx.

### NotFoundError

Raised when an API response has a status code of 4xx or 5xx.

### PermissionDeniedError

Raised when an API response has a status code of 4xx or 5xx.

### RateLimitError

Raised when an API response has a status code of 4xx or 5xx.

### UnprocessableEntityError

Raised when an API response has a status code of 4xx or 5xx.

### APIResponseValidationError

Common base class for all non-exit exceptions.
