import asyncio
from sympy import symbols, sympify


class VehicleDataProperty:
    def __init__(
        self,
        data_id: str,
        category: str,
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

    async def update(self, value, timestamp) -> None:
        async with self.__async_lock:
            if self.__formula is not None:
                self.__value = round(
                    self.__sympy_expr.subs(self.__sympy_x, value).evalf(), 3
                )
            else:
                self.__value = value
            self.__timestamp = timestamp
            print(
                f"Dataproperty: {self.__id} updated | value: {self.__value} {f"{self.__unit} " if self.__unit is not None else ""}| timestamp: {self.__timestamp}"
            )

    async def get_value(self):
        with self.__async_lock:
            return self.__value

    async def get_id(self):
        with self.__async_lock:
            return self.__id

    async def get_category(self):
        with self.__async_lock:
            return self.__category

    async def get_unit(self):
        with self.__async_lock:
            return self.__unit
