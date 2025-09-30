from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync


class InfluxDBHandler:
    def __init__(self, url: str, token: str, org: str):
        self.__url = url
        self.__token = token
        self.__org = org
        self.__client = InfluxDBClientAsync(url=url, token=token, org=org)
        self.__bucket = "data"

    async def connected(self) -> bool:
        return await self.__client.ping()

    async def close(self) -> None:
        await self.__client.close()

    async def restart(self) -> None:
        await self.close()
        self.__client = InfluxDBClientAsync(
            url=self.__url, token=self.__token, org=self.__org
        )

    async def read_tesla_data_property(
        self,
        data_property_id: str,
        relative_time: str = None,
        time_start: str = None,
        time_end: str = None,
        min_value: int = None,
        max_value: int = None,
    ) -> list:
        if (
            relative_time is not None
            and time_start is not None
            and time_end is not None
        ):
            raise ValueError(
                "relative_time must be None when time_start and time_end are not None or vise versa"
            )

        query = f'from(bucket:"{self.__bucket}")'

        if relative_time is not None:
            query += f"\n   |> range(start: {relative_time})"

        if time_start is not None and time_end is not None:
            query += f"\n   |> range(start: {time_start}, stop: {time_end})"

        query += f'''\n    |> filter(fn: (r) => r._measurement == "tesla_data")
            |> filter(fn: (r) => r._id == "{data_property_id}")
        '''

        if min_value is not None:
            query += f"""
                |> filter(fn: (r) => r._value >= {min_value})
            """
        if max_value is not None:
            query += f"""
                |> filter(fn: (r) => r._value <= {max_value})
            """

        query += '\n   |> keep(columns: ["_time", "_value"])'

        result = await self.__client.query_api().query(query=query)

        data = []
        for table in result:
            for record in table.records:
                data.append({"time": record.get_time(), "value": record.get_value()})
        return data

    async def write_tesla_data(self, points: list) -> bool:
        valid_points = [p for p in points if p is not None]
        return await self.__client.write_api().write(bucket="data", record=valid_points)
