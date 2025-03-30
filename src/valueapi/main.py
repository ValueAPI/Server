import os
from collections import defaultdict
from typing import Dict
import urllib.parse
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import PlainTextResponse
import pickle
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

if not os.path.exists("data"):
    os.mkdir("data")
store: Dict[str, Dict[str, str]] = defaultdict(dict)
if os.path.isfile(os.path.join("data", "store.pickle")):
    store = pickle.load(open(os.path.join("data", "store.pickle"), "rb"))

need_export = False


@app.middleware("http")
async def validate_auth_token(request: Request, call_next):
    # 1. Check if there is a token and save it for later
    request_auth_token = None
    if "Authorization" in request.headers:
        request_auth_token = request.headers["Authorization"]

    # 2. Get the requested context
    context = None
    try:
        _, context, *_ = request.url.path.split("/")
    except Exception:
        pass
    if context is None or len(context) == 0:
        return PlainTextResponse("No context found", status_code=404)

    excepted_auth_token = store[context].get("auth_token", None)

    if excepted_auth_token is None or excepted_auth_token == request_auth_token:
        response = await call_next(request)
        return response
    else:
        return PlainTextResponse("Not Authorization", status_code=401)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse("", status_code=400)


@app.get("/{context}/{key}")
async def get_value(context: str, key: str):
    context = urllib.parse.unquote(context)
    key = urllib.parse.unquote(key)
    return PlainTextResponse(store[context].get(key), status_code=200)


# Simple version
@app.get("/{context}/{key}/{value}")
async def set_value(context: str, key: str, value: str):
    context = urllib.parse.unquote(context)
    key = urllib.parse.unquote(key)
    store[context][key] = value
    global need_export
    need_export = True
    return PlainTextResponse(store[context].get(key), status_code=200)


@app.post("/{context}/{key}")
async def set_value_post(request: Request, context: str, key: str):
    context = urllib.parse.unquote(context)
    key = urllib.parse.unquote(key)
    value = await request.body()
    store[context][key] = value.decode("utf-8")
    global need_export
    need_export = True
    return PlainTextResponse(store[context].get(key), status_code=200)


@app.delete("/{context}/{key}")
async def delete_value(context: str, key: str):
    context = urllib.parse.unquote(context)
    key = urllib.parse.unquote(key)
    if key in store[context]:
        del store[context][key]
        global need_export
        need_export = True
        return PlainTextResponse("deleted", status_code=200)
    return PlainTextResponse(
        f"Nothing deleted, {key=} was not present!", status_code=200
    )


def export_data():
    global need_export
    if need_export:
        need_export = False
        with open(os.path.join("data", "store.pickle"), "wb") as f:
            pickle.dump(store, f, pickle.HIGHEST_PROTOCOL)


# Set up the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(export_data, "interval", minutes=1)
scheduler.start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()
