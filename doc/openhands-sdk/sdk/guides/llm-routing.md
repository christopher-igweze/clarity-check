> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Model Routing

> Route agent's LLM requests to different models.

export const path_to_script_0 = "examples/01_standalone_sdk/19_llm_routing.py"

<Warning>This feature is under active development and more default routers will be available in future releases.</Warning>

> A ready-to-run example is available [here](#ready-to-run-example)!

### Using the built-in MultimodalRouter

Define the built-in rule-based `MultimodalRouter` that will route text-only requests to a secondary LLM and multimodal requests (with images) to the primary, multimodal-capable LLM:

```python icon="python" wrap focus={13-16} theme={null}
primary_llm = LLM(
    usage_id="agent-primary",
    model=model,
    base_url=base_url,
    api_key=SecretStr(api_key),
)
secondary_llm = LLM(
    usage_id="agent-secondary",
    model="litellm_proxy/mistral/devstral-small-2507",
    base_url="https://llm-proxy.eval.all-hands.dev",
    api_key=SecretStr(api_key),
)
multimodal_router = MultimodalRouter(
    usage_id="multimodal-router",
    llms_for_routing={"primary": primary_llm, "secondary": secondary_llm},
)
```

You may define your own router by extending the `Router` class. See the [base class](https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-sdk/openhands/sdk/llm/router/base.py) for details.

## Ready-to-run Example

<Note>
  This example is available on GitHub: [examples/01\_standalone\_sdk/19\_llm\_routing.py](https://github.com/OpenHands/software-agent-sdk/blob/main/examples/01_standalone_sdk/19_llm_routing.py)
</Note>

Automatically route requests to different LLMs based on task characteristics to optimize cost and performance:

```python icon="python" expandable examples/01_standalone_sdk/19_llm_routing.py theme={null}
import os

from pydantic import SecretStr

from openhands.sdk import (
    LLM,
    Agent,
    Conversation,
    Event,
    ImageContent,
    LLMConvertibleEvent,
    Message,
    TextContent,
    get_logger,
)
from openhands.sdk.llm.router import MultimodalRouter
from openhands.tools.preset.default import get_default_tools


logger = get_logger(__name__)

# Configure LLM
api_key = os.getenv("LLM_API_KEY")
assert api_key is not None, "LLM_API_KEY environment variable is not set."
model = os.getenv("LLM_MODEL", "openhands/claude-sonnet-4-5-20250929")
base_url = os.getenv("LLM_BASE_URL")

primary_llm = LLM(
    usage_id="agent-primary",
    model=model,
    base_url=base_url,
    api_key=SecretStr(api_key),
)
secondary_llm = LLM(
    usage_id="agent-secondary",
    model="openhands/devstral-small-2507",
    base_url=base_url,
    api_key=SecretStr(api_key),
)
multimodal_router = MultimodalRouter(
    usage_id="multimodal-router",
    llms_for_routing={"primary": primary_llm, "secondary": secondary_llm},
)

# Tools
tools = get_default_tools()  # Use our default openhands experience

# Agent
agent = Agent(llm=multimodal_router, tools=tools)

llm_messages = []  # collect raw LLM messages


def conversation_callback(event: Event):
    if isinstance(event, LLMConvertibleEvent):
        llm_messages.append(event.to_llm_message())


conversation = Conversation(
    agent=agent, callbacks=[conversation_callback], workspace=os.getcwd()
)

conversation.send_message(
    message=Message(
        role="user",
        content=[TextContent(text=("Hi there, who trained you?"))],
    )
)
conversation.run()

conversation.send_message(
    message=Message(
        role="user",
        content=[
            ImageContent(
                image_urls=["http://images.cocodataset.org/val2017/000000039769.jpg"]
            ),
            TextContent(text=("What do you see in the image above?")),
        ],
    )
)
conversation.run()

conversation.send_message(
    message=Message(
        role="user",
        content=[TextContent(text=("Who trained you as an LLM?"))],
    )
)
conversation.run()

print("=" * 100)
print("Conversation finished. Got the following LLM messages:")
for i, message in enumerate(llm_messages):
    print(f"Message {i}: {str(message)[:200]}")

# Report cost
cost = conversation.conversation_stats.get_combined_metrics().accumulated_cost
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

* **[LLM Registry](/sdk/guides/llm-registry)** - Manage multiple LLM configurations
* **[LLM Metrics](/sdk/guides/metrics)** - Track token usage and costs
