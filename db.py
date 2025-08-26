"""
Модуль работы с базой данных.

Обеспечивает сохранение, загрузку и управление данными в JSON-файлах.
"""
import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from models import Customer, Product, Order, OrderItem

class Database:
    """Класс для работы с данными в CSV/JSON форматах."""
    
    def __init__(self, data_dir: str = 'data'):
        """Parameters.

        ----------
        data_dir : str, optional
            Папка для хранения данных (по умолчанию 'data')
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Файлы для хранения данных
        self.customers_file = self.data_dir / 'customers.json'
        self.products_file = self.data_dir / 'products.json'
        self.orders_file = self.data_dir / 'orders.json'
        
        # Инициализация файлов, если они не существуют
        self._init_files()
    
    def _init_files(self):
        """Инициализация файлов с пустыми данными."""
        if not self.customers_file.exists():
            self._save_data([], self.customers_file)
        
        if not self.products_file.exists():
            self._save_data([], self.products_file)
        
        if not self.orders_file.exists():
            self._save_data([], self.orders_file)
    
    def _load_data(self, file_path: Path) -> List[Dict]:
        """Загрузка данных из файла."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix == '.json':
                    return json.load(f)
                elif file_path.suffix == '.csv':
                    return list(csv.DictReader(f))
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_data(self, data: List[Dict], file_path: Path):
        """Сохранение данных в файл."""
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.suffix == '.json':
                json.dump(data, f, indent=4, ensure_ascii=False)
            elif file_path.suffix == '.csv':
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
    
    # CRUD операции для клиентов
    def add_customer(self, customer: Customer):
        """Добавление клиента."""
        customers = self._load_data(self.customers_file)
        
        # Проверка на существующий ID
        if any(c['customer_id'] == customer.customer_id for c in customers):
            raise ValueError(f"Клиент с ID {customer.customer_id} уже существует")
        
        customers.append(customer.to_dict())
        self._save_data(customers, self.customers_file)
    
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Получение клиента по ID."""
        customers = self._load_data(self.customers_file)
        
        for customer_data in customers:
            if customer_data['customer_id'] == customer_id:
                return Customer(
                    customer_data['customer_id'],
                    customer_data['name'],
                    customer_data['email'],
                    customer_data['phone'],
                    customer_data['address']
                )
        return None
    
    def get_all_customers(self) -> List[Customer]:
        """Получение всех клиентов."""
        customers = self._load_data(self.customers_file)
        return [
            Customer(
                c['customer_id'],
                c['name'],
                c['email'],
                c['phone'],
                c['address']
            ) for c in customers
        ]
    
    # CRUD операции для товаров
    def add_product(self, product: Product):
        """Добавление товара."""
        products = self._load_data(self.products_file)
        
        # Проверка на существующий ID
        if any(p['product_id'] == product.product_id for p in products):
            raise ValueError(f"Товар с ID {product.product_id} уже существует")
        
        products.append(product.to_dict())
        self._save_data(products, self.products_file)
    
    def update_product_stock(self, product_id: int, quantity: int):
        """Обновление количества товара на складе."""
        products = self._load_data(self.products_file)
        
        for product in products:
            if product['product_id'] == product_id:
                product['stock'] = max(0, product.get('stock', 0) + quantity)
                break
        
        self._save_data(products, self.products_file)
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Получение товара по ID."""
        products = self._load_data(self.products_file)
        
        for product_data in products:
            if product_data['product_id'] == product_id:
                return Product(
                    product_data['product_id'],
                    product_data['name'],
                    product_data['price'],
                    product_data['category'],
                    product_data.get('stock', 0)
                )
        return None
    
    def get_all_products(self) -> List[Product]:
        """Получение всех товаров."""
        products = self._load_data(self.products_file)
        return [
            Product(
                p['product_id'],
                p['name'],
                p['price'],
                p['category'],
                p.get('stock', 0)
            ) for p in products
        ]
    
    # CRUD операции для заказов
    def add_order(self, order: Order):
        """Добавление заказа."""
        orders = self._load_data(self.orders_file)
        products = self._load_data(self.products_file)
        
        # Проверка на существующий ID
        if any(o['order_id'] == order.order_id for o in orders):
            raise ValueError(f"Заказ с ID {order.order_id} уже существует")
        
        # Обновление количества товаров на складе
        for item in order.items:
            for product in products:
                if product['product_id'] == item.product.product_id:
                    product['stock'] = max(0, product.get('stock', 0) - item.quantity)
                    break
        
        self._save_data(products, self.products_file)
        
        # Сохранение заказа
        orders.append(order.to_dict())
        self._save_data(orders, self.orders_file)
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """Получение заказа по ID."""
        orders = self._load_data(self.orders_file)
        customers = self._load_data(self.customers_file)
        products = self._load_data(self.products_file)
        
        for order_data in orders:
            if order_data['order_id'] == order_id:
                # Находим клиента
                customer_data = next(
                    (c for c in customers if c['customer_id'] == order_data['customer_id']),
                    None
                )
                if not customer_data:
                    return None
                
                customer = Customer(
                    customer_data['customer_id'],
                    customer_data['name'],
                    customer_data['email'],
                    customer_data['phone'],
                    customer_data['address']
                )
                
                # Создаем заказ
                order = Order(
                    order_data['order_id'],
                    customer,
                    datetime.fromisoformat(order_data['date'])
                )
                
                # Добавляем товары в заказ
                for item_data in order_data['items']:
                    product_data = next(
                        (p for p in products if p['product_id'] == item_data['product_id']),
                        None
                    )
                    if product_data:
                        product = Product(
                            product_data['product_id'],
                            product_data['name'],
                            product_data['price'],
                            product_data['category'],
                            product_data.get('stock', 0)
                        )
                        order.add_item(OrderItem(product, item_data['quantity']))
                
                return order
        return None
    
    def get_all_orders(self) -> List[Order]:
        """Получение всех заказов."""
        orders = []
        order_ids = [o['order_id'] for o in self._load_data(self.orders_file)]
        
        for order_id in order_ids:
            order = self.get_order(order_id)
            if order:
                orders.append(order)
        
        return orders
    
    # Экспорт и импорт данных
    def export_to_json(self, file_path: str):
        """Экспорт всех данных в JSON файл."""
        data = {
            'customers': self._load_data(self.customers_file),
            'products': self._load_data(self.products_file),
            'orders': self._load_data(self.orders_file)
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def import_from_json(self, file_path: str):
        """Импорт данных из JSON файла."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._save_data(data.get('customers', []), self.customers_file)
        self._save_data(data.get('products', []), self.products_file)
        self._save_data(data.get('orders', []), self.orders_file)
    
    def export_to_csv(self, directory: str = 'data/exports'):
        """Экспорт данных в CSV файлы."""
        export_dir = Path(directory)
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Экспорт клиентов
        self._save_data(self._load_data(self.customers_file), export_dir / 'customers.csv')
        
        # Экспорт товаров
        self._save_data(self._load_data(self.products_file), export_dir / 'products.csv')
        
        # Экспорт заказов
        self._save_data(self._load_data(self.orders_file), export_dir / 'orders.csv')