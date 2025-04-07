from Crypto.Hash import HMAC, SHA256

from database.models import AppUser


def authenticate(login: str, password: str) -> bool:
    users = AppUser.select().where(AppUser.login == login)[:]

    if len(users) == 0:
        return False

    password_hash = HMAC.new(bytes(password, "utf-8"), digestmod=SHA256).hexdigest()

    return password_hash == users[0].password
