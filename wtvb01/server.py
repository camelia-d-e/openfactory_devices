import asyncio

from opcua_base.opcua_server import OPCUAServer
from wtvb01.adapter import WTVB01


class WTVB01Server(OPCUAServer):
    def __init__(self, endpoint="opc.tcp://0.0.0.0:4842", use_virtual_device=True):
        super().__init__(endpoint=endpoint, namespace="lab-usine")
        self.adapter = WTVB01(virtual=use_virtual_device)
        if not use_virtual_device:
            if not self.adapter.connected:
                raise ValueError(f"WTVB01 sensor not connected on port {self.adapter.port}")

    async def start(self):
        await super().start()
        await self.create_equipment_node("WTVB01")

        await self.add_variable("WTVB01", "temp", 0.0)
        # acceleration
        await self.add_variable("WTVB01", "acc_x", 0.0)
        await self.add_variable("WTVB01", "acc_y", 0.0)
        await self.add_variable("WTVB01", "acc_z", 0.0)
        # velocity
        await self.add_variable("WTVB01", "vx", 0.0)
        await self.add_variable("WTVB01", "vy", 0.0)
        await self.add_variable("WTVB01", "vz", 0.0)
        # angles
        await self.add_variable("WTVB01", "angle_x", 0.0)
        await self.add_variable("WTVB01", "angle_y", 0.0)
        await self.add_variable("WTVB01", "angle_z", 0.0)
        # displacements
        await self.add_variable("WTVB01", "dx", 0.0)
        await self.add_variable("WTVB01", "dy", 0.0)
        await self.add_variable("WTVB01", "dz", 0.0)
        # frequencies
        await self.add_variable("WTVB01", "hx", 0.0)
        await self.add_variable("WTVB01", "hy", 0.0)
        await self.add_variable("WTVB01", "hz", 0.0)

       

    async def run(self):
        await self.start()
        try:
            while True:
                data = self.adapter.read_data()
                for key, value in data.items():
                    await self.set_value("WTVB01", key, value)
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()


if __name__ == "__main__":
    asyncio.run(WTVB01Server().run())