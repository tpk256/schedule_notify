import sqlite3
import os
from typing import Annotated
from datetime import timedelta

from pymongo import MongoClient
from pymongo.synchronous.collection import Collection
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status, Request, Form, Body, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

from models import model
from forms import forms
from depend import get_current_user, get_conn
from db import save_tg_group, has_chat_id, get_edu_groups

router = APIRouter()


@router.post('', name='api_create_group')
async def create_group(
        group_form: Annotated[forms.GroupForm, Body()],
        db_conn: Annotated[sqlite3.Connection, Depends(get_conn)],
        _: Annotated[model.User, Depends(get_current_user)]
):

    if has_chat_id(db_conn, group_form.chat_id):
        raise HTTPException(
            status_code=409,
            detail="Группа с таким ID уже существует"
        )
    save_tg_group(db_conn, group_form)
    return JSONResponse({"message": "ok"}, status_code=200)


@router.get('/edu_group/', name='get_edu_group')
async def edu_groups(db_conn: Annotated[sqlite3.Connection, Depends(get_conn)]) -> list[model.EduGroup]:
    return get_edu_groups(db_conn)
