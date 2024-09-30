from cargomart.main import Cargomart
import asyncio
import os
import requests
from dotenv import load_dotenv
from cargomart.ati_crud import delete_all_orders, delete_order, create_order, update_order
import time
import json
import os

# load_dotenv()
# ati_token = os.getenv('ATI_TOKEN')

# if not ati_token:
#     print("ATI_TOKEN not found in .env file")

# headers = {
#     'Authorization': f'Bearer {ati_token}'
# }

ORDERS_FILE = 'cargomart/existed_orders.json'
# delete_all_orders()

cargomart = Cargomart()

orders = {}
while True:
    # Load existing orders from file
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            orders = json.load(f)
    else:
        orders = {}

    new_orders = asyncio.run(cargomart.get_orders())
    
    for order_id, new_order in new_orders.items():
        if order_id not in orders:
            # Create new order
            result = create_order(new_order)
            
            orders[order_id] = result
               
        elif orders[order_id] is not None:
            # Check if rate has changed
            new_rate = int(new_order['payment']['rate_with_vat'])
            old_rate = int(orders[order_id]['payment']['rate_with_vat'])
            
            if int(float(new_rate)) != int(float(old_rate)):
                # Update order
                result = update_order(order_id, new_order)
                orders[order_id] = result

    # Check for orders to delete
    for order_id in list(orders.keys()):
        if order_id not in new_orders and orders[order_id] is not None:
            cargo_id = orders[order_id]['cargo_id']
            delete_order(cargo_id)
            del orders[order_id]

    # Save updated orders to file
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f)

    # Wait for 5 minutes
    time.sleep(60)