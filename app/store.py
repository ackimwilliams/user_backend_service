from __future__ import annotations

import threading
from typing import Dict, Optional, Protocol

from .models import User


class UserStore(Protocol):
    def create(self, user: User) -> User: ...
    def get(self, user_id: int) -> Optional[User]: ...
    def update_email(self, user_id: int, email: str) -> Optional[User]: ...
    def delete(self, user_id: int) -> bool: ...


class InMemoryUserStore(UserStore):
    """
    Thread-safe, in-memory store
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._users: Dict[int, User] = {}

    def create(self, user: User) -> User:
        with self._lock:
            self._users[user.id] = user

            return User(id=user.id, name=user.name, email=user.email)

    def get(self, user_id: int) -> Optional[User]:
        with self._lock:
            u = self._users.get(user_id)
            if u is None:
                return None

            return User(id=u.id, name=u.name, email=u.email)

    def update_email(self, user_id: int, email: str) -> Optional[User]:
        with self._lock:
            u = self._users.get(user_id)

            if u is None:
                return None

            updated = User(id=u.id, name=u.name, email=email)
            self._users[user_id] = updated

            return User(id=updated.id, name=updated.name, email=updated.email)

    def delete(self, user_id: int) -> bool:
        with self._lock:
            return self._users.pop(user_id, None) is not None
