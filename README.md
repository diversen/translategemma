https://ollama.com/library/translategemma

Simple CLI wrapper around Ollama's `translategemma` model using the OpenAI Python client.

Usage:

```bash
gemma-translate --from en --to da "text to translate"
gemma-translate --from en --to da ./input.txt
```

Defaults:

- `OPENAI_BASE_URL=http://localhost:11434/v1`
- `OPENAI_API_KEY=ollama`
- model name: `translategemma:27b`

Override the model with:

```bash
gemma-translate --from en --to da --model translategemma:latest "Hello world"
```
