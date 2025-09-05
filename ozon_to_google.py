import gspread
from google.oauth2.service_account import Credentials
import requests
import pandas as pd
from datetime import datetime
import time
import logging
import os
from typing import Dict, List, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ozon_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OzonGoogleIntegration:
    def __init__(self, config: Dict):
        """
        Инициализация интеграции
        
        :param config: словарь с настройками
        """
        self.config = config
        self.setup_google_client()
        
    def setup_google_client(self):
        """Настройка клиента Google Sheets"""
        try:
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file"
            ]
            
            self.creds = Credentials.from_service_account_file(
                self.config['google_credentials_path'],
                scopes=scope
            )
            self.client = gspread.authorize(self.creds)
            self.spreadsheet = self.client.open_by_key(self.config['spreadsheet_id'])
            self.sheet = self.spreadsheet.sheet1
            
            logger.info("✅ Google Sheets клиент настроен успешно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки Google клиента: {e}")
            raise
    
    def initialize_sheet(self):
        """Инициализация структуры таблицы"""
        try:
            # Заголовки столбцов
            headers = [
                ['Артикул продавца', 'Название товара', 'Актуальная цена', 'Рекомендованная цена', 'Статус']
            ]
            
            # Очищаем и устанавливаем заголовки
            self.sheet.clear()
            self.sheet.update('A1:E1', headers)
            
            # Форматирование заголовков
            self.sheet.format('A1:E1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            
            # Добавляем информацию о последнем обновлении
            self.sheet.update('G1', [['Последнее обновление:']])
            self.sheet.update('H1', [[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]])
            
            logger.info("✅ Структура таблицы инициализирована")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации таблицы: {e}")
    
    def get_ozon_products(self) -> List[Dict]:
        """
        Получение товаров из Ozon (заглушка для тестирования)
        В реальной реализации здесь будет работа с Ozon API
        """
        logger.info("📦 Получение товаров из Ozon...")
        
        # ЗАГЛУШКА - в реальности здесь будет Ozon API
        # Пример структуры данных, которую вернет Ozon API
        mock_products = [
            {'offer_id': '12345', 'name': 'Смартфон Xiaomi Redmi Note 12', 'price': 19999, 'stock': 15},
            {'offer_id': '67890', 'name': 'Наушники Sony WH-1000XM4', 'price': 29999, 'stock': 8},
            {'offer_id': '11111', 'name': 'Чехол для iPhone 14 Pro', 'price': 2499, 'stock': 0},  # Нет в наличии
            {'offer_id': '22222', 'name': 'Power Bank 20000 mAh', 'price': 4499, 'stock': 25},
            {'offer_id': '33333', 'name': 'Умные часы Amazfit GTS 4', 'price': 12999, 'stock': 3}
        ]
        
        # Фильтруем только товары в наличии
        available_products = [
            product for product in mock_products 
            if product['stock'] > 0 and product['price'] > 0
        ]
        
        logger.info(f"✅ Найдено {len(available_products)} товаров в наличии")
        return available_products
    
    def load_recommended_prices(self) -> Dict:
        """Загрузка рекомендованных цен из Excel"""
        try:
            if os.path.exists(self.config['excel_file_path']):
                df = pd.read_excel(self.config['excel_file_path'])
                recommended_prices = {}
                
                for _, row in df.iterrows():
                    offer_id = str(row.iloc[0]).strip()
                    price = row.iloc[1]
                    recommended_prices[offer_id] = price
                
                logger.info(f"✅ Загружено {len(recommended_prices)} рекомендованных цен")
                return recommended_prices
            else:
                logger.warning("⚠️ Excel файл не найден, использую пустые значения")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки Excel: {e}")
            return {}
    
    def update_google_sheet(self):
        """Основной метод обновления таблицы"""
        try:
            logger.info("🔄 Начало обновления Google таблицы...")
            
            # Получаем данные
            products = self.get_ozon_products()
            recommended_prices = self.load_recommended_prices()
            
            # Подготавливаем данные для записи
            data_to_update = []
            for product in products:
                offer_id = product['offer_id']
                recommended_price = recommended_prices.get(offer_id, 'Не указана')
                
                data_to_update.append([
                    offer_id,
                    product['name'],
                    product['price'],
                    recommended_price,
                    '✅ В наличии' if product['stock'] > 0 else '❌ Нет в наличии'
                ])
            
            # Записываем данные в таблицу (начиная со 2-й строки)
            if data_to_update:
                range_start = f'A2:E{len(data_to_update) + 1}'
                self.sheet.update(range_start, data_to_update)
            
            # Обновляем время последнего обновления
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.sheet.update('H1', [[current_time]])
            
            logger.info(f"✅ Таблица успешно обновлена! Добавлено {len(data_to_update)} товаров")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления таблицы: {e}")
            return False

def load_config() -> Dict:
    """Загрузка конфигурации"""
    return {
        'google_credentials_path': 'google-credentials.json',
        'spreadsheet_id': '1dIWkp18ehW7njKGoUUgNQ3xGl85as6cgIcUqSdiSs3o',  # ЗАМЕНИТЕ НА ВАШ ID
        'excel_file_path': 'recommended_prices.xlsx',
        'ozon_api_key': '54d139cd-2d89-4646-9524-19897c162ccd',  # Для будущей реализации
        'ozon_client_id': '222453'  # Для будущей реализации
    }

def create_sample_excel():
    """Создание примера Excel файла если его нет"""
    if not os.path.exists('recommended_prices.xlsx'):
        sample_data = {
            'Артикул': ['12345', '67890', '22222', '33333'],
            'Рекомендованная цена': [18999, 28999, 3999, 11999]
        }
        df = pd.DataFrame(sample_data)
        df.to_excel('recommended_prices.xlsx', index=False)
        print("✅ Создан пример файла recommended_prices.xlsx")

def main():
    """Основная функция"""
    print("🚀 Запуск интеграции Ozon с Google Таблицами")
    print("=" * 50)
    
    # Создаем пример Excel файла если нужно
    create_sample_excel()
    
    # Загружаем конфигурацию
    config = load_config()
    
    try:
        # Инициализируем интеграцию
        integration = OzonGoogleIntegration(config)
        
        # Инициализируем структуру таблицы
        integration.initialize_sheet()
        
        # Обновляем данные
        success = integration.update_google_sheet()
        
        if success:
            print("🎉 Программа успешно завершена!")
            print("📊 Проверьте вашу Google таблицу")
        else:
            print("❌ Возникли ошибки при выполнении. Проверьте логи.")
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print("Проверьте:")
        print("1. Файл google-credentials.json в папке")
        print("2. Правильность spreadsheet_id")
        print("3. Доступ сервисного аккаунта к таблице")

if __name__ == "__main__":
    main()