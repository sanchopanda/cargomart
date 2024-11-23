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
        return response.json().get('cargo_application', {})
    else:
        print(f"Failed to create order. Status code: {response.status_code} order_id: {order['external_id']}")
        
        # Attempt to parse JSON response
        try:
            error_data = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Response content is not valid JSON. {response}")
            error_data = {
                'status': 'failed',
                'code': response.status_code
            }

        if 'reason' in error_data:
            print(f"Reason: {error_data['reason']}")
            if 'error_list' in error_data and error_data['error_list']:
                print(f"Detailed reason: {error_data['error_list'][0]['reason']}")

        # Ensure the 'failed_create' directory exists
        # os.makedirs('failed_create', exist_ok=True)

        # # Create the filename using the order's external_id
        # external_id = order['external_id'].split('3D')[-1] if '3D' in order['external_id'] else order['external_id']
        # external_id = order['external_id'].replace("https://lk.logistpro.su/Tender/Details/", "")
        # filename = f"failed_create/{external_id}.json"
        
        # # Write the order data to the JSON file
        # with open(filename, 'w') as f:
        #     json.dump(order, f, indent=4)

        # print(f"Failed order data saved to {filename}")

        return {
            "status": "failed",
            "code": response.status_code
        }

def update_order(order_id, order):
    # Update order
    response = requests.put(f'https://api.ati.su/v2/cargos/{order_id}', headers=headers, json={'cargo_application': order})
    if response.status_code == 200:
        print(f"Successfully updated order with id: {order_id}")
        return response.json()['cargo_application']
    else:
        print(f"Failed to update order with id: {order_id}. Status code: {response.status_code}")
        external_id = order['external_id'].split('3D')[-1] if '3D' in order['external_id'] else order['external_id']
        filename = f"failed_updated/{external_id}.json"
        os.makedirs('failed_updated', exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(order, f, indent=4)

def delete_order(order_id, external_id=None):
    # Delete order
    delete_response = requests.delete(f'https://api.ati.su/v1.0/loads/{order_id}', headers=headers)
    if delete_response.status_code == 200:
        print(f"Successfully deleted order with id: {order_id} and external_id: {external_id}")
    else:
        print(f"Failed to delete order with id: {order_id}. Status code: {delete_response.status_code}")

def delete_all_orders():
    # Get loads
    orders = get_api_orders()
    print(orders)
    # Delete each load
    for order_id, order_data in orders.items():
        if 'Id' in order_data:
            delete_order(order_data['Id'])
        elif 'cargo_id' in order_data:
            delete_order(order_data['cargo_id'])

def get_api_orders():
    # Get loads from ATI API
    response = requests.get('https://api.ati.su/v1.0/loads', headers=headers)
    if response.status_code != 200:
        print(f"Failed to get loads. Status code: {response.status_code}")
        return None

    loads = response.json()

    # Filter and transform the loads
    filtered_orders = {}
    for order in loads:
        if order.get('Source') == 'public-cargos-api':
            order_number = order.get('OrderNumber')
            if order_number:
                filtered_orders[order_number] = {
                    'cargo_id': order.get('Id'),
                    'payment': {
                        'rate_with_vat': order.get('Payment', {}).get('SumWithNDS')
                    },
                    'contacts': [order.get('ContactId1')] if order.get('ContactId1') else []
                }

    return filtered_orders
