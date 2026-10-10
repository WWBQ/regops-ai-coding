"""Redact configured credentials before persisting diagnostics."""

from __future__ import annotations

import os


def mask_token(text: str) -> str:
    masked = str(text)
    for name, value in os.environ.items():
        if (name.endswith(("_TOKEN", "_API_KEY", "_SECRET", "_PASSWORD"))
                and value and len(value) >= 8):
            masked = masked.replace(value, "***")
    return masked
