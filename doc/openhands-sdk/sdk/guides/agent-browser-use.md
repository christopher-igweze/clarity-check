> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Browser Use

> Enable web browsing and interaction capabilities for your agent.

export const path_to_script_0 = "examples/01_standalone_sdk/15_browser_use.py"

> A ready-to-run example is available [here](#ready-to-run-example)!

The BrowserToolSet integration enables your agent to interact with web pages through automated browser control. Built
on top of [browser-use](https://github.com/browser-use/browser-use), it provides capabilities for navigating websites, clicking elements, filling forms,
and extracting content - all through natural language instructions.

## How It Works

The [ready-to-run example](#ready-to-run-example) demonstrates combining multiple tools to create a capable web research agent:

1. **BrowserToolSet**: Provides automated browser control for web interaction
2. **FileEditorTool**: Allows the agent to read and write files if needed
3. **BashTool**: Enables command-line operations for additional functionality

The agent uses these tools to:

* Navigate to specified URLs
* Interact with web page elements (clicking, scrolling, etc.)
* Extract and analyze content from web pages
* Summarize information from multiple sources

In this example, the agent visits the openhands.dev blog, finds the latest blog post, and provides a summary of its main points.

## Customization

For advanced use cases requiring only a subset of browser tools or custom configurations, you can manually
register individual browser tools. Refer to the [BrowserToolSet definition](https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-tools/openhands/tools/browser_use/definition.py) to see the available individual
tools and create a `BrowserToolExecutor` with customized tool configurations before constructing the Agent.
This gives you fine-grained control over which browser capabilities are exposed to the agent.

## Ready-to-run Example

<Note>
  This example is available on GitHub: [examples/01\_standalone\_sdk/15\_browser\_use.py](https://github.com/OpenHands/software-agent-sdk/blob/main/examples/01_standalone_sdk/15_browser_use.py)
</Note>

```python icon="python" expandable examples/01_standalone_sdk/15_browser_use.py theme={null}
import os

from pydantic import SecretStr

from openhands.sdk import (
    LLM,
    Agent,
    Conversation,
    Event,
    LLMConvertibleEvent,
    get_logger,
)
from openhands.sdk.tool import Tool
from openhands.tools.browser_use import BrowserToolSet
from openhands.tools.file_editor import FileEditorTool
from openhands.tools.terminal import TerminalTool


logger = get_logger(__name__)

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
cwd = os.getcwd()
tools = [
    Tool(
        name=TerminalTool.name,
    ),
    Tool(name=FileEditorTool.name),
    Tool(name=BrowserToolSet.name),
]

# If you need fine-grained browser control, you can manually register individual browser
# tools by creating a BrowserToolExecutor and providing factories that return customized
# Tool instances before constructing the Agent.

# Agent
agent = Agent(llm=llm, tools=tools)

llm_messages = []  # collect raw LLM messages


def conversation_callback(event: Event):
    if isinstance(event, LLMConvertibleEvent):
        llm_messages.append(event.to_llm_message())


conversation = Conversation(
    agent=agent, callbacks=[conversation_callback], workspace=cwd
)

conversation.send_message(
    "Could you go to https://openhands.dev/ blog page and summarize main "
    "points of the latest blog?"
)
conversation.run()

print("=" * 100)
print("Conversation finished. Got the following LLM messages:")
for i, message in enumerate(llm_messages):
    print(f"Message {i}: {str(message)[:200]}")
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

* **[Custom Tools](/sdk/guides/custom-tools)** - Create specialized tools
* **[MCP Integration](/sdk/guides/mcp)** - Connect external services
