from django.conf import settings
from datetime import datetime, timedelta, timezone
import jwt, random, string

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_MINUTES = 60


class Authentication:
    # generate random string
    def get_random(length: int):
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    # generate access token based and encode user's id
    def create_access_token(payload: dict):
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"exp": expire, **payload}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    # generate random refresh token
    def create_refresh_token():
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES
        )
        return jwt.encode(
            {"exp": expire, "data": Authentication.get_random(10)},
            settings.SECRET_KEY,
            algorithm=ALGORITHM,
        )
