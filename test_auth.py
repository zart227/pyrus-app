from pyrus import client
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Инициализация клиента Pyrus
pyrus_client = client.PyrusAPI(
    login=os.getenv("PYRUS_LOGIN"),
    security_key=os.getenv("PYRUS_SECURITY_KEY")
)

# Попытка авторизации
auth_response = pyrus_client.auth()
print(f"Успешная авторизация: {auth_response.success}")
if not auth_response.success:
    print(f"Ошибка: {auth_response.error}") 