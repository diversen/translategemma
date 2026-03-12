from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from openai import OpenAI


DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "translategemma:27b"
DEFAULT_API_KEY = "ollama"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="translategemma",
        description="Translate text or a file with TranslateGemma served by Ollama.",
    )
    parser.add_argument(
        "--from",
        dest="source_lang",
        required=True,
        help="Source language code or name, for example 'en'.",
    )
    parser.add_argument(
        "--to",
        dest="target_lang",
        required=True,
        help="Target language code or name, for example 'da'.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("GEMMA_TRANSLATE_MODEL", DEFAULT_MODEL),
        help=f"Model name to request from Ollama. Default: {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "input_value",
        help="Text to translate or a path to a file containing the text.",
    )
    return parser


def load_input(input_value: str) -> str:
    path = Path(input_value).expanduser()
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return input_value


def build_prompt(source_lang: str, target_lang: str, text: str) -> str:
    return (
        f"Translate the following text from {source_lang} to {target_lang}. "
        "Return only the translated text.\n\n"
        f"{text}"
    )


def stream_translation(
    *,
    source_lang: str,
    target_lang: str,
    text: str,
    model: str,
) -> int:
    client = OpenAI(
        base_url=os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL),
        api_key=os.environ.get("OPENAI_API_KEY", DEFAULT_API_KEY),
    )

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a translation engine. Translate the user text exactly "
                    "as requested and return only the translation."
                ),
            },
            {
                "role": "user",
                "content": build_prompt(source_lang, target_lang, text),
            },
        ],
        stream=True,
    )

    wrote_output = False
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if not delta:
            continue
        sys.stdout.write(delta)
        sys.stdout.flush()
        wrote_output = True

    if wrote_output:
        sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        text = load_input(args.input_value)
        return stream_translation(
            source_lang=args.source_lang,
            target_lang=args.target_lang,
            text=text,
            model=args.model,
        )
    except FileNotFoundError as exc:
        print(f"Input file not found: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nTranslation interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Translation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
