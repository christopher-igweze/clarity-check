> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# LLM Subscriptions

> Use your ChatGPT Plus/Pro subscription to access Codex models without consuming API credits.

export const path_to_script_0 = "examples/01_standalone_sdk/35_subscription_login.py"

<Info>
  OpenAI subscription is the first provider we support. More subscription providers will be added in future releases.
</Info>

> A ready-to-run example is available [here](#ready-to-run-example)!

Use your existing ChatGPT Plus or Pro subscription to access OpenAI's Codex models without consuming API credits. The SDK handles OAuth authentication, credential caching, and automatic token refresh.

## How It Works

<Steps>
  <Step>
    ### Call subscription\_login()

    The `LLM.subscription_login()` class method handles the entire authentication flow:

    ```python icon="python" theme={null}
    from openhands.sdk import LLM

    llm = LLM.subscription_login(vendor="openai", model="gpt-5.2-codex")
    ```

    On first run, this opens your browser for OAuth authentication with OpenAI. After successful login, credentials are cached locally in `~/.openhands/auth/` for future use.
  </Step>

  <Step>
    ### Use the LLM

    Once authenticated, use the LLM with your agent as usual. The SDK automatically refreshes tokens when they expire.
  </Step>
</Steps>

## Supported Models

The following models are available via ChatGPT subscription:

| Model                | Description                  |
| -------------------- | ---------------------------- |
| `gpt-5.2-codex`      | Latest Codex model (default) |
| `gpt-5.2`            | GPT-5.2 base model           |
| `gpt-5.1-codex-max`  | High-capacity Codex model    |
| `gpt-5.1-codex-mini` | Lightweight Codex model      |

## Configuration Options

### Force Fresh Login

If your cached credentials become stale or you want to switch accounts:

```python icon="python" theme={null}
llm = LLM.subscription_login(
    vendor="openai",
    model="gpt-5.2-codex",
    force_login=True,  # Always perform fresh OAuth login
)
```

### Disable Browser Auto-Open

For headless environments or when you prefer to manually open the URL:

```python icon="python" theme={null}
llm = LLM.subscription_login(
    vendor="openai",
    model="gpt-5.2-codex",
    open_browser=False,  # Prints URL to console instead
)
```

### Check Subscription Mode

Verify that the LLM is using subscription-based authentication:

```python icon="python" theme={null}
llm = LLM.subscription_login(vendor="openai", model="gpt-5.2-codex")
print(f"Using subscription: {llm.is_subscription}")  # True
```

## Credential Storage

Credentials are stored securely in `~/.openhands/auth/`. To clear cached credentials and force a fresh login, delete the files in this directory.

## Ready-to-run Example

<Note>
  This example is available on GitHub: [examples/01\_standalone\_sdk/35\_subscription\_login.py](https://github.com/OpenHands/software-agent-sdk/blob/main/examples/01_standalone_sdk/35_subscription_login.py)
</Note>

```python icon="python" expandable examples/01_standalone_sdk/35_subscription_login.py theme={null}
"""Example: Using ChatGPT subscription for Codex models.

This example demonstrates how to use your ChatGPT Plus/Pro subscription
to access OpenAI's Codex models without consuming API credits.

The subscription_login() method handles:
- OAuth PKCE authentication flow
- Credential caching (~/.openhands/auth/)
- Automatic token refresh

Supported models:
- gpt-5.2-codex
- gpt-5.2
- gpt-5.1-codex-max
- gpt-5.1-codex-mini

Requirements:
- Active ChatGPT Plus or Pro subscription
- Browser access for initial OAuth login
"""

import os

from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.tools.file_editor import FileEditorTool
from openhands.tools.terminal import TerminalTool


# First time: Opens browser for OAuth login
# Subsequent calls: Reuses cached credentials (auto-refreshes if expired)
llm = LLM.subscription_login(
    vendor="openai",
    model="gpt-5.2-codex",  # or "gpt-5.2", "gpt-5.1-codex-max", "gpt-5.1-codex-mini"
)

# Alternative: Force a fresh login (useful if credentials are stale)
# llm = LLM.subscription_login(vendor="openai", model="gpt-5.2-codex", force_login=True)

# Alternative: Disable auto-opening browser (prints URL to console instead)
# llm = LLM.subscription_login(
#     vendor="openai", model="gpt-5.2-codex", open_browser=False
# )

# Verify subscription mode is active
print(f"Using subscription mode: {llm.is_subscription}")

# Use the LLM with an agent as usual
agent = Agent(
    llm=llm,
    tools=[
        Tool(name=TerminalTool.name),
        Tool(name=FileEditorTool.name),
    ],
)

cwd = os.getcwd()
conversation = Conversation(agent=agent, workspace=cwd)

conversation.send_message("List the files in the current directory.")
conversation.run()
print("Done!")
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
* **[LLM Streaming](/sdk/guides/llm-streaming)** - Stream responses token-by-token
* **[LLM Reasoning](/sdk/guides/llm-reasoning)** - Access model reasoning traces
