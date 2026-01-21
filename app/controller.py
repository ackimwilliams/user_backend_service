from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .errors import UserNotFoundException
from .logging_utils import generate_request_id
from .service import UserService

logger = logging.getLogger("amex_app")

"""
@todo: consider using pydantic for field validation
"""

# email address regex
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _require_json_object(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("Request body must be a JSON object")

    return value


def _validate_name(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Field 'name' must be a string")

    name = value.strip()

    if not name:
        raise ValueError("Field 'name' must be non-empty")

    if len(name) > 200:
        raise ValueError("Field 'name' must be <= 200 characters")

    return name


def _validate_email(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Field 'email' must be a string")

    email = value.strip()

    if not email:
        raise ValueError("Field 'email' must be non-empty")

    if len(email) > 200:
        raise ValueError("Field 'email' must be <= 200 characters")

    if not _EMAIL_RE.match(email):
        raise ValueError("Field 'email' must be a valid email address")

    return email


class UserController:
    """
    Amex user service controller
    """

    def __init__(self, service: UserService, request_log: bool = True):
        self._service = service
        self._request_log = request_log

    def create_app(self) -> FastAPI:
        app = FastAPI(title="Amex User Service", version="1.0.0")

        @app.middleware("http")
        async def correlation_and_request_logging(request: Request, call_next):
            """
            Propagate request id for traceability
            """
            rid = request.headers.get("X-Request-Id") or generate_request_id()
            request.state.request_id = rid

            start = time.perf_counter()

            try:
                response = await call_next(request)
            finally:
                duration_ms = int((time.perf_counter() - start) * 1000)

                if self._request_log:
                    client_ip = request.client.host if request.client else None
                    logger.info(
                        "request",
                        extra={
                            "request_id": rid,
                            "method": request.method,
                            "path": request.url.path,
                            "status_code": getattr(locals().get("response"), "status_code"),
                            "duration_ms": duration_ms,
                            "client_ip": client_ip,
                        },
                    )

            # propagate request id
            response.headers["X-Request-Id"] = rid
            return response

        @app.exception_handler(UserNotFoundException)
        async def not_found_handler(request: Request, exc: UserNotFoundException):
            rid = getattr(request.state, "request_id")

            return JSONResponse(
                status_code=404,
                content={
                    "error": "user_not_found",
                    "message": str(exc),
                    "user_id": exc.user_id,
                    "request_id": rid
                },
            )

        @app.exception_handler(ValueError)
        async def bad_request_handler(request: Request, exc: ValueError):
            rid = getattr(request.state, "request_id")

            return JSONResponse(
                status_code=400,
                content={
                    "error": "bad_request",
                    "message": str(exc),
                    "request_id": rid
                },
            )

        @app.exception_handler(Exception)
        async def unhandled_handler(request: Request, _: Exception):
            rid = getattr(request.state, "request_id")
            logging.getLogger("app").exception("unhandled_exception", extra={"request_id": rid})

            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_error",
                    "message": "Unexpected server error",
                    "request_id": rid
                },
            )

        @app.get("/health")
        async def health():
            return {"status": "ok"}

        @app.post("/users", status_code=201)
        async def create_user(request: Request):
            payload = _require_json_object(await request.json())
            name = _validate_name(payload.get("name"))
            email = _validate_email(payload.get("email"))

            user = self._service.create_user(name=name, email=email)

            return user.to_dict()

        @app.get("/users/{user_id}")
        async def get_user(user_id: int):
            user = self._service.get_user(user_id)

            return user.to_dict()

        @app.put("/users/{user_id}/email")
        async def update_email(user_id: int, request: Request):
            payload = _require_json_object(await request.json())
            email = _validate_email(payload.get("email"))

            user = self._service.update_user_email(user_id=user_id, email=email)

            return user.to_dict()

        @app.delete("/users/{user_id}", status_code=204)
        async def delete_user(user_id: int):
            self._service.delete_user(user_id)

            return JSONResponse(status_code=204, content=None)

        return app
