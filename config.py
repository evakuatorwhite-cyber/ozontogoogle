import os
import json
from typing import Dict, Any

class Config:
    def __init__(self):
        self.settings = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из .env файла"""
        config = {}
        
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value
        else:
            # Значения по умолчанию
            config = {
                'SPREADSHEET_ID': '',
                'GOOGLE_CREDS_PATH': 'google-credentials.json',
                'EXCEL_FILE_PATH': 'recommended_prices.xlsx',
                'OZON_API_KEY': 'your_ozon_api_key_here',
                'OZON_CLIENT_ID': 'your_ozon_client_id_here'
            }
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения настройки"""
        return self.settings.get(key, default)
    
    def save_config(self, config_data: Dict[str, str]):
        """Сохранение конфигурации"""
        with open('.env', 'w', encoding='utf-8') as f:
            for key, value in config_data.items():
                f.write(f"{key}={value}\n")

def first_time_setup() -> bool:
    """Первоначальная настройка программы"""
    print("\n🎯 Первоначальная настройка программы")
    print("=" * 40)
    
    try:
        config_data = {}
        
        # Запрашиваем настройки у пользователя
        print("\n1. 📊 Настройка Google Таблицы:")
        spreadsheet_url = input("Введите URL вашей Google таблицы: ").strip()
        
        # Извлекаем ID из URL
        if '/d/' in spreadsheet_url:
            spreadsheet_id = spreadsheet_url.split('/d/')[1].split('/')[0]
        else:
            spreadsheet_id = spreadsheet_url
        
        config_data['SPREADSHEET_ID'] = spreadsheet_id
        
        print("\n2. 🔑 Настройка Ozon API (можно пропстить Enter):")
        ozon_api_key = input("Ozon API Key: ").strip() or 'your_ozon_api_key_here'
        ozon_client_id = input("Ozon Client ID: ").strip() or 'your_ozon_client_id_here'
        
        config_data['OZON_API_KEY'] = ozon_api_key
        config_data['OZON_CLIENT_ID'] = ozon_client_id
        config_data['GOOGLE_CREDS_PATH'] = 'google-credentials.json'
        config_data['EXCEL_FILE_PATH'] = 'recommended_prices.xlsx'
        
        # Сохраняем конфигурацию
        config = Config()
        config.save_config(config_data)
        
        # Создаем пример Excel файла
        create_sample_excel()
        
        print("\n✅ Настройка завершена!")
        print("📋 Следующие шалы:")
        print("1. Положите google-credentials.json в папку с программой")
        print("2. Заполните recommended_prices.xlsx вашими данными")
        print("3. Запустите программу снова")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при настройке: {e}")
        return False

def create_sample_excel():
    """Создание примера Excel файла"""
    import pandas as pd
    
    sample_data = {
        'Артикул': ['12345', '67890', '11111', '22222', '33333'],
        'Рекомендованная цена': [15000, 25000, 3000, 5000, 12000]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_excel('recommended_prices.xlsx', index=False)
    print("✅ Создан пример файла recommended_prices.xlsx")