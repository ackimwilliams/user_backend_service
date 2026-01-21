from __future__ import annotations

import json
import logging
import os
import sys
import time
import uuid
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        if record.exc_info:
            # add execution info
            payload["exc_info"] = self.formatException(record.exc_info)

        for extra_fields in ("request_id", "method", "path", "status_code", "duration_ms", "client_ip"):
            record = getattr(record, extra_fields)
            if record is not None:
                payload[extra_fields] = record

        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def configure_logging(level: str, json_logs: bool):
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if json_logs:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s"))

    root.addHandler(handler)


def generate_request_id() -> str:
    # generate new request id
    return uuid.uuid4().hex


def getenv_bool(name: str, default: bool) -> bool:
    """
    Handle boolean env variables
    """
    env_var = os.getenv(name)

    if env_var is None:
        return default

    return env_var.strip().lower() in ("1", "true", "yes", "y", "on")

