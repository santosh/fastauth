import datetime
import time

import bcrypt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session

from . import models, schemas, crud


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
JWT_ALGORITHM = "HS256"

def check_username_password(db: Session, user: schemas.UserAuthenticate):
    db_user_info: models.UserInfo = crud.get_user_by_username(db, username=user.username)
    db_pass = db_user_info.password.encode('utf8')
    request_pass = user.password.encode('utf8')
    return bcrypt.checkpw(request_pass, db_pass)

def encode_jwt_token(*, data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str):
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=JWT_ALGORITHM)
    print(decoded_token)
    return decoded_token if decoded_token['exp'] >= time.time() else None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials : HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=401, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=401, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=401, detail="Invalid authentication code.")

    def verify_jwt(self, jwtToken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_jwt_token(jwtToken)
        except:
            payload = None

        if payload:
            isTokenValid = True
        return isTokenValid
