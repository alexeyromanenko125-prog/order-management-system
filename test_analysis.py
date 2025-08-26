"""
Unit-тесты для модуля analysis.py.
"""
import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

# Добавляем путь к текущей директории для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analysis import DataAnalyzer
from models import Customer, Product, Order, OrderItem

class TestDataAnalyzer(unittest.TestCase):
    """Тесты для класса DataAnalyzer."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        # Создаем mock базу данных
        self.mock_db = Mock()
        
        # Создаем тестовых клиентов
        self.customer1 = Customer(1, "Иван Иванов", "ivan@mail.com", "+79161234567", "Москва")
        self.customer2 = Customer(2, "Петр Петров", "petr@mail.com", "+79169876543", "СПб")
        self.customer3 = Customer(3, "Сидор Сидоров", "sidor@mail.com", "+79165555555", "Казань")
        
        # Создаем тестовые товары
        self.product1 = Product(1, "Телефон", 10000.0, "Электроника", 10)
        self.product2 = Product(2, "Ноутбук", 50000.0, "Электроника", 5)
        self.product3 = Product(3, "Книга", 500.0, "Книги", 20)
        
        # Создаем тестовые заказы
        self.order1 = Order(1, self.customer1, datetime.now() - timedelta(days=2))
        self.order1.add_item(OrderItem(self.product1, 2))  # 20000
        self.order1.add_item(OrderItem(self.product3, 1))  # 500
        
        self.order2 = Order(2, self.customer1, datetime.now() - timedelta(days=1))
        self.order2.add_item(OrderItem(self.product2, 1))  # 50000
        
        self.order3 = Order(3, self.customer2, datetime.now())
        self.order3.add_item(OrderItem(self.product1, 1))  # 10000
        self.order3.add_item(OrderItem(self.product3, 3))  # 1500
        
        # Настраиваем mock методы
        self.mock_db.get_all_customers.return_value = [
            self.customer1, self.customer2, self.customer3
        ]
        
        self.mock_db.get_all_orders.return_value = [
            self.order1, self.order2, self.order3
        ]
        
        self.mock_db.get_all_products.return_value = [
            self.product1, self.product2, self.product3
        ]
        
        self.analyzer = DataAnalyzer(self.mock_db)
    
    def test_get_top_customers(self):
        """Тест получения топ клиентов."""
        top_customers = self.analyzer.get_top_customers(2)
        
        # Проверяем количество возвращаемых клиентов
        self.assertEqual(len(top_customers), 2)
        
        # Проверяем порядок (по количеству заказов)
        self.assertEqual(top_customers[0][0].customer_id, 1)  # Иван - 2 заказа
        self.assertEqual(top_customers[1][0].customer_id, 2)  # Петр - 1 заказ
        
        # Проверяем статистику
        ivan_stats = next(c for c in top_customers if c[0].customer_id == 1)
        self.assertEqual(ivan_stats[1], 2)  # 2 заказа
        self.assertAlmostEqual(ivan_stats[2], 70500.0)  # 20000 + 500 + 50000
        
        petr_stats = next(c for c in top_customers if c[0].customer_id == 2)
        self.assertEqual(petr_stats[1], 1)  # 1 заказ
        self.assertAlmostEqual(petr_stats[2], 11500.0)  # 10000 + 1500
        
    def test_get_top_products_empty(self):
        """Тест получения топ товаров при пустой базе."""
        self.mock_db.get_all_orders.return_value = []
        self.mock_db.get_all_products.return_value = []
        
        top_products = self.analyzer.get_top_products()
        self.assertEqual(len(top_products), 0)
    
    def test_get_customer_connections(self):
        """Тест получения связей между клиентами."""
        connections = self.analyzer.get_customer_connections()
        
        # Проверяем узлы
        self.assertEqual(len(connections['nodes']), 3)
        
        # Проверяем наличие связей
        edges = connections['edges']
        self.assertTrue(len(edges) > 0)
        
        # Клиенты 1 и 2 должны иметь связь (общий товар 1 и 3)
        connection_found = any(
            (id1 == 1 and id2 == 2) or (id1 == 2 and id2 == 1)
            for id1, id2, weight in edges
        )
        self.assertTrue(connection_found)
    
    def test_get_customer_connections_no_common(self):
        """Тест связей когда нет общих товаров."""
        # Создаем заказы без общих товаров
        order4 = Order(4, self.customer3, datetime.now())
        order4.add_item(OrderItem(self.product2, 1))
        
        self.mock_db.get_all_orders.return_value = [order4]
        
        connections = self.analyzer.get_customer_connections()
        self.assertEqual(len(connections['edges']), 0)  # Не должно быть связей
    
    def test_get_sales_trend(self):
        """Тест получения динамики продаж."""
        trend = self.analyzer.get_sales_trend('D')
        
        # Проверяем структуру DataFrame
        self.assertIn('date', trend.columns)
        self.assertIn('orders_count', trend.columns)
        self.assertIn('total_amount', trend.columns)
        
        # Проверяем что данные не пустые
        self.assertFalse(trend.empty)

class TestDataAnalyzerEdgeCases(unittest.TestCase):
    """Тесты для крайних случаев DataAnalyzer."""
    
    def setUp(self):
        self.mock_db = Mock()
        self.analyzer = DataAnalyzer(self.mock_db)
    
    def test_single_customer_no_orders(self):
        """Тест с одним клиентом без заказов."""
        customer = Customer(1, "Test", "test@mail.com", "+79161234567", "Address")
        
        self.mock_db.get_all_customers.return_value = [customer]
        self.mock_db.get_all_orders.return_value = []

if __name__ == '__main__':
    unittest.main()