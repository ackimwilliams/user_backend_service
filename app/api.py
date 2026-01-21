from __future__ import annotations

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .errors import UserNotFoundException
from .models import CreateUserRequest, UpdateEmailRequest, User
from .service import UserService


class UserController:
    """
    User service controller
    """
    def __init__(self, service: UserService):
        self._service = service

    def create_app(self) -> FastAPI:
        app = FastAPI(title="User Service", version="1.0.0")
        router = APIRouter()

        @app.exception_handler(UserNotFoundException)
        def user_not_found_handler(_, exc: UserNotFoundException):
            return JSONResponse(
                status_code=404,
                content={"error": "user_not_found", "message": str(exc), "user_id": exc.user_id},
            )

        @app.exception_handler(ValidationError)
        def validation_handler(_, exc: ValidationError):
            return JSONResponse(status_code=422, content={"error": "validation_error", "details": exc.errors()})

        @router.post("/users", response_model=User, status_code=201)
        def create_user(req: CreateUserRequest):
            return self._service.create_user(name=req.name, email=str(req.email))

        @router.get("/users/{user_id}", response_model=User)
        def get_user(user_id: int):
            return self._service.get_user(user_id)

        @router.put("/users/{user_id}/email", response_model=User)
        def update_email(user_id: int, req: UpdateEmailRequest):
            return self._service.update_user_email(user_id, email=str(req.email))

        @router.delete("/users/{user_id}", status_code=204)
        def delete_user(user_id: int):
            self._service.delete_user(user_id)
            return None

        @router.get("/health")
        def health():
            return {"status": "ok"}

        app.include_router(router)
        return app

