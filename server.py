# encoding: utf-8
import os

import socketio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse

import sys
sys.path.append('/root/PUG/pugdab-socket-server')

from pugdagd.PugdagdMultiClient import PugdagdMultiClient

os.environ["PUGDAGD_HOST_1"] = "localhost:26589"

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
socket_app = socketio.ASGIApp(sio)

app = FastAPI(
    title="Pugdag REST-API server",
    description="This server is to communicate with pugdag network via REST-API",
    version=os.getenv("VERSION", "tbd"),
    contact={
        "name": "OxJosh"
    },
    license_info={
        "name": "MIT LICENSE"
    }
)

app.add_middleware(GZipMiddleware, minimum_size=500)

app.mount("/ws", socket_app)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PingResponse(BaseModel):
    serverVersion: str = "0.12.2"
    isUtxoIndexed: bool = True
    isSynced: bool = True


@app.get("/ping",
         include_in_schema=False,
         response_model=PingResponse)
async def ping_server():
    """
    Ping Pong
    """
    try:
        info = await pugdagd_client.pugdagds[0].request("getInfoRequest")
        assert info["getInfoResponse"]["isSynced"] is True

        return {
            "server_version": info["getInfoResponse"]["serverVersion"],
            "is_utxo_indexed": info["getInfoResponse"]["isUtxoIndexed"],
            "is_synced": info["getInfoResponse"]["isSynced"]
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Pugdagd not connected.")


pugdagd_hosts = []

for i in range(100):
    try:
        pugdagd_hosts.append(os.environ[f"PUGDAGD_HOST_{i + 1}"].strip())
    except KeyError:
        break

if not pugdagd_hosts:
    raise Exception('Please set at least PUGDAGD_HOST_1 environment variable.')

pugdagd_client = PugdagdMultiClient(pugdagd_hosts)


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception):
    await pugdagd_client.initialize_all()
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"
                 # "traceback": f"{traceback.format_exception(exc)}"
                 },
    )


@app.on_event("startup")
@repeat_every(seconds=60)
async def periodical_blockdag():
    await pugdagd_client.initialize_all()
