import sqlite3
from typing import Annotated

from fastapi import FastAPI
from fastapi import Depends
import uvicorn

from models import model
from depend import get_conn
from db import get_all_file_type


app = FastAPI()


@app.get("/file_type/")
async def get_file_type(db_conn: Annotated[sqlite3.Connection, Depends(get_conn)]) -> list[model.FileType]:
    return get_all_file_type(db_conn)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)