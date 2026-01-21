import unittest

from app.errors import UserNotFoundException
from app.service import AtomicCounter, UserService
from app.store import InMemoryUserStore


class TestUserService(unittest.TestCase):
    def test_create_user_and_assign_id(self):
        user_service = UserService(store=InMemoryUserStore(), id_counter=AtomicCounter(start=1))
        user = user_service.create_user("James", "james@example.com")

        self.assertEqual(user.id, 1)
        self.assertEqual(user.name, "James")
        self.assertEqual(user.email, "james@example.com")

    def test_get_user_not_found(self):
        user_service = UserService(store=InMemoryUserStore())

        with self.assertRaises(UserNotFoundException) as ctx:
            user_service.get_user(999)

        self.assertEqual(ctx.exception.user_id, 999)

    def test_get_user_success(self):
        user_service = UserService(store=InMemoryUserStore(), id_counter=AtomicCounter(start=10))
        created = user_service.create_user("Bob", "bob@example.com")
        fetched = user_service.get_user(created.id)

        self.assertEqual(fetched.id, created.id)
        self.assertEqual(fetched.name, "Bob")
        self.assertEqual(fetched.email, "bob@example.com")

    # --------------------------- updates
    def test_update_email_success(self):
        user_service = UserService(store=InMemoryUserStore(), id_counter=AtomicCounter(start=1))
        created = user_service.create_user("Carlos", "carlos@example.com")
        updated = user_service.update_user_email(created.id, "carlos@example.com")

        self.assertEqual(updated.id, created.id)
        self.assertEqual(updated.name, "Carlos")
        self.assertEqual(updated.email, "carlos@example.com")

    def test_update_email_not_found(self):
        user_service = UserService(store=InMemoryUserStore())

        with self.assertRaises(UserNotFoundException) as ctx:
            user_service.update_user_email(404, "not_found@example.com")

        self.assertEqual(ctx.exception.user_id, 404)

    def test_delete_user_success_and_then_not_found(self):
        user_service = UserService(store=InMemoryUserStore(), id_counter=AtomicCounter(start=1))
        created = user_service.create_user("Dave", "dave@example.com")

        user_service.delete_user(created.id)

        with self.assertRaises(UserNotFoundException):
            user_service.get_user(created.id)

        with self.assertRaises(UserNotFoundException):
            user_service.delete_user(created.id)


if __name__ == "__main__":
    unittest.main()
