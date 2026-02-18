> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Conversation with Async

> Use async/await for concurrent agent operations and non-blocking execution.

export const path_to_script_0 = "examples/01_standalone_sdk/11_async.py"

> A ready-to-run example is available [here](#ready-to-run-example)!

### Concurrent Agents

Run multiple agent tasks in parallel using `asyncio.gather()`:

```python icon="python" wrap theme={null}
async def main():
    loop = asyncio.get_running_loop()
    callback = AsyncCallbackWrapper(callback_coro, loop)

    # Create multiple conversation tasks running in parallel
    tasks = [
        loop.run_in_executor(None, run_conversation, callback),
        loop.run_in_executor(None, run_conversation, callback),
        loop.run_in_executor(None, run_conversation, callback)
    ]
    results = await asyncio.gather(*tasks)
```

## Ready-to-run Example

<Note>
  This example is available on GitHub: [examples/01\_standalone\_sdk/11\_async.py](https://github.com/OpenHands/software-agent-sdk/blob/main/examples/01_standalone_sdk/11_async.py)
</Note>

This example demonstrates usage of a Conversation in an async context
(e.g.: From a fastapi server). The conversation is run in a background
thread and a callback with results is executed in the main runloop

```python icon="python" expandable examples/01_standalone_sdk/11_async.py theme={null}
"""
This example demonstrates usage of a Conversation in an async context
(e.g.: From a fastapi server). The conversation is run in a background
thread and a callback with results is executed in the main runloop
"""

import asyncio
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
from openhands.sdk.conversation.types import ConversationCallbackType
from openhands.sdk.tool import Tool
from openhands.sdk.utils.async_utils import AsyncCallbackWrapper
from openhands.tools.file_editor import FileEditorTool
from openhands.tools.task_tracker import TaskTrackerTool
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
    Tool(name=TaskTrackerTool.name),
]

# Agent
agent = Agent(llm=llm, tools=tools)

llm_messages = []  # collect raw LLM messages


# Callback coroutine
async def callback_coro(event: Event):
    if isinstance(event, LLMConvertibleEvent):
        llm_messages.append(event.to_llm_message())


# Synchronous run conversation
def run_conversation(callback: ConversationCallbackType):
    conversation = Conversation(agent=agent, callbacks=[callback])

    conversation.send_message(
        "Hello! Can you create a new Python file named hello.py that prints "
        "'Hello, World!'? Use task tracker to plan your steps."
    )
    conversation.run()

    conversation.send_message("Great! Now delete that file.")
    conversation.run()


async def main():
    loop = asyncio.get_running_loop()

    # Create the callback
    callback = AsyncCallbackWrapper(callback_coro, loop)

    # Run the conversation in a background thread and wait for it to finish...
    await loop.run_in_executor(None, run_conversation, callback)

    print("=" * 100)
    print("Conversation finished. Got the following LLM messages:")
    for i, message in enumerate(llm_messages):
        print(f"Message {i}: {str(message)[:200]}")

    # Report cost
    cost = llm.metrics.accumulated_cost
    print(f"EXAMPLE_COST: {cost}")


if __name__ == "__main__":
    asyncio.run(main())
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

* **[Persistence](/sdk/guides/convo-persistence)** - Save and restore conversation state
* **[Send Message While Processing](/sdk/guides/convo-send-message-while-running)** - Interrupt running agents
