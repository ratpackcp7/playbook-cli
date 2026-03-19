"""OpenRouter API client, model panel config, prompt assembly, response parsing."""

import json
import os
import re
from datetime import date
from pathlib import Path

import httpx


DEFAULT_MODELS = [
    {"id": "google/gemini-3.1-pro-preview", "name": "Gemini 3.1 Pro", "slug": "gemini", "role": "Architect"},
    {"id": "deepseek/deepseek-chat", "name": "DeepSeek V3.2", "slug": "deepseek", "role": "Practitioner"},
    {"id": "meta-llama/llama-4-maverick", "name": "Llama 4 Maverick", "slug": "llama", "role": "Contrarian"},
]

SYSTEM_PROMPT = (
    "You are a critical technical reviewer. You are reviewing a project specification "
    "and task breakdown that will be executed by an autonomous coding agent (Claude Code). "
    "The agent follows instructions literally and cannot ask clarifying questions.\n\n"
    "Your job is to find every issue that would cause the agent to produce wrong code, "
    "make wrong assumptions, or get stuck. Be brutally critical. Focus on:\n\n"
    "1. Gaps or ambiguities that would cause wrong assumptions\n"
    "2. Missing acceptance criteria\n"
    "3. Dependency ordering problems\n"
    "4. Interface mismatches between tasks (function signatures, data formats)\n"
    "5. Things that sound good in theory but will break in practice\n"
    "6. Python packaging, config, or tooling gotchas\n\n"
    "Do NOT be polite. List every issue you find. Number each issue. "
    "For each issue, state: what's wrong, why it matters, and how to fix it."
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
HTTP_REFERER = "https://github.com/ratpackcp7/playbook-cli"


def load_review_config(project_root: Path) -> list[dict]:
    """Load model panel from .playbook-review.json or return defaults."""
    config_path = project_root / ".playbook-review.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        return config.get("models", DEFAULT_MODELS)
    return DEFAULT_MODELS


def get_api_key() -> str:
    """Read OPENROUTER_API_KEY from environment. Raises if not set."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit(2)
    return key


def build_user_message(spec_content: str, tasks_content: str) -> str:
    """Assemble the user message from SPEC.md and TASKS.md contents."""
    return f"## PROJECT SPECIFICATION\n\n{spec_content}\n\n## TASK BREAKDOWN\n\n{tasks_content}"


def estimate_tokens(text: str) -> int:
    """Estimate token count: ~1.3 tokens per word."""
    word_count = len(text.split())
    return int(word_count * 1.3)


def estimate_cost(input_tokens: int, output_tokens: int = 2500) -> float:
    """Rough cost estimate. Uses conservative rates."""
    # Approximate rates per 1M tokens (input/output)
    # These are ballpark — exact rates vary by model
    input_cost = (input_tokens / 1_000_000) * 1.0
    output_cost = (output_tokens / 1_000_000) * 3.0
    return input_cost + output_cost


def count_issues(response_text: str) -> int:
    """Count issues in the model response. Heuristic: lines matching numbered items or bullet points."""
    count = 0
    for line in response_text.splitlines():
        stripped = line.strip()
        if re.match(r"^\d+\.", stripped) or stripped.startswith("- "):
            count += 1
    return count


def call_openrouter(model_id: str, api_key: str, user_message: str) -> dict:
    """Send a review request to OpenRouter. Returns the API response dict."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": HTTP_REFERER,
    }
    body = {
        "model": model_id,
        "max_tokens": 8000,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    }
    response = httpx.post(OPENROUTER_URL, json=body, headers=headers, timeout=120.0)
    response.raise_for_status()
    return response.json()


def extract_response_content(api_response: dict) -> str:
    """Extract the message content from an OpenRouter response."""
    return api_response["choices"][0]["message"]["content"]


def write_review_file(
    reviews_dir: Path,
    model: dict,
    response_text: str,
    input_tokens: int,
    cost: float,
) -> Path:
    """Write review output to reviews/spec-review-{slug}.md."""
    reviews_dir.mkdir(parents=True, exist_ok=True)
    output_path = reviews_dir / f"spec-review-{model['slug']}.md"
    content = (
        f"# Spec Review — {model['name']} ({model['role']})\n\n"
        f"**Model:** {model['id']}\n"
        f"**Date:** {date.today().isoformat()}\n"
        f"**Input tokens:** ~{input_tokens}\n"
        f"**Estimated cost:** ${cost:.4f}\n\n"
        f"---\n\n"
        f"{response_text}\n"
    )
    output_path.write_text(content)
    return output_path
