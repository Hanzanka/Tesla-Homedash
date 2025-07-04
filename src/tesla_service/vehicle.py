import asyncio
from ..utils.config_parser import ConfigUtils
from .vehicle_data_property import VehicleDataProperty


class Vehicle:
    def __init__(self, vin: str):
        self.__vin = vin
        self.__asleep = False
        self.__data = {}
        self.__async_lock = asyncio.Lock()
        self.__load_data_properties()

    def __load_data_properties(self) -> None:
        data_property_config = ConfigUtils.get_config()["tesla data"]
        for data_property_id, config in data_property_config.items():
            self.__data[data_property_id] = VehicleDataProperty(
                data_id=data_property_id,
                category=config["category"],
                unit=config["unit"],
                formula=config["formula"],
                log=config["log"]
            )

    def on_telemetry_event(self, data) -> None:
        asyncio.create_task(coro=self.__update(data=data))

    async def __update(self, data) -> None:
        if data["vin"] != self.__vin:
            return
        
        if "timestamp" not in data:
            return
        timestamp = data["timestamp"]
        
        if "data" not in data:
            if "state" in data:
                online = data["state"] == "online"
                await self.__data["VehicleOnline"].update(value=online, timestamp=timestamp)
            return
        
        async with self.__async_lock:
            vehicle_data = data["data"]
            tasks = []
            for data_property_id, value in vehicle_data.items():
                if data_property_id not in self.__data:
                    continue
                task = asyncio.create_task(
                    coro=self.__data[data_property_id].update(
                        value=value, timestamp=timestamp
                    )
                )
                tasks.append(task)
            await asyncio.gather(*tasks)

    @property
    def vin(self) -> str:
        return self.__vin
