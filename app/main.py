import sqlite3
import os
from typing import Annotated, Any
from datetime import datetime, timedelta, timezone
from pathlib import Path


from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from dotenv import load_dotenv
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import uvicorn
import jwt

from models import model
from forms import forms
from depend import get_conn
from db import get_all_file_type, get_user_by_username, save_tg_group, has_chat_id, get_groups


load_dotenv()
ALGORITHM = os.getenv('ALGORITHM')
SECRET_KEY = os.getenv('SECRET_KEY')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.mount("/static", StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db_conn, username: str, password: str):
    user = get_user_by_username(db_conn, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        db_conn: Annotated[sqlite3.Connection, Depends(get_conn)],
        token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = get_user_by_username(db_conn, username=username)
    if user is None:
        raise credentials_exception
    if not user.isActive:
        raise credentials_exception

    return user, db_conn




@app.post('/token/')
async def token(
        db_conn: Annotated[sqlite3.Connection, Depends(get_conn)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> model.Token:
    user = authenticate_user(db_conn, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return model.Token(access_token=access_token, token_type="bearer")


@app.post('/token/validate/')
async def token_validate(
        _: Annotated[tuple[model.User, sqlite3.Connection], Depends(get_current_user)],
):
    return JSONResponse({}, status_code=200)


@app.post('/group/create/')
async def create_group(
        group_form: Annotated[forms.GroupForm, Body()],
        user_and_db: Annotated[tuple[model.User, sqlite3.Connection], Depends(get_current_user)]

):
    if has_chat_id(user_and_db[-1], group_form.chat_id):
        raise HTTPException(
            status_code=409,
            detail="Группа с таким ID уже существует"
        )
    save_tg_group(user_and_db[-1], group_form)
    return JSONResponse({"message": "ok"}, status_code=200)


@app.get('/login/')
async def auth(request: Request):
   return templates.TemplateResponse("login.html",  {"request": request})


@app.get("/file_type/")
async def get_file_type(
        db_conn_and_user: Annotated[tuple[model.User, sqlite3.Connection], Depends(get_current_user)],
) -> list[model.FileType]:
    _, db_conn = db_conn_and_user
    return get_all_file_type(db_conn)


@app.get("/admin/")
async def admin(
        request: Request
):
    return templates.TemplateResponse("admin.html",  {"request": request})


@app.get("/admin/create_group/")
async def create_group(
        request: Request
):
    return templates.TemplateResponse("create_group.html",  {"request": request})


@app.get("/admin/groups/")
async def groups(
        request: Request,
        db_conn: Annotated[sqlite3.Connection, Depends(get_conn)]
):
    return templates.TemplateResponse(
        "groups.html",
          {
              "request": request,
              "groups": get_groups(db_conn)
          }
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)