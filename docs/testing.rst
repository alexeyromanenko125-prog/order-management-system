Тестирование
============

Запуск тестов
-------------



   # Все тесты
   python -m unittest discover

   # Конкретные модули
   python -m unittest test_models.py
   python -m unittest test_analysis.py

   # С покрытием
   coverage run -m unittest discover
   coverage report

Структура тестов
----------------

* ``test_models.py`` - Тесты моделей данных
* ``test_analysis.py`` - Тесты анализа данных
