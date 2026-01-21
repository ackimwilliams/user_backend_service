from __future__ import annotations

import os
from dataclasses import dataclass


def _get_env(name: str, default: str) -> str:
    v = os.getenv(name)
    return default if v is None or v.strip() == "" else v.strip()


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)

    if raw is None or raw.strip() == "":
        return default

    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True, slots=True)
class AppConfig:
    env: str
    host: str
    port: int
    log_level: str
    log_json: bool
    request_log: bool

    @staticmethod
    def from_env() -> "AppConfig":
        env = _get_env("APP_ENV", "dev")
        host = _get_env("HOST", "0.0.0.0")
        port = _get_int("PORT", 8000)
        log_level = _get_env("LOG_LEVEL", "INFO").upper()
        log_json = _get_env("LOG_JSON", "true").lower() in ("1", "true", "yes", "y", "on")
        request_log = _get_env("REQUEST_LOG", "true").lower() in ("1", "true", "yes", "y", "on")

        return AppConfig(
            env=env,
            host=host,
            port=port,
            log_level=log_level,
            log_json=log_json,
            request_log=request_log,
        )

