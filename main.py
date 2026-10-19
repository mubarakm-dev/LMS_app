

from src.data.connection import get_connection
from src.data.repositories.user_repo import UserRepository
from src.services.auth_service import AuthService
from src.presentation.app import App


def build():

    user_repo = UserRepository()
    auth_service = AuthService(user_repo)
    return App(auth_service)


# print(service.register("Ada", "Lovelace", "ada@example.com", "Str0ng!Pass", "Str0ng!Pass"))
# print(service.login("ada@example.com", "Str0ng!Pass"))

conn = get_connection()
print("connected:" ,conn.is_connected())
conn.close()

