import datetime

import bcrypt
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
