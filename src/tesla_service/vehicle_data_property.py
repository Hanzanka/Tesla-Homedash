import asyncio
from sympy import symbols, sympify
from influxdb_client import Point, WritePrecision
import datetime
from datetime import timezone
from json import dumps


class VehicleDataProperty:
    def __init__(
        self,
        data_id: str,
        category: str,
        vehicle,
        unit: str = None,
        formula: str = None,
        log: bool = False,
    ):
        self.__id = data_id
        self.__category = category
        self.__unit = unit
        self.__value = None
        self.__timestamp = None
        self.__formula = formula
        if self.__formula is not None:
            self.__sympy_x = symbols("x")
            self.__sympy_expr = sympify(self.__formula)
        self.__log = log
        self.__async_lock = asyncio.Lock()
        self.__vehicle = vehicle
        self.__value_type = None

    async def update(self, value, timestamp) -> None:
        if value is None:
            return
        if self.__value_type is None:
            if isinstance(value, bool):
                self.__value_type = "value_bool"
            elif isinstance(value, int) or isinstance(value, float):
                self.__value_type = "value_float"
            elif isinstance(value, str):
                self.__value_type = "value_string"
            elif isinstance(value, dict):
                self.__value_type = "value_dict"
        async with self.__async_lock:
            if self.__formula is not None:
                self.__value = float(
                    self.__sympy_expr.subs(self.__sympy_x, value).evalf()
                )
            else:
                if self.__value_type == "value_float":
                    self.__value = float(value)
                else:
                    self.__value = value
            self.__timestamp = timestamp

    async def get_value(self):
        async with self.__async_lock:
            return self.__value

    async def get_id(self):
        async with self.__async_lock:
            return self.__id

    async def get_category(self):
        async with self.__async_lock:
            return self.__category

    async def get_unit(self):
        async with self.__async_lock:
            return self.__unit

    async def get_logging(self):
        async with self.__async_lock:
            return self.__log

    async def get_value_type(self):
        async with self.__async_lock:
            return self.__value_type

    async def get_influxdb_point(self) -> Point:
        async with self.__async_lock:
            if self.__value is None or self.__timestamp is None:
                return
            try:
                point = (
                    Point("tesla_data")
                    .tag("vin", self.__vehicle.vin)
                    .tag("category", self.__category)
                    .tag("id", self.__id)
                    .time(
                        datetime.datetime.fromtimestamp(self.__timestamp / 1000, tz=timezone.utc),
                        WritePrecision.MS,
                    )
                )
                if self.__value_type == "value_dict":
                    for key, value in self.__value.items():
                        point = point.field(key, value)
                else:
                    point = point.field(self.__value_type, self.__value)
                return point
            except Exception as e:
                print(e)
                return
    
    async def get_as_json(self) -> str:
        async with self.__async_lock:
            data = {
                "id": self.__id,
                "category": self.__category,
                "unit": self.__unit,
                "value": self.__value,
                "value_type": self.__value_type,
                "timestamp": self.__timestamp
            }
            return dumps(data)

    async def get_as_dict(self) -> dict:
        async with self.__async_lock:
            data = {
                "id": self.__id,
                "category": self.__category,
                "unit": self.__unit,
                "value": self.__value,
                "value_type": self.__value_type,
                "timestamp": self.__timestamp
            }
            return data
