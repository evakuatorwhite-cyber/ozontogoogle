import pandas as pd
from typing import List, Dict
import logging

class OzonAPI:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def get_available_products(self) -> List[Dict]:
        """Получение товаров из Ozon (заглушка)"""
        self.logger.info("📦 Получаем товары из Ozon (тестовые данные)")
        
        # Тестовые данные - в реальности здесь будет Ozon API
        mock_products = [
            {'offer_id': '12345', 'name': 'Смартфон Xiaomi Redmi Note 12', 'price': 19999, 'stock': 15},
            {'offer_id': '67890', 'name': 'Наушники Sony WH-1000XM4', 'price': 29999, 'stock': 8},
            {'offer_id': '11111', 'name': 'Чехол для iPhone 14 Pro', 'price': 2499, 'stock': 0},
            {'offer_id': '22222', 'name': 'Power Bank 20000 mAh', 'price': 4499, 'stock': 25},
            {'offer_id': '33333', 'name': 'Умные часы Amazfit GTS 4', 'price': 12999, 'stock': 3}
        ]
        
        # Фильтруем товары в наличии
        available_products = [
            product for product in mock_products 
            if product['stock'] > 0
        ]
        
        self.logger.info(f"✅ Найдено {len(available_products)} товаров в наличии")
        return available_products
    
    def load_recommended_prices(self) -> Dict:
        """Загрузка рекомендованных цен из Excel"""
        try:
            excel_path = self.config.get('EXCEL_FILE_PATH')
            
            if not os.path.exists(excel_path):
                self.logger.warning("⚠️ Excel файл не найден")
                return {}
            
            df = pd.read_excel(excel_path)
            recommended_prices = {}
            
            for _, row in df.iterrows():
                offer_id = str(row.iloc[0]).strip()
                price = row.iloc[1]
                recommended_prices[offer_id] = price
            
            self.logger.info(f"✅ Загружено {len(recommended_prices)} рекомендованных цен")
            return recommended_prices
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки Excel: {e}")
            return {}