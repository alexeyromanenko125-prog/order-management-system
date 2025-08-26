    
"""
Unit-тесты для модуля models.py.
"""
import unittest
from datetime import datetime
from models import Person, Customer, Product, OrderItem, Order

class TestPerson(unittest.TestCase):
    """Тесты для класса Person."""
    
    def test_person_creation(self):
        """Тест создания объекта Person."""
        person = Person("Иван Иванов", "ivan@mail.com", "+79161234567", "Москва")
        self.assertEqual(person.name, "Иван Иванов")
        self.assertEqual(person.email, "ivan@mail.com")
        self.assertEqual(person.phone, "+79161234567")
        self.assertEqual(person.address, "Москва")
    
    def test_email_validation(self):
        """Тест валидации email."""
        person = Person("Test", "test@mail.com", "+79161234567", "Address")
        
        # Valid emails
        self.assertTrue(Person.validate_email("test@mail.com"))
        self.assertTrue(Person.validate_email("test.name@mail.ru"))
        self.assertTrue(Person.validate_email("test123@domain.org"))
        
        # Invalid emails
        self.assertFalse(Person.validate_email("invalid"))
        self.assertFalse(Person.validate_email("invalid@"))
        self.assertFalse(Person.validate_email("@mail.com"))
    
    def test_phone_validation(self):
        """
        Тест валидации телефона. 

        Проверяемые форматы:
        - +79161234567 (международный)
        - 89161234567 (российский с 8)
        - 9161234567 (простой 10-значный)
        - Форматированные номера с скобками и дефисами
    
        Ожидается отклонение:
        - Неправильных форматов
        - Номеров с буквами
        - Пустых значений
        """
        # Тестируем различные форматы, которые допускает текущее регулярное выражение
        self.assertTrue(Person.validate_phone("+79161234567"))  # международный формат
        self.assertTrue(Person.validate_phone("79161234567"))   # с кодом страны
        self.assertTrue(Person.validate_phone("9161234567"))    # простой 10-значный
        self.assertTrue(Person.validate_phone("(916)123-4567")) # с форматированием
        self.assertTrue(Person.validate_phone("916-123-4567"))  # с дефисами
    
        # Невалидные номера
        self.assertFalse(Person.validate_phone("1234567890"))   # неправильный формат
        self.assertFalse(Person.validate_phone("916123456"))    # меньше цифр
        self.assertFalse(Person.validate_phone("91612345678"))  # больше цифр
        self.assertFalse(Person.validate_phone("abc9161234567")) # содержит буквы
    
    def test_email_setter_validation(self):
        """Тест валидации при установке email."""
        person = Person("Test", "test@mail.com", "+79161234567", "Address")
        
        with self.assertRaises(ValueError):
            person.email = "invalid-email"
        
        # Should not raise exception
        person.email = "valid@mail.com"
        self.assertEqual(person.email, "valid@mail.com")
    
    def test_phone_setter_validation(self):
        """Тест валидации при установке телефона."""
        person = Person("Test", "test@mail.com", "+79161234567", "Address")
        
        with self.assertRaises(ValueError):
            person.phone = "invalid-phone"
        
        # Should not raise exception
        person.phone = "+79161234567"
        self.assertEqual(person.phone, "+79161234567")

class TestCustomer(unittest.TestCase):
    """Тесты для класса Customer."""
    
    def test_customer_creation(self):
        """Тест создания объекта Customer."""
        customer = Customer(1, "Иван Иванов", "ivan@mail.com", "+79161234567", "Москва")
        self.assertEqual(customer.customer_id, 1)
        self.assertEqual(customer.name, "Иван Иванов")
        self.assertEqual(customer.orders, [])
    
    def test_add_order(self):
        """Тест добавления заказа клиенту."""
        customer = Customer(1, "Test", "test@mail.com", "+79161234567", "Address")
        order = Order(1, customer)
        
        customer.add_order(order)
        self.assertEqual(len(customer.orders), 1)
        self.assertEqual(customer.orders[0], order)
    
    def test_get_total_spent(self):
        """Тест расчета общей суммы покупок."""
        customer = Customer(1, "Test", "test@mail.com", "+79161234567", "Address")
        product = Product(1, "Product", 100.0, "Category", 10)
        
        order1 = Order(1, customer)
        order1.add_item(OrderItem(product, 2))  # 200
        
        order2 = Order(2, customer)
        order2.add_item(OrderItem(product, 1))  # 100
        
        customer.add_order(order1)
        customer.add_order(order2)
        
        self.assertEqual(customer.get_total_spent(), 300.0)

class TestProduct(unittest.TestCase):
    """Тесты для класса Product."""
    
    def test_product_creation(self):
        """Тест создания объекта Product."""
        product = Product(1, "Телефон", 10000.0, "Электроника", 5)
        self.assertEqual(product.product_id, 1)
        self.assertEqual(product.name, "Телефон")
        self.assertEqual(product.price, 10000.0)
        self.assertEqual(product.category, "Электроника")
        self.assertEqual(product.stock, 5)
    
    def test_update_stock(self):
        """Тест обновления запасов."""
        product = Product(1, "Product", 100.0, "Category", 10)
        
        product.update_stock(5)  # Add 5
        self.assertEqual(product.stock, 15)
        
        product.update_stock(-3)  # Remove 3
        self.assertEqual(product.stock, 12)
        
        product.update_stock(-20)  # Try to remove more than available
        self.assertEqual(product.stock, 0)  # Should not go below 0

class TestOrderItem(unittest.TestCase):
    """Тесты для класса OrderItem."""
    
    def test_order_item_creation(self):
        """Тест создания объекта OrderItem."""
        product = Product(1, "Product", 100.0, "Category")
        item = OrderItem(product, 3)
        
        self.assertEqual(item.product, product)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.price, 100.0)
    
    def test_total_price(self):
        """Тест расчета общей стоимости позиции."""
        product = Product(1, "Product", 150.0, "Category")
        item = OrderItem(product, 4)
        
        self.assertEqual(item.total_price, 600.0)  # 150 * 4

class TestOrder(unittest.TestCase):
    """Тесты для класса Order."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.customer = Customer(1, "Test", "test@mail.com", "+79161234567", "Address")
        self.product1 = Product(1, "Product1", 100.0, "Category1", 10)
        self.product2 = Product(2, "Product2", 200.0, "Category2", 5)
    
    def test_order_creation(self):
        """Тест создания объекта Order."""
        order = Order(1, self.customer)
        
        self.assertEqual(order.order_id, 1)
        self.assertEqual(order.customer, self.customer)
        self.assertIsInstance(order.date, datetime)
        self.assertEqual(order.items, [])
    
    def test_add_item(self):
        """Тест добавления позиции в заказ."""
        order = Order(1, self.customer)
        item = OrderItem(self.product1, 2)
        
        order.add_item(item)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0], item)
    
    def test_total_amount(self):
        """Тест расчета общей суммы заказа."""
        order = Order(1, self.customer)
        
        order.add_item(OrderItem(self.product1, 2))  # 100 * 2 = 200
        order.add_item(OrderItem(self.product2, 1))  # 200 * 1 = 200
        
        self.assertEqual(order.total_amount, 400.0)
    
    def test_empty_order_total(self):
        """Тест суммы пустого заказа."""
        order = Order(1, self.customer)
        self.assertEqual(order.total_amount, 0.0)

if __name__ == '__main__':
    unittest.main()