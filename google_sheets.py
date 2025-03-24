import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def get_worksheet(spreadsheet_id, worksheet_name):
    """Подключение к Google Sheets"""
    creds_file = os.getenv("CREDENTIALS_PATH")  # Берем путь из переменной окружения
    
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    gs_client = gspread.authorize(creds)
    return gs_client.open_by_key(spreadsheet_id).worksheet(worksheet_name)

def get_previous_data(sheet):
    """Получение предпоследней строки из Google Sheets"""
    try:
        records = sheet.get_all_records()
        return records[-2] if len(records) > 1 else None
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None