class UserIds:
    def __init__(self):
        with open('data/users_ids.txt', 'r') as file:
            self.users_ids = list(map(lambda x: x.strip(), file.readlines()))

    def add_user_id(self, user_id):
        if user_id not in self.users_ids:
            self.users_ids.append(user_id)
            self._write_user_ids()

    def remove_user_id(self, user_id):
        if user_id in self.users_ids:
            self.users_ids.remove(user_id)
            self._write_user_ids()

    def _write_user_ids(self):
        with open('data/users_ids.txt', 'w') as file:
            for _id in self.users_ids:
                file.write(f'{_id}\n')


user_ids = UserIds()
