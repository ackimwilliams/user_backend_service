from __future__ import annotations

import logging
import uvicorn

from .config import AppConfig
from .controller import UserController
from .logging_utils import configure_logging
from .service import UserService
from .store import InMemoryUserStore


def build_app():
    configuration = AppConfig.from_env()
    configure_logging(level=configuration.log_level, json_logs=configuration.log_json)

    logging.getLogger("app").info(
        "starting up",
        extra={
            "env": configuration.env,
            "host": configuration.host,
            "port": configuration.port,
            "log_level": configuration.log_level
        },
    )

    store = InMemoryUserStore()
    service = UserService(store=store)
    controller = UserController(service=service, request_log=configuration.request_log)

    return controller.create_app(), configuration


app, _config = build_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=_config.host,
        port=_config.port,
        reload=False,
        log_config=None,
    )
