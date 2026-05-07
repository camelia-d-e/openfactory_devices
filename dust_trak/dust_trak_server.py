import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dust_trak.dust_trak_adapter import DustTrak
from opcua_base.opcua_server import OPCUAServer


class DustTrakServer(OPCUAServer):
    def __init__(self, endpoint="opc.tcp://0.0.0.0:4841", use_virtual_device=True):
        super().__init__(endpoint=endpoint, namespace="lab-usine")
        self.use_virtual_device = use_virtual_device

    async def start(self):
        await super().start()
        await self.create_equipment_node("DustTrak")

        await self.add_variable("DustTrak", "pm1_concentration", 0.0)
        await self.add_variable("DustTrak", "pm2_5_concentration", 0.0)
        await self.add_variable("DustTrak", "pm4_concentration", 0.0)
        await self.add_variable("DustTrak", "pm10_concentration", 0.0)

        if not self.use_virtual_device:
            self.adapter = DustTrak()
            self.adapter.start_capture()
        else:
            self.adapter = DustTrak(virtual=True)

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
            if not self.use_virtual_device:
                self.adapter.stop_capture()


if __name__ == "__main__":
    asyncio.run(DustTrakServer().run())
