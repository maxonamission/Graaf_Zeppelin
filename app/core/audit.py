"""Structured audit logging for security-relevant events (S11-04).

Usage:
    from app.core.audit import audit_log
    audit_log("login_success", user_id=user.id, ip=request.client.host)
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

_logger = logging.getLogger("audit")

# Ensure audit logger outputs at INFO level even if root is WARNING
if not _logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)
    _logger.propagate = False


def audit_log(
    event_type: str,
    *,
    user_id: int | None = None,
    ip: str | None = None,
    detail: str | None = None,
    **extra: Any,
) -> None:
    """Write a structured audit log entry as JSON."""
    entry: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": event_type,
        "user_id": user_id,
        "ip": ip,
    }
    if detail:
        entry["detail"] = detail
    if extra:
        entry["extra"] = extra

    _logger.info(json.dumps(entry, default=str))
