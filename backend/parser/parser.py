"""
STUB — owned by Person 1 (Backend Core / Parser Lead).

Real implementation: tokenizer, chaining resolution (&&, ||, ;, |),
alias expansion, base64/obfuscation pre-detection. Builds the execution-tree
data structure everyone else consumes.

This stub exists so Persons 2-5 can build against a fixed mock shape during
Phase 1 without being blocked. Replace this file's internals; keep the
function signature and return shape stable (or update schema.py + tell
everyone if it changes).
"""

import re
import base64


def parse_command(raw_command: str) -> dict:
    """
    Returns an execution-tree dict. Minimal viable shape used downstream:

    {
        "raw": "<original string>",
        "normalized": "<alias-expanded, whitespace-cleaned string>",
        "sub_commands": ["<cmd1>", "<cmd2>", ...],  # split on chaining operators
        "chain_operators": ["&&", ";"],              # operators between sub_commands
        "obfuscation_detected": bool,
        "decoded_segments": ["<any base64-decoded strings found>"]
    }
    """
    normalized = raw_command.strip()

    # naive chain split — Person 1's real parser should respect quoting/escaping
    tokens = re.split(r"(\&\&|\|\||;|\|)", normalized)
    sub_commands = [t.strip() for t in tokens[::2] if t.strip()]
    chain_operators = [t.strip() for t in tokens[1::2]]

    obfuscation_detected, decoded_segments = _detect_obfuscation(normalized)

    return {
        "raw": raw_command,
        "normalized": normalized,
        "sub_commands": sub_commands,
        "chain_operators": chain_operators,
        "obfuscation_detected": obfuscation_detected,
        "decoded_segments": decoded_segments,
    }


def _detect_obfuscation(command: str) -> tuple[bool, list[str]]:
    """Very naive base64 pre-detection — replace with Person 1's real logic."""
    candidates = re.findall(r"[A-Za-z0-9+/]{16,}={0,2}", command)
    decoded = []
    for c in candidates:
        try:
            decoded_bytes = base64.b64decode(c, validate=True)
            decoded_str = decoded_bytes.decode("utf-8")
            if decoded_str.isprintable():
                decoded.append(decoded_str)
        except Exception:
            continue
    return (len(decoded) > 0, decoded)
