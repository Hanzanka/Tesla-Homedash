from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Set
if TYPE_CHECKING:
    from .vehicle import Vehicle
from websockets.asyncio.server import serve
from websockets.asyncio.server import ServerConnection
from json import loads
from websockets import ConnectionClosed
import asyncio


class TeslaDataServer:
    def __init__(self, vehicle: Vehicle = None):
        self.__vehicle = vehicle
        self.__active_connections: dict[ServerConnection, set[str]] = {}

    async def __handler(self, websocket: ServerConnection) -> None:
        self.__active_connections[websocket] = set()
        try:
            async for message in websocket:
                data = loads(message)
                action = data["action"]
                match action:
                    case "subscribe":
                        properties = data["properties"]
                        for prop in properties:
                            self.__active_connections[websocket].add(prop)

                    case "unsubscribe":
                        properties = data["properties"]
                        for prop in properties:
                            self.__active_connections[websocket].discard(prop)

                    case "request":
                        properties = data["properties"]
                        data_properties = await self.__vehicle.get_data_properties_as_json(properties)
                        print(data_properties)
                        await websocket.send(data_properties)
                    
                    case "test stop":
                        self.__stop.set_result("stop server")

        except ConnectionClosed:
            pass

    async def __send_update(self) -> None:
        pass

    async def start(self) -> None:
        self.__stop = asyncio.get_running_loop().create_future()
        async with serve(handler=self.__handler, host="localhost", port=6969):
            await self.__stop

    def set_vehicle(self, vehicle: Vehicle):
        self.__vehicle = vehicle
