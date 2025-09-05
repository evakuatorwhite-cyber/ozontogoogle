import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict
import logging

class GoogleSheetsManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.setup_client()
    
    def setup_client(self):
        """Настройка клиента Google Sheets"""
        try:
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file"
            ]
            
            creds_path = self.config.get('GOOGLE_CREDS_PATH')
            if not creds_path or not os.path.exists(creds_path):
                raise FileNotFoundError("Файл google-credentials.json не найден")
            
            self.creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            self.client = gspread.authorize(self.creds)
            
            # Открываем таблицу
            spreadsheet_id = self.config.get('SPREADSHEET_ID')
            if not spreadsheet_id:
                raise ValueError("SPREADSHEET_ID не указан в настройках")
            
            self.spreadsheet = self.client.open_by_key(spreadsheet_id)
            self.sheet = self.spreadsheet.sheet1
            
            self.logger.info("✅ Успешное подключение к Google Таблицам")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка подключения к Google Таблицам: {e}")
            raise
    
    def initialize_sheet(self):
        """Инициализация структуры таблицы"""
        try:
            # Заголовки
            headers = [['Артикул продавца', 'Название товара', 'Актуальная цена', 'Рекомендованная цена', 'Статус']]
            
            self.sheet.clear()
            self.sheet.update('A1:E1', headers)
            
            # Форматирование заголовков
            self.sheet.format('A1:E1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            
            self.logger.info("✅ Структура таблицы инициализирована")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации таблицы: {e}")
            raise
    
    def update_sheet(self, products: List[Dict], recommended_prices: Dict) -> bool:
        """Обновление данных в таблице"""
        try:
            self.initialize_sheet()
            
            # Подготавливаем данные
            data_to_update = []
            for product in products:
                offer_id = product['offer_id']
                recommended_price = recommended_prices.get(offer_id, 'Не указана')
                
                data_to_update.append([
                    offer_id,
                    product['name'],
                    product['price'],
                    recommended_price,
                    '✅ В наличии'
                ])
            
            # Записываем данные
            if data_to_update:
                range_start = f'A2:E{len(data_to_update) + 1}'
                self.sheet.update(range_start, data_to_update)
                self.logger.info(f"✅ Обновлено {len(data_to_update)} товаров")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления таблицы: {e}")
            return False