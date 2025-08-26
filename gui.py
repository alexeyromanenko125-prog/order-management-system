import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from models import Customer, Product, Order, OrderItem
from db import Database
from analysis import DataAnalyzer

class OrderManagementApp:
    """Главное приложение для управления заказами"""
    
    def __init__(self, root: tk.Tk):
        """
        Parameters
        ----------
        root : tk.Tk
            Корневое окно приложения
        """
        self.root = root
        self.root.title("Система управления заказами")
        self.root.geometry("1920x1080")
        
        self.db = Database()
        self.analyzer = DataAnalyzer(self.db)
        
        self.current_customer: Optional[Customer] = None
        self.current_order: Optional[Order] = None
        self.order_items: List[OrderItem] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создание вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка клиентов
        self.customer_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.customer_tab, text="Клиенты")
        self._setup_customer_tab()
        
        # Вкладка товаров
        self.product_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.product_tab, text="Товары")
        self._setup_product_tab()
        
        # Вкладка заказов
        self.order_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.order_tab, text="Заказы")
        self._setup_order_tab()
        
        # Вкладка анализа
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="Анализ")
        self._setup_analysis_tab()
        
        # Вкладка администрирования
        self.admin_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.admin_tab, text="Администрирование")
        self._setup_admin_tab()
    
    def _setup_customer_tab(self):
        """Настройка вкладки клиентов"""
        # Основной фрейм с выравниванием по левому краю
        main_frame = ttk.Frame(self.customer_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, anchor='nw')
        
        # Панель управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5, anchor='nw')
    
        ttk.Button(control_frame, text="Добавить клиента", 
                  command=self._show_add_customer_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Импорт", 
                  command=self._import_customers).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Экспорт", 
                  command=self._export_customers).pack(side=tk.LEFT, padx=5)
    
        # Поиск
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5, anchor='nw')
    
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.customer_search_entry = ttk.Entry(search_frame)
        self.customer_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.customer_search_entry.bind('<KeyRelease>', self._search_customers)
    
        # Создаем стиль с видимыми границами
        style = ttk.Style()
        style.configure("Border.Treeview",
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white")
    
        style.configure("Border.Treeview.Heading",
                        background="#e0e0e0",
                        foreground="black",
                        relief="raised",
                        borderwidth=1)
    
        # Фрейм для Treeview с выравниванием по левому краю
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=5, anchor='nw')
    


        # Таблица клиентов
        columns = ("ID", "Имя", "Email", "Телефон", "Адрес")
        self.customer_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Border.Treeview",
            selectmode="browse",
            padding=0
        )
    
        self.customer_tree.column("#0", width=0, stretch=False)  # Полностью скрыть

        # Настраиваем колонки с минимальной шириной
        column_widths = {"ID": 60, "Имя": 150, "Email": 120, "Телефон": 100, "Адрес": 200}
    
        for col in columns:
            self.customer_tree.heading(col, text=col, anchor=tk.W)
            # Для столбца ID убираем растягивание и выравниваем по левому краю
            if col == "ID":
                self.customer_tree.column(col, width=60, anchor=tk.W, minwidth=60, stretch=False)
            else:
                self.customer_tree.column(col, width=column_widths.get(col, 100), 
                                    anchor=tk.W, minwidth=50, stretch=True)
    
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещаем Treeview и скроллбар
        self.customer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Добавляем чередование цветов для лучшей читаемости
        self.customer_tree.tag_configure('odd', background='#f8f8f8')
        self.customer_tree.tag_configure('even', background='white')
        
        self.customer_tree.bind('<<TreeviewSelect>>', self._on_customer_select)

        # Обновление данных
        self._update_customer_list()

    def _setup_product_tab(self):
        """Настройка вкладки товаров"""
        # Панель управления
        control_frame = ttk.Frame(self.product_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Добавить товар", 
                  command=self._show_add_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Импорт", 
                  command=self._import_products).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Экспорт", 
                  command=self._export_products).pack(side=tk.LEFT, padx=5)
        
        # Поиск
        search_frame = ttk.Frame(self.product_tab)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.product_search_entry = ttk.Entry(search_frame)
        self.product_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.product_search_entry.bind('<KeyRelease>', self._search_products)
        
        # Таблица товаров
        columns = ("ID", "Название", "Цена", "Категория", "На складе")
        self.product_tree = ttk.Treeview(
            self.product_tab, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=100, anchor=tk.W)
        
        self.product_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Обновление данных
        self._update_product_list()
    
    def _setup_order_tab(self):
        """Настройка вкладки заказов"""
        # Панель управления
        control_frame = ttk.Frame(self.order_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Новый заказ", 
                  command=self._create_new_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сохранить заказ", 
                  command=self._save_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Отменить заказ", 
                  command=self._cancel_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Импорт", 
                  command=self._import_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Экспорт", 
                  command=self._export_orders).pack(side=tk.LEFT, padx=5)
        
        # Информация о заказе
        order_info_frame = ttk.LabelFrame(self.order_tab, text="Информация о заказе")
        order_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(order_info_frame, text="Клиент:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.order_customer_label = ttk.Label(order_info_frame, text="Не выбран")
        self.order_customer_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(order_info_frame, text="Дата:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.order_date_label = ttk.Label(order_info_frame, text=datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.order_date_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(order_info_frame, text="Сумма:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.order_total_label = ttk.Label(order_info_frame, text="0.00")
        self.order_total_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Добавление товаров
        add_product_frame = ttk.Frame(self.order_tab)
        add_product_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(add_product_frame, text="Товар:").pack(side=tk.LEFT)
        self.product_combobox = ttk.Combobox(add_product_frame, state="readonly", width=30)
        self.product_combobox.pack(side=tk.LEFT, padx=5)
        self._update_product_combobox()
        
        ttk.Label(add_product_frame, text="Количество:").pack(side=tk.LEFT, padx=5)
        self.quantity_spinbox = ttk.Spinbox(add_product_frame, from_=1, to=100, width=5)
        self.quantity_spinbox.pack(side=tk.LEFT, padx=5)
        self.quantity_spinbox.set(1)
        
        ttk.Button(add_product_frame, text="Добавить", 
                  command=self._add_product_to_order).pack(side=tk.LEFT, padx=5)
        
        # Таблица товаров в заказе
        columns = ("Товар", "Цена", "Количество", "Сумма")
        self.order_items_tree = ttk.Treeview(
            self.order_tab, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.order_items_tree.heading(col, text=col)
            self.order_items_tree.column(col, width=100, anchor=tk.W)
        
        self.order_items_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Таблица всех заказов
        self.order_tree = ttk.Treeview(
            self.order_tab, columns=("ID", "Клиент", "Дата", "Сумма"), show="headings", height=8)
        
        for col in ("ID", "Клиент", "Дата", "Сумма"):
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, width=100, anchor=tk.W)
        
        self.order_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.order_tree.bind('<<TreeviewSelect>>', self._on_order_select)
        
        # Обновление данных
        self._update_order_list()
        self._clear_order_form()
    
    def _setup_analysis_tab(self):
        """Настройка вкладки анализа"""
        # Панель управления
        control_frame = ttk.Frame(self.analysis_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Топ клиентов", 
                  command=self._show_top_customers).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Динамика продаж", 
                  command=self._show_sales_trend).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Топ товаров", 
                  command=self._show_top_products).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Граф связей", 
                  command=self._show_customer_graph).pack(side=tk.LEFT, padx=5)
        
        # Область для графиков
        self.analysis_frame = ttk.Frame(self.analysis_tab)
        self.analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _setup_admin_tab(self):
        """Настройка вкладки администрирования"""
        # Экспорт/импорт всей базы
        db_frame = ttk.LabelFrame(self.admin_tab, text="База данных")
        db_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(db_frame, text="Экспорт всей базы (JSON)", 
                  command=self._export_full_db).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(db_frame, text="Импорт всей базы (JSON)", 
                  command=self._import_full_db).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(db_frame, text="Экспорт всей базы (CSV)", 
                  command=self._export_full_db_csv).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Статистика
        stats_frame = ttk.LabelFrame(self.admin_tab, text="Статистика")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(stats_frame, text="Клиентов:").pack(side=tk.LEFT, padx=5)
        self.customer_count_label = ttk.Label(stats_frame, text="0")
        self.customer_count_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(stats_frame, text="Товаров:").pack(side=tk.LEFT, padx=5)
        self.product_count_label = ttk.Label(stats_frame, text="0")
        self.product_count_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(stats_frame, text="Заказов:").pack(side=tk.LEFT, padx=5)
        self.order_count_label = ttk.Label(stats_frame, text="0")
        self.order_count_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(stats_frame, text="Общая выручка:").pack(side=tk.LEFT, padx=5)
        self.total_revenue_label = ttk.Label(stats_frame, text="0.00")
        self.total_revenue_label.pack(side=tk.LEFT, padx=5)
        
        # Обновление статистики
        self._update_stats()
    
    # Методы для работы с клиентами
    def _update_customer_list(self, customers: Optional[List[Customer]] = None):
        """Обновление списка клиентов"""
        if customers is None:
            customers = self.db.get_all_customers()
        
        self.customer_tree.delete(*self.customer_tree.get_children())
        
        for i, customer in enumerate(customers):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.customer_tree.insert("", tk.END, values=(
                customer.customer_id,
                customer.name,
                customer.email,
                customer.phone,
                customer.address
            ), tags=(tag,))
    
    def _search_customers(self, event=None):
        """Поиск клиентов"""
        search_term = self.customer_search_entry.get().lower()
        
        if not search_term:
            self._update_customer_list()
            return
        
        customers = self.db.get_all_customers()
        filtered = [
            c for c in customers 
            if (search_term in str(c.customer_id).lower() or 
                search_term in c.name.lower() or 
                search_term in c.email.lower() or 
                search_term in c.phone.lower() or 
                search_term in c.address.lower())
        ]
        
        self._update_customer_list(filtered)
    
    def _on_customer_select(self, event):
        """Обработка выбора клиента"""
        selected = self.customer_tree.focus()
        if not selected:
            return
        
        customer_id = self.customer_tree.item(selected)['values'][0]
        self.current_customer = self.db.get_customer(customer_id)
    
    def _show_add_customer_dialog(self):
        """Показ диалога добавления клиента"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить клиента")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Поля формы
        ttk.Label(dialog, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        id_entry = ttk.Entry(dialog)
        id_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(dialog, text="Имя:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(dialog, text="Email:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        email_entry = ttk.Entry(dialog)
        email_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(dialog, text="Телефон:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        phone_entry = ttk.Entry(dialog)
        phone_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(dialog, text="Адрес:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        address_entry = ttk.Entry(dialog)
        address_entry.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Отмена", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить", 
                  command=lambda: self._save_new_customer(
                      id_entry.get(),
                      name_entry.get(),
                      email_entry.get(),
                      phone_entry.get(),
                      address_entry.get(),
                      dialog
                  )).pack(side=tk.LEFT, padx=5)
        
        # Настройка веса колонок для правильного растягивания
        dialog.columnconfigure(1, weight=1)
    
    def _save_new_customer(self, customer_id: str, name: str, email: str, 
                         phone: str, address: str, dialog: tk.Toplevel):
        """Сохранение нового клиента"""
        try:
            customer = Customer(
                int(customer_id),
                name,
                email,
                phone,
                address
            )
            
            self.db.add_customer(customer)
            self._update_customer_list()
            dialog.destroy()
            messagebox.showinfo("Успех", "Клиент успешно добавлен")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверные данные: {e}")
    
    def _import_customers(self):
        """Импорт клиентов из файла"""
        file_path = filedialog.askopenfilename(
            title="Импорт клиентов",
            filetypes=(("JSON files", "*.json"), ("CSV files", "*.csv")))
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for customer_data in data:
                    self.db.add_customer(Customer(**customer_data))
            
            elif file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.db.add_customer(Customer(
                            int(row['customer_id']),
                            row['name'],
                            row['email'],
                            row['phone'],
                            row['address']
                        ))
            
            self._update_customer_list()
            messagebox.showinfo("Успех", "Клиенты успешно импортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта: {e}")
    
    def _export_customers(self):
        """Экспорт клиентов в файл"""
        file_path = filedialog.asksaveasfilename(
            title="Экспорт клиентов",
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("CSV files", "*.csv")))
        
        if not file_path:
            return
        
        try:
            customers = self.db.get_all_customers()
            data = [customer.to_dict() for customer in customers]
            
            if file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            
            elif file_path.endswith('.csv'):
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            
            messagebox.showinfo("Успех", "Клиенты успешно экспортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    # Методы для работы с товарами
    def _update_product_list(self, products: Optional[List[Product]] = None):
        """Обновление списка товаров"""
        if products is None:
            products = self.db.get_all_products()
        
        self.product_tree.delete(*self.product_tree.get_children())
        
        for product in products:
            self.product_tree.insert("", tk.END, values=(
                product.product_id,
                product.name,
                f"{product.price:.2f}",
                product.category,
                product.stock
            ))
    
    def _search_products(self, event=None):
        """Поиск товаров"""
        search_term = self.product_search_entry.get().lower()
        
        if not search_term:
            self._update_product_list()
            return
        
        products = self.db.get_all_products()
        filtered = [
            p for p in products 
            if (search_term in str(p.product_id).lower() or 
                search_term in p.name.lower() or 
                search_term in p.category.lower())
        ]
        
        self._update_product_list(filtered)
    
    def _update_product_combobox(self):
        """Обновление списка товаров в комбобоксе"""
        products = self.db.get_all_products()
        product_names = [f"{p.product_id}: {p.name} ({p.price:.2f} руб.)" for p in products]
        self.product_combobox['values'] = product_names
        if product_names:
            self.product_combobox.current(0)
    
    def _show_add_product_dialog(self):
        """Показ диалога добавления товара"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить товар")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Поля формы
        ttk.Label(dialog, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        id_entry = ttk.Entry(dialog)
        id_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(dialog, text="Название:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(dialog, text="Цена:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        price_entry = ttk.Entry(dialog)
        price_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(dialog, text="Категория:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        category_entry = ttk.Entry(dialog)
        category_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(dialog, text="Количество:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        stock_entry = ttk.Entry(dialog)
        stock_entry.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Отмена", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить", 
                  command=lambda: self._save_new_product(
                      id_entry.get(),
                      name_entry.get(),
                      price_entry.get(),
                      category_entry.get(),
                      stock_entry.get(),
                      dialog
                  )).pack(side=tk.LEFT, padx=5)
        
        dialog.columnconfigure(1, weight=1)
    
    def _save_new_product(self, product_id: str, name: str, price: str, 
                         category: str, stock: str, dialog: tk.Toplevel):
        """Сохранение нового товара"""
        try:
            product = Product(
                int(product_id),
                name,
                float(price),
                category,
                int(stock)
            )
            
            self.db.add_product(product)
            self._update_product_list()
            self._update_product_combobox()
            dialog.destroy()
            messagebox.showinfo("Успех", "Товар успешно добавлен")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверные данные: {e}")
    
    def _import_products(self):
        """Импорт товаров из файла"""
        file_path = filedialog.askopenfilename(
            title="Импорт товаров",
            filetypes=(("JSON files", "*.json"), ("CSV files", "*.csv")))
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for product_data in data:
                    self.db.add_product(Product(**product_data))
            
            elif file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.db.add_product(Product(
                            int(row['product_id']),
                            row['name'],
                            float(row['price']),
                            row['category'],
                            int(row.get('stock', 0))
                        ))
            
            self._update_product_list()
            self._update_product_combobox()
            messagebox.showinfo("Успех", "Товары успешно импортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта: {e}")
    
    def _export_products(self):
        """Экспорт товаров в файл"""
        file_path = filedialog.asksaveasfilename(
            title="Экспорт товаров",
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("CSV files", "*.csv")))
        
        if not file_path:
            return
        
        try:
            products = self.db.get_all_products()
            data = [product.to_dict() for product in products]
            
            if file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            
            elif file_path.endswith('.csv'):
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            
            messagebox.showinfo("Успех", "Товары успешно экспортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    # Методы для работы с заказами
    def _update_order_list(self):
        """Обновление списка заказов"""
        orders = self.db.get_all_orders()
        
        self.order_tree.delete(*self.order_tree.get_children())
        
        for order in orders:
            self.order_tree.insert("", tk.END, values=(
                order.order_id,
                order.customer.name,
                order.date.strftime("%Y-%m-%d %H:%M"),
                f"{order.total_amount:.2f}"
            ))
    
    def _on_order_select(self, event):
        """Обработка выбора заказа"""
        selected = self.order_tree.focus()
        if not selected:
            return
        
        order_id = self.order_tree.item(selected)['values'][0]
        self._load_order(order_id)
    
    def _load_order(self, order_id: int):
        """Загрузка заказа для просмотра"""
        order = self.db.get_order(order_id)
        if not order:
            return
        
        self.current_order = order
        self.current_customer = order.customer
        
        # Обновление информации о заказе
        self.order_customer_label.config(text=f"{order.customer.name} (ID: {order.customer.customer_id})")
        self.order_date_label.config(text=order.date.strftime("%Y-%m-%d %H:%M"))
        self.order_total_label.config(text=f"{order.total_amount:.2f}")
        
        # Обновление списка товаров
        self.order_items_tree.delete(*self.order_items_tree.get_children())
        for item in order.items:
            self.order_items_tree.insert("", tk.END, values=(
                f"{item.product.name} (ID: {item.product.product_id})",
                f"{item.price:.2f}",
                item.quantity,
                f"{item.total_price:.2f}"
            ))
    
    def _clear_order_form(self):
        """Очистка формы заказа"""
        self.current_order = None
        self.current_customer = None
        self.order_items = []
        
        self.order_customer_label.config(text="Не выбран")
        self.order_date_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.order_total_label.config(text="0.00")
        self.order_items_tree.delete(*self.order_items_tree.get_children())
    
    def _create_new_order(self):
        """Создание нового заказа"""
        if not self.current_customer:
            messagebox.showwarning("Внимание", "Сначала выберите клиента")
            return
        
        # Генерация ID для нового заказа
        orders = self.db.get_all_orders()
        new_id = max([o.order_id for o in orders], default=0) + 1
        
        self.current_order = Order(new_id, self.current_customer)
        self.order_items = []
        
        # Обновление информации о заказе
        self.order_customer_label.config(text=f"{self.current_customer.name} (ID: {self.current_customer.customer_id})")
        self.order_date_label.config(text=self.current_order.date.strftime("%Y-%m-%d %H:%M"))
        self.order_total_label.config(text="0.00")
        self.order_items_tree.delete(*self.order_items_tree.get_children())
        
        messagebox.showinfo("Успех", f"Создан новый заказ ID: {new_id}")
    
    def _add_product_to_order(self):
        """Добавление товара в заказ"""
        if not self.current_order:
            messagebox.showwarning("Внимание", "Сначала создайте или выберите заказ")
            return
        
        selected_product = self.product_combobox.get()
        if not selected_product:
            return
        
        try:
            product_id = int(selected_product.split(':')[0])
            quantity = int(self.quantity_spinbox.get())
            
            product = self.db.get_product(product_id)
            if not product:
                raise ValueError("Товар не найден")
            
            if product.stock < quantity:
                raise ValueError(f"Недостаточно товара на складе (доступно: {product.stock})")
            
            item = OrderItem(product, quantity)
            self.current_order.add_item(item)
            self.order_items.append(item)
            
            # Обновление списка товаров
            self.order_items_tree.insert("", tk.END, values=(
                f"{product.name} (ID: {product.product_id})",
                f"{product.price:.2f}",
                quantity,
                f"{item.total_price:.2f}"
            ))
            
            # Обновление общей суммы
            self.order_total_label.config(text=f"{self.current_order.total_amount:.2f}")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверные данные: {e}")
    
    def _save_order(self):
        """Сохранение заказа"""
        if not self.current_order or not self.current_order.items:
            messagebox.showwarning("Внимание", "Нет данных для сохранения")
            return
        
        try:
            self.db.add_order(self.current_order)
            self._update_order_list()
            self._clear_order_form()
            messagebox.showinfo("Успех", "Заказ успешно сохранён")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def _cancel_order(self):
        """Отмена текущего заказа"""
        self._clear_order_form()
    
    def _import_orders(self):
        """Импорт заказов из файла"""
        file_path = filedialog.askopenfilename(
            title="Импорт заказов",
            filetypes=(("JSON files", "*.json"), ("CSV files", "*.csv")))
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for order_data in data:
                    customer = self.db.get_customer(order_data['customer_id'])
                    if not customer:
                        continue
                    
                    order = Order(
                        order_data['order_id'],
                        customer,
                        datetime.fromisoformat(order_data['date'])
                    )
                    
                    for item_data in order_data['items']:
                        product = self.db.get_product(item_data['product_id'])
                        if product:
                            order.add_item(OrderItem(product, item_data['quantity']))
                    
                    self.db.add_order(order)
            
            elif file_path.endswith('.csv'):
                # Для CSV потребуется более сложная логика из-за структуры заказов
                messagebox.showwarning("Внимание", "Импорт заказов из CSV требует специального формата")
                return
            
            self._update_order_list()
            messagebox.showinfo("Успех", "Заказы успешно импортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта: {e}")
    
    def _export_orders(self):
        """Экспорт заказов в файл"""
        file_path = filedialog.asksaveasfilename(
            title="Экспорт заказов",
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("CSV files", "*.csv")))
        
        if not file_path:
            return
        
        try:
            orders = self.db.get_all_orders()
            data = [order.to_dict() for order in orders]
            
            if file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            
            elif file_path.endswith('.csv'):
                # Для CSV потребуется более сложная логика из-за структуры заказов
                messagebox.showwarning("Внимание", "Экспорт заказов в CSV будет ограниченным")
                
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['order_id', 'customer_id', 'date', 'total_amount'])
                    for order in orders:
                        writer.writerow([
                            order.order_id,
                            order.customer.customer_id,
                            order.date.isoformat(),
                            order.total_amount
                        ])
            
            messagebox.showinfo("Успех", "Заказы успешно экспортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    # Методы для анализа данных
    def _show_top_customers(self):
        """Показать топ клиентов по количеству заказов"""
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()
        
        fig = self.analyzer.plot_top_customers()
        canvas = FigureCanvasTkAgg(fig, master=self.analysis_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _show_sales_trend(self):
        """Показать динамику продаж"""
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()
        
        fig = self.analyzer.plot_sales_trend()
        canvas = FigureCanvasTkAgg(fig, master=self.analysis_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _show_top_products(self):
        """Показать топ товаров по продажам"""
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()
        
        fig = self.analyzer.plot_top_products()
        canvas = FigureCanvasTkAgg(fig, master=self.analysis_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _show_customer_graph(self):
        """Показать граф связей клиентов"""
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()
        
        fig = self.analyzer.plot_customer_graph()
        canvas = FigureCanvasTkAgg(fig, master=self.analysis_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Методы администрирования
    def _update_stats(self):
        """Обновление статистики"""
        customers = self.db.get_all_customers()
        products = self.db.get_all_products()
        orders = self.db.get_all_orders()
        total_revenue = sum(order.total_amount for order in orders)
        
        self.customer_count_label.config(text=str(len(customers)))
        self.product_count_label.config(text=str(len(products)))
        self.order_count_label.config(text=str(len(orders)))
        self.total_revenue_label.config(text=f"{total_revenue:.2f}")
    
    def _export_full_db(self):
        """Экспорт всей базы данных в JSON"""
        file_path = filedialog.asksaveasfilename(
            title="Экспорт всей базы данных",
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"),))
        
        if not file_path:
            return
        
        try:
            self.db.export_to_json(file_path)
            messagebox.showinfo("Успех", "База данных успешно экспортирована")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    def _import_full_db(self):
        """Импорт всей базы данных из JSON"""
        file_path = filedialog.askopenfilename(
            title="Импорт всей базы данных",
            filetypes=(("JSON files", "*.json"),))
        
        if not file_path:
            return
        
        try:
            self.db.import_from_json(file_path)
            self._update_customer_list()
            self._update_product_list()
            self._update_order_list()
            self._update_product_combobox()
            self._update_stats()
            messagebox.showinfo("Успех", "База данных успешно импортирована")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта: {e}")
    
    def _export_full_db_csv(self):
        """Экспорт всей базы данных в CSV"""
        try:
            self.db.export_to_csv()
            messagebox.showinfo("Успех", "База данных успешно экспортирована в CSV")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OrderManagementApp(root)
    root.mainloop()