# Order Management System
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![GitHub](https://img.shields.io/github/repo-size/alexeyromanenko125-prog/order-management-system)
![GitHub](https://img.shields.io/github/last-commit/alexeyromanenko125-prog/order-management-system)
![GitHub](https://img.shields.io/github/languages/top/alexeyromanenko125-prog/order-management-system)
![GitHub issues](https://img.shields.io/github/issues/alexeyromanenko125-prog/order-management-system)
![GitHub pull requests](https://img.shields.io/github/issues-pr/alexeyromanenko125-prog/order-management-system)
![GitHub contributors](https://img.shields.io/github/contributors/alexeyromanenko125-prog/order-management-system)


Система управления заказами (OMS) с графическим интерфейсом на Python.

## Функциональность

- Управление клиентами, товарами и заказами
- Аналитика и визуализация данных
- Импорт/экспорт данных (JSON, CSV)
- Графический интерфейс на tkinter

## Установка

1. Клонируйте репозиторий:

git clone https://github.com/alexeyromanenko125-prog/order-management-system.git
cd order-management-system

2. Установите зависимости:

pip install -r requirements.txt

3. Запустите приложение:

python main.py

## Тестирование

### Запуск тестов

```bash
# Все тесты
python -m unittest discover

# Конкретный модуль
python -m unittest test_models.py
python -m unittest test_analysis.py