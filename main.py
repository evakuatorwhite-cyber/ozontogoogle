import os
import sys
import logging
from datetime import datetime
from config import Config
from google_sheets import GoogleSheetsManager
from ozon_api import OzonAPI

class OzonGoogleIntegration:
    def __init__(self):
        self.config = Config()
        self.setup_logging()
        
    def setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ozon_integration.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Основной метод запуска программы"""
        self.logger.info("🚀 Запуск программы Ozon-Google интеграции")
        self.logger.info("=" * 50)
        
        try:
            # Инициализируем менеджер Google Таблиц
            sheets_manager = GoogleSheetsManager(self.config)
            
            # Инициализируем подключение к Ozon API
            ozon_api = OzonAPI(self.config)
            
            # Получаем товары из Ozon
            self.logger.info("📦 Получаем товары из Ozon...")
            products = ozon_api.get_available_products()
            
            if not products:
                self.logger.warning("⚠️ Не найдено товаров для обновления")
                return False
            
            # Загружаем рекомендованные цены
            recommended_prices = ozon_api.load_recommended_prices()
            
            # Обновляем Google таблицу
            self.logger.info("📊 Обновляем Google таблицу...")
            success = sheets_manager.update_sheet(products, recommended_prices)
            
            if success:
                self.logger.info("✅ Программа успешно завершена!")
                print("\n🎉 Готово! Проверьте вашу Google таблицу")
                return True
            else:
                self.logger.error("❌ Ошибка при обновлении таблицы")
                return False
                
        except Exception as e:
            self.logger.error(f"💥 Критическая ошибка: {e}")
            return False

def main():
    """Точка входа программы"""
    print("=" * 50)
    print("🛍️  Ozon to Google Sheets Integration")
    print("=" * 50)
    
    # Проверяем наличие файла настроек
    if not os.path.exists('.env'):
        print("⚠️  Файл настроек не найден. Запускаем первоначальную настройку...")
        from config import first_time_setup
        if first_time_setup():
            print("✅ Настройка завершена! Перезапустите программу.")
        return
    
    # Запускаем основную программу
    app = OzonGoogleIntegration()
    success = app.run()
    
    if not success:
        print("\n❌ Программа завершилась с ошибками.")
        print("📋 Проверьте файл ozon_integration.log для деталей")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

if __name__ == "__main__":
    main()