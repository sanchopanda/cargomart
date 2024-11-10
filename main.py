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

# contacts = [
#     12,
#     36,
#     38,
#     39
# ]

contacts = [
    12,
    36,
    39
]

contact_index = 0

ORDERS_FILE = 'ati/existed_orders.json'
# delete_all_orders()

cargomart = Cargomart()
logistpro = Logistpro()

orders = get_api_orders()

with open(ORDERS_FILE, 'w') as f:
    json.dump(orders, f)

while True:
    # Load existing orders from file
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            orders = json.load(f)
    else:
        orders = {}

    # new_orders = asyncio.run(cargomart.get_orders())
    new_orders = asyncio.run(logistpro.get_orders())

    if len(new_orders.items()) == 0:
        break

    print(len(new_orders.items()))
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S"))
    print(orders)
    for order_id in list(orders.keys()):
        if order_id not in new_orders and orders[order_id] is not None and orders[order_id].get('status') != 'failed':
            cargo_id = orders[order_id]['cargo_id']
            delete_order(cargo_id, order_id)
            del orders[order_id]
    for order_id, new_order in new_orders.items():
        if order_id not in orders or (order_id in orders and orders[order_id] is not None and orders[order_id].get('status') == 'failed' and orders[order_id].get('code') == 403):
            # Create new order
            new_order['contacts'] = [contacts[contact_index]]
            contact_index += 1
            if contact_index >= len(contacts):
                contact_index = 0

            result = create_order(new_order)                
            # Add a small delay before creating the order
            time.sleep(0.1)
            if result.get('status') == 'failed':
                orders[order_id] = result
            else:
                orders[order_id] = {
                    'cargo_id': result['cargo_id'],
                    'payment': result['payment'],
                    'external_id': result['external_id'],
                    'contacts': result['contacts']
                }
        elif orders[order_id] is not None and orders[order_id].get('status') != 'failed':
            # Check if rate has changed
            new_rate = int(new_order['payment']['rate_with_vat'])
            old_rate = int(orders[order_id]['payment']['rate_with_vat']) if 'payment' in orders[order_id] and 'rate_with_vat' in orders[order_id]['payment'] else None

            if old_rate is not None:
                new_rate = int(float(new_rate))
                old_rate = int(float(old_rate))
            
            if int(float(new_rate)) != int(float(old_rate)):
                # Update order
                new_order['contacts'] = [orders[order_id].get('contacts')[0]]
                result = update_order(orders[order_id]['cargo_id'], new_order)
                orders[order_id] = result
    # Check for orders to delete
  

    # Save updated orders to file
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f)

    # Wait for 5 minutes
    time.sleep(60)
 