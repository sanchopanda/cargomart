from cargomart.main import Cargomart
import asyncio

cargomart = Cargomart()

orders = asyncio.run(cargomart.get_orders())
print(orders)