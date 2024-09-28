import os
import requests
import json
from dotenv import load_dotenv


load_dotenv()
ati_token = os.getenv('ATI_TOKEN')

if not ati_token:
    print("ATI_TOKEN not found in .env file")

headers = {
    'Authorization': f'Bearer {ati_token}'
}

def create_order(order):
    # Create order
    response = requests.post('https://api.ati.su/v2/cargos', headers=headers, json={'cargo_application': order})
    if response.status_code == 200:
        print(f"Successfully created order with id: {order['external_id']}")
        return response.json()['cargo_application']
    else:
        print(f"Failed to create order. Status code: {response.status_code}")

        # Ensure the 'failed_create' directory exists
        os.makedirs('failed_create', exist_ok=True)

        # Create the filename using the order's external_id
        filename = f"failed_create/{order['external_id']}.json"
        print(f"Failed order data saved to {filename}")
        # Write the order data to the JSON file
        with open(filename, 'w') as f:
            json.dump(order, f, indent=4)

        print(f"Failed order data saved to {filename}")

def update_order(order_id, order):
    # Update order
    response = requests.put(f'https://api.ati.su/v2/cargos/{order_id}', headers=headers, json={'cargo_application': order})
    if response.status_code == 200:
        print(f"Successfully updated order with id: {order_id}")
    else:
        print(f"Failed to update order with id: {order_id}. Status code: {response.status_code}")

def delete_order(order_id):
    # Delete order
    delete_response = requests.delete(f'https://api.ati.su/v1.0/loads/{order_id}', headers=headers)
    if delete_response.status_code == 200:
        print(f"Successfully deleted order with id: {order_id}")
    else:
        print(f"Failed to delete order with id: {order_id}. Status code: {delete_response.status_code}")

def delete_all_orders():
    # Get loads
    response = requests.get('https://api.ati.su/v1.0/loads', headers=headers)
    if response.status_code != 200:
        print(f"Failed to get loads. Status code: {response.status_code}")
        return

    loads = response.json()

    # Delete each load
    for load in loads:
        load_id = load.get('Id')
        if load_id:
            delete_order(load_id)
