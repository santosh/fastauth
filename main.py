from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from fastauth import schemas, crud, auth
from fastauth.database import DBInit

# These constants go in a specific config file
ACCESS_TOKEN_EXPIRE_MINUTES=15

def get_db():
    session = None
    try:
        session = DBInit("postgresql+psycopg2://postgres:postgres@localhost/fastauth").get_session()
        session = session()
        yield session
    finally:
        session.close()

app = FastAPI()

@app.get("/ping")
async def ping():
    return {'msg': 'pong'}

@app.post("/users/register", status_code=201, response_model=schemas.UserInfo, tags=["users"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=409, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.post("/users/auth", response_model=schemas.Token, tags=["users"])
def authenticate_user(user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user is None:
        raise HTTPException(status_code=403, detail="Username or password is incorrect")
    else:
        is_password_correct = auth.check_username_password(db, user)
        if is_password_correct is False:
            raise HTTPException(status_code=403, detail="Username or password is incorrect")
        else:
            from datetime import timedelta
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = auth.encode_jwt_token(
                data={"sub": user.username}, expires_delta=access_token_expires)
            return {"access_token": access_token, "token_type": "Bearer"}
