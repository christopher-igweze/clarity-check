# Prompting Guides Bundle (Markdown Only)

This folder contains model prompting guides in `.md` format from official provider docs/repos.

## Providers included
- OpenAI
- Anthropic
- Google Gemini
- xAI Grok

## Source policy
- No HTML dumps.
- Notebook sources (`.ipynb`) are converted to `.md` by extracting markdown cells and wrapping code cells in fenced blocks.
- All files come from official provider domains or official provider GitHub org repos.

## Sources used
- OpenAI cookbook notebooks: `https://github.com/openai/openai-cookbook`
- OpenAI docs index: `https://developers.openai.com/llms.txt`
- Anthropic prompt-engineering markdown pages: `https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/`
- Google Gemini cookbook examples: `https://github.com/google-gemini/cookbook`
- xAI Grok prompts repo: `https://github.com/xai-org/grok-prompts`
- xAI docs index: `https://docs.x.ai/llms.txt`

## Layout
- `openai/`
- `anthropic/`
- `google/`
- `grok/`
- `ONE_SHOT_IMPLEMENTATION_FRAMEWORK.md` (canonical one-shot coding prompt contract)
- `ONE_SHOT_MATRIX_RESULTS.md` (tracked summary of matrix outcomes)
