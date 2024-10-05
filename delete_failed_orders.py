
from ati.ati_crud import delete_order
import os
import json

orders = {}

ORDERS_FILE = 'ati/existed_orders.json'

if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, 'r') as f:
        orders = json.load(f)
else:
    orders = {}

for order_id in list(orders.keys()):
    if orders[order_id] is None or orders[order_id].get('status') == 'failed':
        print(f"Deleting order with id: {order_id} - {orders[order_id]}")
        del orders[order_id]
        
with open(ORDERS_FILE, 'w') as f:
    json.dump(orders, f)
           