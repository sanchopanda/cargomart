import logging
import json
from time import sleep
from ozon.ids_manager import load_processed_bids, save_processed_bids
from ozon.cookies_manager import load_cookies
from ozon.ozon_parser import get_biddings_list, get_bidding_details

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Ozon:
    def __init__(self):
        self.cookies = load_cookies()
        self.processed_bids_file = "processed_bids.json"
        self.details_file = "bidding_details.json"
        self.processed_bids = load_processed_bids(self.processed_bids_file)
        self.detailed_bids_data = []

    def get_orders(self):
        bid_ids = get_biddings_list(self.cookies, self.processed_bids)[:2]

        for bid_id in bid_ids:
            logging.info(f"Начата обработка заявки с ID: {bid_id}")
            try:
                details = get_bidding_details(self.cookies, bid_id)
                if details:
                    self.detailed_bids_data.append(details)
                    self.processed_bids.append(bid_id)  # Добавляем ID в список обработанных
                    logging.info(f"Успешно обработана заявка с ID: {bid_id}")
                else:
                    logging.warning(f"Не удалось получить детали для заявки с ID: {bid_id}")
            except Exception as e:
                logging.error(f"Ошибка при обработке заявки с ID: {bid_id}: {e}")
            sleep(1)

        # Сохраняем обновленный список обработанных заявок
        save_processed_bids(self.processed_bids, self.processed_bids_file)

        # Сохранение подробных данных о каждой заявке
        with open(self.details_file, "w", encoding="utf-8") as f:
            json.dump(self.detailed_bids_data, f, ensure_ascii=False, indent=4)
        logging.info("Обработка заявок завершена.")