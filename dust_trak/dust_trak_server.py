from opcua_base.opcua_server import OPCUAServer
from dust_trak.dust_trak_adapter import DustTrak
import asyncio


class DustTrakServer(OPCUAServer):
    def __init__(self, endpoint="opc.tcp://localhost:4841"):
        super().__init__(endpoint=endpoint, namespace="lab-usine")

    async def start(self):
        await super().start()
        await self.create_equipment_node("DustTrak")

        await self.add_variable("DustTrak", "pm1_concentration", 0.0)
        await self.add_variable("DustTrak", "pm2_5_concentration", 0.0)
        await self.add_variable("DustTrak", "pm4_concentration", 0.0)
        await self.add_variable("DustTrak", "pm10_concentration", 0.0)

        self.adapter = DustTrak()
        self.adapter.start_capture()

    async def run(self):
        await self.start()
        try:
            while True:
                data = self.adapter.read_data()
                for key, value in data.items():
                    await self.set_value("DustTrak", key, value)
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            self.adapter.stop_capture()
            await self.stop()


if __name__ == "__main__":
    asyncio.run(DustTrakServer().run())