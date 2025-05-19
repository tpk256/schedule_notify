import sqlite3
import os
from typing import Annotated
from datetime import timedelta


from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends,  HTTPException, status, APIRouter
from fastapi.responses import JSONResponse


from utils import create_access_token
from models import model
from depend import get_conn, authenticate_user, get_current_user


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

router = APIRouter()


@router.post('', name="get_token")
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


@router.post('/validate/', name="validate_token")
async def token_validate(
        _: Annotated[tuple[model.User, sqlite3.Connection], Depends(get_current_user)],
):
    return JSONResponse({}, status_code=200)
