# encoding: utf-8
import asyncio

from pugdagd.PugdagdClient import PugdagdClient
# pipenv run python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/rpc.proto ./protos/messages.proto ./protos/p2p.proto
from pugdagd.PugdagdThread import PugdagdCommunicationError


class PugdagdMultiClient(object):
    def __init__(self, hosts: list[str]):
        self.pugdagds = [PugdagdClient(*h.split(":")) for h in hosts]

    def __get_pugdagd(self):
        for k in self.pugdagds:
            if k.is_utxo_indexed and k.is_synced:
                return k

    async def initialize_all(self):
        tasks = [asyncio.create_task(k.ping()) for k in self.pugdagds]

        for t in tasks:
            await t

    async def request(self, command, params=None, timeout=5):
        try:
            return await self.__get_pugdagd().request(command, params, timeout=timeout)
        except PugdagdCommunicationError:
            await self.initialize_all()
            return await self.__get_pugdagd().request(command, params, timeout=timeout)

    async def notify(self, command, params, callback):
        return await self.__get_pugdagd().notify(command, params, callback)
