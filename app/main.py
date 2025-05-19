import os
from typing import Annotated
import sqlite3

from pymongo import MongoClient
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import uvicorn


from api import router
from depend import get_conn
from db import get_tg_groups, get_govno, has_chat_id
from utils import even_week
from models import mongo_model

load_dotenv()
ALGORITHM = os.getenv('ALGORITHM')
SECRET_KEY = os.getenv('SECRET_KEY')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
client = MongoClient(os.getenv('HOST_MONGO'), int(os.getenv('PORT_MONGO')))
mongo_db = client[os.getenv('NAME_DATABASE_MONGO')]


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.include_router(router)
app.mount("/static", StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")


def get_group(
        db_conn: Annotated[sqlite3.Connection, Depends(get_conn)],
        chat_id: int,
        edu_group_id: int
) -> mongo_model.Group | None:

    mongo_coll = mongo_db['course_form']
    gr = has_chat_id(db_conn, chat_id)
    data = get_govno(db_conn, chat_id, edu_group_id)
    if not (data and gr):
        raise HTTPException(status_code=404)

    course, edu_form, edu_group_name = data

    if not gr.is_activated:
        raise HTTPException(status_code=403)

    obj = mongo_coll.find_one({"_id": edu_form * 10 + course})
    flag_parity = even_week()
    groups = []

    for table in obj.get('tables'):
        if table.get('flag_parity') == flag_parity:
            for group in table.get('groups'):
                if group.get('name') == edu_group_name:
                    groups.append(mongo_model.Group.parse_obj(group))
                    break
    if not groups:
        groups.append(None)

    for table in obj.get('tables'):
        if table.get('flag_parity') != flag_parity:
            for group in table.get('groups'):
                if group.get('name') == edu_group_name:
                    groups.append(mongo_model.Group.parse_obj(group))
                    break
    if len(groups) == 1:
        groups.append(None)

    return tuple(groups)



@app.get('/login/')
async def auth(request: Request):
   return templates.TemplateResponse("pages/login.html",  {"request": request})


@app.get("/admin/", name='admin')
async def admin(
        request: Request
):
    return templates.TemplateResponse("pages/admin.html",  {"request": request})


@app.get("/admin/create_group/", name="form_create_group")
async def admin_create_group(
        request: Request
):
    return templates.TemplateResponse("pages/create_group.html",  {"request": request})


@app.get("/admin/groups", name="admin_groups")
async def admin_groups(
        request: Request,
        db_conn: Annotated[sqlite3.Connection, Depends(get_conn)]
):
    return templates.TemplateResponse(
          "pages/groups.html",
          {
              "request": request,
              "groups": get_tg_groups(db_conn)
          }
    )


@app.get("/schedule/{chat_id}/{edu_group_id}")
async def schedule(
        request: Request,
        groups:
        Annotated[tuple[mongo_model.Group | None, mongo_model.Group | None],
            Depends(get_group)]
):

    a, b = "Четная", "Нечетная"
    if even_week:
        a, b = b, a
    return templates.TemplateResponse(
        "pages/schedule.html",
          {
              "request": request,
              "btn1": a,
              "btn2": b,
              "second_group": groups[1],
              "first_group": groups[0]
          }
    )


@app.get("/admin/create_message/", name="admin_message")
async def create_message(
        request: Request
):

    return templates.TemplateResponse(
        "pages/create_message.html",
          {
              "request": request

          }
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)