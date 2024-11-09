import logging
import json
from time import sleep
from ids_manager import load_processed_bids, save_processed_bids
from cookies_manager import load_cookies
from ozon_parser import get_biddings_list, get_bidding_details

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Основная функция
def main():
    cookies = load_cookies()
    
    # Загрузим ранее обработанные заявки
    processed_bids = load_processed_bids("processed_bids.json")
    
    # Получим новые заявки, которые еще не были обработаны
    bid_ids = get_biddings_list(cookies, processed_bids)[:2]
    detailed_bids_data = []

    for bid_id in bid_ids:
        logging.info(f"Начата обработка заявки с ID: {bid_id}")
        try:
            details = get_bidding_details(cookies, bid_id)
            if details:
                detailed_bids_data.append(details)
                processed_bids.append(bid_id)  # Добавляем ID в список обработанных
                logging.info(f"Успешно обработана заявка с ID: {bid_id}")
            else:
                logging.warning(f"Не удалось получить детали для заявки с ID: {bid_id}")
        except Exception as e:
            logging.error(f"Ошибка при обработке заявки с ID: {bid_id}: {e}")
        sleep(1)

    # Сохраняем обновленный список обработанных заявок
    save_processed_bids(processed_bids, "processed_bids.json")

    # Сохранение подробных данных о каждой заявке
    with open("bidding_details.json", "w", encoding="utf-8") as f:
        json.dump(detailed_bids_data, f, ensure_ascii=False, indent=4)
    logging.info("Обработка заявок завершена.")

if __name__ == "__main__":
    main()