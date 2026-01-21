from __future__ import annotations

import threading
from typing import Optional

from .errors import UserNotFoundException
from .models import User
from .store import UserStore


class AtomicCounter:
    """
    Prevent race conditions
    """
    def __init__(self, start: int = 1):
        self._value = start
        self._lock = threading.Lock()

    def next(self) -> int:
        with self._lock:
            v = self._value
            self._value += 1
            return v


class UserService:
    def __init__(self, store: UserStore, id_counter: Optional[AtomicCounter] = None):
        self._store = store
        self._counter = id_counter or AtomicCounter(start=1)

    def create_user(self, name: str, email: str) -> User:
        user_id = self._counter.next()

        return self._store.create(User(id=user_id, name=name, email=email))

    def get_user(self, user_id: int) -> User:
        user = self._store.get(user_id)

        if user is None:
            raise UserNotFoundException(user_id)

        return user

    def update_user_email(self, user_id: int, email: str) -> User:
        updated = self._store.update_email(user_id, email)

        if updated is None:
            raise UserNotFoundException(user_id)

        return updated

    def delete_user(self, user_id: int):
        deleted = self._store.delete(user_id)

        if not deleted:
            raise UserNotFoundException(user_id)
