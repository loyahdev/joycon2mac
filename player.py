import gc
from joycon import JoyCon
from app_state import unregister_controller, register_controller



global cliente
cliente = None
class Player:
    def __init__(self, number, controller_type, side=None, task=None):
        self.number = number
        self.type = controller_type
        self.side = side
        self.clients = []
        # Explicit garbage collection to prevent reuse issues
        gc.collect()
        self.gamepad = None

    def __str__(self):
        print(f"Joy-Con: {self.number}, type: {self.type}, side: {self.side}, clients: {self.clients}")

    def attach_joycon(self, side):
        self.side = side
        self.gamepad = JoyCon(side=side)  # Initialize JoyCon instance
        try:
            register_controller(side)
        except Exception:
            pass
    
    async def disconnect(self):
        for client in self.clients:
            if client.is_connected:
                await client.disconnect()
        self.clients.clear()
        # Explicit garbage collection to prevent reuse issues
        await self.task.cancel()
        gc.collect()
        try:
            if self.side:
                unregister_controller(self.side)
        except Exception:
            pass