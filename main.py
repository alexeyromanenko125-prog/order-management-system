import tkinter as tk
from gui import OrderManagementApp

def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = OrderManagementApp(root)
    
    def on_closing():
        """Обработчик закрытия окна"""
        root.quit()     # Завершает mainloop
        root.destroy()  # Уничтожает окно
    
    # Устанавливаем обработчик закрытия окна
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except:
        on_closing()

if __name__ == "__main__":
    main()