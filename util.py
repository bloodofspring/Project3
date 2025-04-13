from Crypto.Hash import HMAC, SHA256

from database.models import AppUser


def hash_password(password: str) -> str:
    return HMAC.new(bytes(password, "utf-8"), digestmod=SHA256).hexdigest()


def authenticate(login: str, password: str) -> bool:
    users = AppUser.select().where(AppUser.login == login)[:]

    if len(users) == 0:
        return False

    return hash_password(password) == users[0].password
