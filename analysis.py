from typing import List, Dict, Tuple
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pandas as pd
import networkx as nx
import seaborn as sns

from models import Customer, Product, Order

class DataAnalyzer:
    """Класс для анализа и визуализации данных"""
    
    def __init__(self, db):
        """
        Parameters
        ----------
        db : Database
            Экземпляр базы данных для анализа
        """
        self.db = db
    
    def get_top_customers(self, n: int = 5) -> List[Tuple[Customer, int, float]]:
        """
        Получение топ-N клиентов по количеству заказов и общей сумме
        
        Parameters
        ----------
        n : int, optional
            Количество клиентов в топе (по умолчанию 5)
        
        Returns
        -------
        List[Tuple[Customer, int, float]]
            Список кортежей (клиент, количество заказов, общая сумма)
        """
        customers = self.db.get_all_customers()
        orders = self.db.get_all_orders()
        
        customer_stats = []
        for customer in customers:
            customer_orders = [o for o in orders if o.customer.customer_id == customer.customer_id]
            total_spent = sum(o.total_amount for o in customer_orders)
            customer_stats.append((customer, len(customer_orders), total_spent))
        
        # Сортировка по количеству заказов (по убыванию)
        customer_stats.sort(key=lambda x: x[1], reverse=True)
        
        return customer_stats[:n]
    
    def get_sales_trend(self, period: str = 'D') -> pd.DataFrame:
        """
        Получение динамики продаж по периодам
        
        Parameters
        ----------
        period : str, optional
            Период агрегации ('D' - день, 'W' - неделя, 'M' - месяц)
        
        Returns
        -------
        pd.DataFrame
            DataFrame с колонками: date, orders_count, total_amount
        """
        orders = self.db.get_all_orders()
        
        data = []
        for order in orders:
            data.append({
                'date': order.date.date(),
                'orders_count': 1,
                'total_amount': order.total_amount
            })
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # Группировка по периоду
        trend = df.resample(period).agg({
            'orders_count': 'sum',
            'total_amount': 'sum'
        }).reset_index()
        
        return trend
    
    def get_top_products(self, n: int = 5) -> List[Tuple[Product, int, float]]:
        """
        Получение топ-N товаров по количеству продаж и общей выручке
        
        Parameters
        ----------
        n : int, optional
            Количество товаров в топе (по умолчанию 5)
        
        Returns
        -------
        List[Tuple[Product, int, float]]
            Список кортежей (товар, количество продаж, общая выручка)
        """
        orders = self.db.get_all_orders()
        products = self.db.get_all_products()
        
        product_stats = {p.product_id: {'product': p, 'quantity': 0, 'revenue': 0.0} 
                        for p in products}
        
        for order in orders:
            for item in order.items:
                pid = item.product.product_id
                product_stats[pid]['quantity'] += item.quantity
                product_stats[pid]['revenue'] += item.total_price
        
        # Преобразование в список и сортировка по количеству продаж
        stats_list = [(v['product'], v['quantity'], v['revenue']) 
                     for v in product_stats.values()]
        stats_list.sort(key=lambda x: x[1], reverse=True)
        
        return stats_list[:n]
    
    def get_customer_connections(self) -> Dict[str, List[Tuple[int, int]]]:
        """
        Получение связей между клиентами (по общим товарам)
        
        Returns
        -------
        Dict[str, List[Tuple[int, int]]]
            Словарь с данными для построения графа:
            - 'nodes': список кортежей (id, имя)
            - 'edges': список кортежей (id1, id2, weight)
        """
        customers = self.db.get_all_customers()
        orders = self.db.get_all_orders()
        
        # Собираем товары для каждого клиента
        customer_products = {}
        for customer in customers:
            customer_orders = [o for o in orders if o.customer.customer_id == customer.customer_id]
            products = set()
            for order in customer_orders:
                for item in order.items:
                    products.add(item.product.product_id)
            customer_products[customer.customer_id] = products
        
        # Находим связи между клиентами (по общим товарам)
        connections = []
        customer_ids = list(customer_products.keys())
        
        for i in range(len(customer_ids)):
            for j in range(i + 1, len(customer_ids)):
                id1 = customer_ids[i]
                id2 = customer_ids[j]
                common = customer_products[id1] & customer_products[id2]
                if common:
                    connections.append((id1, id2, len(common)))
        
        return {
            'nodes': [(c.customer_id, c.name) for c in customers],
            'edges': connections
        }
    
    def plot_top_customers(self):
        """Построение графика топ клиентов"""
        top_customers = self.get_top_customers()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Топ клиентов')
        
        # График по количеству заказов
        names = [c.name for c, cnt, amt in top_customers]
        counts = [cnt for c, cnt, amt in top_customers]
        
        ax1.bar(names, counts, color='skyblue')
        ax1.set_title('По количеству заказов')
        ax1.set_ylabel('Количество заказов')
        ax1.tick_params(axis='x', rotation=45)
        
        # График по сумме заказов
        amounts = [amt for c, cnt, amt in top_customers]
        
        ax2.bar(names, amounts, color='lightgreen')
        ax2.set_title('По сумме заказов')
        ax2.set_ylabel('Сумма заказов')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_sales_trend(self):
        """Построение графика динамики продаж"""
        trend = self.get_sales_trend('W')  # По неделям
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.suptitle('Динамика продаж')
        
        # График количества заказов
        ax1.plot(trend['date'], trend['orders_count'], marker='o', color='blue')
        ax1.set_title('Количество заказов')
        ax1.set_ylabel('Заказов в неделю')
        ax1.grid(True)
        
        # График суммы заказов
        ax2.plot(trend['date'], trend['total_amount'], marker='o', color='green')
        ax2.set_title('Сумма заказов')
        ax2.set_ylabel('Сумма в неделю')
        ax2.grid(True)
        
        plt.tight_layout()
        return fig
    
    def plot_top_products(self):
        """Построение графика топ товаров"""
        top_products = self.get_top_products()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Топ товаров')
        
        # График по количеству продаж
        names = [p.name for p, qty, rev in top_products]
        quantities = [qty for p, qty, rev in top_products]
        
        ax1.bar(names, quantities, color='salmon')
        ax1.set_title('По количеству продаж')
        ax1.set_ylabel('Количество проданных единиц')
        ax1.tick_params(axis='x', rotation=45)
        
        # График по выручке
        revenues = [rev for p, qty, rev in top_products]
        
        ax2.bar(names, revenues, color='gold')
        ax2.set_title('По выручке')
        ax2.set_ylabel('Общая выручка')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_customer_graph(self):
        """Построение графа связей клиентов"""
        graph_data = self.get_customer_connections()
        
        fig = plt.figure(figsize=(10, 8))
        plt.title('Граф связей клиентов (по общим товарам)')
        
        G = nx.Graph()
        
        # Добавление узлов
        for node_id, node_name in graph_data['nodes']:
            G.add_node(node_id, name=node_name)
        
        # Добавление рёбер
        for id1, id2, weight in graph_data['edges']:
            G.add_edge(id1, id2, weight=weight)
        
        # Визуализация графа
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Узлы
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
        
        # Рёбра
        nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.5)
        
        # Подписи
        labels = {node_id: f"{node_id}\n{data['name']}" 
                for node_id, data in G.nodes(data=True)}
        nx.draw_networkx_labels(G, pos, labels, font_size=10)
        
        plt.axis('off')
        plt.tight_layout()
        return fig