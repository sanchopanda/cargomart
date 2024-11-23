import json

# Функция для загрузки обработанных заявок
def load_processed_bids(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Функция для сохранения обработанных заявок
def save_processed_bids(bid_ids, filename):
    with open(filename, 'w') as f:
        json.dump(bid_ids, f)