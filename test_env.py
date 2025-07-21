import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Вывод значений переменных
print("PYRUS_LOGIN:", os.getenv("PYRUS_LOGIN"))
print("PYRUS_SECURITY_KEY:", os.getenv("PYRUS_SECURITY_KEY")) 