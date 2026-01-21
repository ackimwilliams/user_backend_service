class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        super().__init__(f'User with id={user_id} was not found')
        self.user_id = user_id
