> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Secret Registry

> Provide environment variables and secrets to agent workspace securely.

export const path_to_script_0 = "examples/01_standalone_sdk/12_custom_secrets.py"

> A ready-to-run example is available [here](#ready-to-run-example)!

The Secret Registry provides a secure way to handle sensitive data in your agent's workspace.
It automatically detects secret references in bash commands, injects them as environment variables when needed,
and masks secret values in command outputs to prevent accidental exposure.

### Injecting Secrets

Use the `update_secrets()` method to add secrets to your conversation.

Secrets can be provided as static strings or as callable functions that dynamically retrieve values, enabling integration with external secret stores and credential management systems:

```python focus={4,11} icon="python" wrap theme={null}
from openhands.sdk.conversation.secret_source import SecretSource

# Static secret
conversation.update_secrets({"SECRET_TOKEN": "my-secret-token-value"})

# Dynamic secret using SecretSource
class MySecretSource(SecretSource):
    def get_value(self) -> str:
        return "callable-based-secret"

conversation.update_secrets({"SECRET_FUNCTION_TOKEN": MySecretSource()})
```

## Ready-to-run Example

<Note>
  This example is available on GitHub: [examples/01\_standalone\_sdk/12\_custom\_secrets.py](https://github.com/OpenHands/software-agent-sdk/blob/main/examples/01_standalone_sdk/12_custom_secrets.py)
</Note>

```python icon="python" expandable examples/01_standalone_sdk/12_custom_secrets.py theme={null}
import os

from pydantic import SecretStr

from openhands.sdk import (
    LLM,
    Agent,
    Conversation,
)
from openhands.sdk.secret import SecretSource
from openhands.sdk.tool import Tool
from openhands.tools.file_editor import FileEditorTool
from openhands.tools.terminal import TerminalTool


# Configure LLM
api_key = os.getenv("LLM_API_KEY")
assert api_key is not None, "LLM_API_KEY environment variable is not set."
model = os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-5-20250929")
base_url = os.getenv("LLM_BASE_URL")
llm = LLM(
    usage_id="agent",
    model=model,
    base_url=base_url,
    api_key=SecretStr(api_key),
)

# Tools
tools = [
    Tool(name=TerminalTool.name),
    Tool(name=FileEditorTool.name),
]

# Agent
agent = Agent(llm=llm, tools=tools)
conversation = Conversation(agent)


class MySecretSource(SecretSource):
    def get_value(self) -> str:
        return "callable-based-secret"


conversation.update_secrets(
    {"SECRET_TOKEN": "my-secret-token-value", "SECRET_FUNCTION_TOKEN": MySecretSource()}
)

conversation.send_message("just echo $SECRET_TOKEN")

conversation.run()

conversation.send_message("just echo $SECRET_FUNCTION_TOKEN")

conversation.run()

# Report cost
cost = llm.metrics.accumulated_cost
print(f"EXAMPLE_COST: {cost}")
```

You can run the example code as-is.

<Note>
  The model name should follow the [LiteLLM convention](https://models.litellm.ai/): `provider/model_name` (e.g., `anthropic/claude-sonnet-4-5-20250929`, `openai/gpt-4o`).
  The `LLM_API_KEY` should be the API key for your chosen provider.
</Note>

<CodeGroup>
  <CodeBlock language="bash" filename="Bring-your-own provider key" icon="terminal" wrap>
    {`export LLM_API_KEY="your-api-key"\nexport LLM_MODEL="anthropic/claude-sonnet-4-5-20250929"  # or openai/gpt-4o, etc.\ncd software-agent-sdk\nuv run python ${path_to_script_0}`}
  </CodeBlock>

  <CodeBlock language="bash" filename="OpenHands Cloud" icon="terminal" wrap>
    {`# https://app.all-hands.dev/settings/api-keys\nexport LLM_API_KEY="your-openhands-api-key"\nexport LLM_MODEL="openhands/claude-sonnet-4-5-20250929"\ncd software-agent-sdk\nuv run python ${path_to_script_0}`}
  </CodeBlock>
</CodeGroup>

<Tip>
  **ChatGPT Plus/Pro subscribers**: You can use `LLM.subscription_login()` to authenticate with your ChatGPT account and access Codex models without consuming API credits. See the [LLM Subscriptions guide](/sdk/guides/llm-subscriptions) for details.
</Tip>

## Next Steps

* **[MCP Integration](/sdk/guides/mcp)** - Connect to MCP
* **[Security Analyzer](/sdk/guides/security)** - Add security validation
