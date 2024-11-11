from cargomart.main import Cargomart
from logistpro.main import Logistpro
import asyncio
import os
import requests
from dotenv import load_dotenv
from ati.ati_crud import delete_all_orders, delete_order, create_order, update_order, get_api_orders
import time
import json
import os
import datetime


ORDERS_FILE = 'ati/existed_orders.json'

cargomart = Cargomart()
logistpro = Logistpro()

logistpro_orders = asyncio.run(logistpro.get_orders())
# cargomart_orders = await cargomart.get_orders()

# Merge orders
new_orders = {**logistpro_orders}

with open(ORDERS_FILE, 'w') as f:
    json.dump(new_orders, f, indent=4)