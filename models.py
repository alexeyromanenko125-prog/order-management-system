"""
Модуль моделей данных.

Содержит классы для представления бизнес-сущностей:
- Person: базовая персона
- Customer: клиент
- Product: товар
- Order: заказ
- OrderItem: позиция заказа
"""
import re
from datetime import datetime
from typing import List, Dict, Optional

class Person:
    """Базовый класс для представления персоны."""
    
    def __init__(self, name: str, email: str, phone: str, address: str):
        """Parameters.

        ----------
        name : str
            Полное имя персоны
        email : str
            Электронная почта
        phone : str
            Номер телефона
        address : str
            Адрес проживания
        """
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
    
    @property
    def email(self) -> str:
        """Email адрес персоны.
    
        Returns
        -------
        str
            Email адрес.
        """
        return self._email
    
    @email.setter
    def email(self, value: str):
        """Устанавливает email адрес.
    
        Parameters
        ----------
        value : str
            Новый email адрес.
        
        Raises
        ------
        ValueError
            Если email невалиден.
        """
        if not self.validate_email(value):
            raise ValueError("Неверный формат email")
        self._email = value
    
    @property
    def phone(self) -> str:
        """Номер телефона персоны.
    
        Returns
        -------
        str
            Номер телефона.
        """    
        return self._phone
    
    @phone.setter
    def phone(self, value: str):
        """Устанавливает номер телефона.
    
        Parameters
        ----------
        value : str
            Новый номер телефона.
        
        Raises
        ------
        ValueError
            Если номер телефона невалиден.
        """    
        if not self.validate_phone(value):
            raise ValueError("Неверный формат телефона")
        self._phone = value
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Проверка email с помощью регулярного выражения."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Проверка телефона с помощью регулярного выражения."""
        pattern = r'^(\+7|8|7)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
        return re.match(pattern, phone) is not None
    
    def to_dict(self) -> Dict:
        """Преобразование объекта в словарь."""
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address
        }

class Customer(Person):
    """Класс для представления клиента."""
    
    def __init__(self, customer_id: int, name: str, email: str, phone: str, address: str):
        """Parameters.

        ----------
        customer_id : int
            Уникальный идентификатор клиента
        name : str
            Полное имя клиента
        email : str
            Электронная почта
        phone : str
            Номер телефона
        address : str
            Адрес доставки
        """
        super().__init__(name, email, phone, address)
        self.customer_id = customer_id
        self.orders = []
    
    def add_order(self, order: 'Order'):
        """Добавление заказа клиенту."""
        self.orders.append(order)
    
    def get_total_spent(self) -> float:
        """Общая сумма всех заказов клиента."""
        return sum(order.total_amount for order in self.orders)

class Product:
    """Класс для представления товара."""
    
    def __init__(self, product_id: int, name: str, price: float, category: str, stock: int = 0):
        """Parameters.

        ----------
        product_id : int
            Уникальный идентификатор товара
        name : str
            Название товара
        price : float
            Цена товара
        category : str
            Категория товара
        stock : int, optional
            Количество на складе (по умолчанию 0)
        """
        self.product_id = product_id
        self.name = name
        self.price = price
        self.category = category
        self.stock = stock
    
    def update_stock(self, quantity: int):
        """Обновление количества товара на складе."""
        self.stock += quantity
        if self.stock < 0:
            self.stock = 0
    
    def to_dict(self) -> Dict:
        """Преобразование объекта в словарь."""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'stock': self.stock
        }

class OrderItem:
    """Класс для представления позиции в заказе."""
    
    def __init__(self, product: Product, quantity: int):
        """Parameters.

        ----------
        product : Product
            Товар
        quantity : int
            Количество товара
        """
        self.product = product
        self.quantity = quantity
        self.price = product.price
    
    @property
    def total_price(self) -> float:
        """Общая стоимость позиции."""
        return self.price * self.quantity
    
    def to_dict(self) -> Dict:
        """Преобразование объекта в словарь."""
        return {
            'product_id': self.product.product_id,
            'quantity': self.quantity,
            'price': self.price,
            'total_price': self.total_price
        }

class Order:
    """Класс для представления заказа."""
    
    def __init__(self, order_id: int, customer: Customer, date: Optional[datetime] = None):
        """Parameters.

        ----------
        order_id : int
            Уникальный идентификатор заказа
        customer : Customer
            Клиент, сделавший заказ
        date : datetime, optional
            Дата заказа (по умолчанию текущая дата)
        """
        self.order_id = order_id
        self.customer = customer
        self.date = date if date else datetime.now()
        self.items: List[OrderItem] = []
    
    def add_item(self, item: OrderItem):
        """Добавление позиции в заказ."""
        self.items.append(item)
    
    @property
    def total_amount(self) -> float:
        """Общая сумма заказа."""
        return sum(item.total_price for item in self.items)
    
    def to_dict(self) -> Dict:
        """Преобразование объекта в словарь."""
        return {
            'order_id': self.order_id,
            'customer_id': self.customer.customer_id,
            'date': self.date.isoformat(),
            'items': [item.to_dict() for item in self.items],
            'total_amount': self.total_amount
        }
