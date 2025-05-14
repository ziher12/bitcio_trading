from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QMessageBox, QTextEdit, QComboBox)
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import time

class ScalpingApp(QWidget):
    def __init__(self, scalper):
        super().__init__()
        self.scalper = scalper
        self.prices = []
        self.times = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Bitcio Scalping App')

        # Ввод параметров
        self.symbol_input = QLineEdit(self)
        self.symbol_input.setText("BTCUSDT")
        self.quantity_input = QLineEdit(self)
        self.quantity_input.setText("0.001")
        self.strategy_combo = QComboBox(self)
        self.strategy_combo.addItems(["Ручная торговля", "Авто-скальпинг"])

        # Кнопки
        self.buy_button = QPushButton('Купить', self)
        self.sell_button = QPushButton('Продать', self)
        self.start_auto_button = QPushButton('Запустить авто', self)
        self.cancel_all_button = QPushButton('Отменить все ордера', self)

        # Лог
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)

        # График
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Цена в реальном времени")
        self.ax.set_xlabel("Время")
        self.ax.set_ylabel("Цена")

        # Макет
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel('Тикер:'))
        input_layout.addWidget(self.symbol_input)
        input_layout.addWidget(QLabel('Количество:'))
        input_layout.addWidget(self.quantity_input)
        input_layout.addWidget(QLabel('Стратегия:'))
        input_layout.addWidget(self.strategy_combo)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.buy_button)
        button_layout.addWidget(self.sell_button)
        button_layout.addWidget(self.start_auto_button)
        button_layout.addWidget(self.cancel_all_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(QLabel('Лог транзакций:'))
        main_layout.addWidget(self.log_text)

        self.setLayout(main_layout)
        self.resize(600, 800)

        # Подключение сигналов
        self.buy_button.clicked.connect(self.buy)
        self.sell_button.clicked.connect(self.sell)
        self.start_auto_button.clicked.connect(self.start_auto)
        self.cancel_all_button.clicked.connect(self.cancel_all)

        # Таймер для обновления графика
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)  # Обновление каждую секунду

        # Запуск WebSocket
        self.scalper.api.start_websocket(self.symbol_input.text(), self.update_price)
        self.show()

    def update_price(self, data):
        """Обновление цены с WebSocket."""
        price = float(data.get('price', 0))
        self.prices.append(price)
        self.times.append(time.time())
        if len(self.prices) > 100:  # Ограничение длины графика
            self.prices.pop(0)
            self.times.pop(0)

    def update_plot(self):
        """Обновление графика цен."""
        self.ax.clear()
        self.ax.plot(self.times, self.prices, 'b-')
        self.ax.set_title(f"Цена {self.symbol_input.text()}")
        self.ax.grid(True)
        self.canvas.draw()

    def buy(self):
        """Обработка покупки."""
        try:
            symbol = self.symbol_input.text()
            quantity = float(self.quantity_input.text())
            res = self.scalper.buy(symbol, quantity)
            self.log_text.append(f"Покупка: {res}")
            QMessageBox.information(self, 'Купить', str(res))
        except Exception as e:
            self.log_text.append(f"Ошибка покупки: {e}")
            QMessageBox.critical(self, 'Ошибка', str(e))

    def sell(self):
        """Обработка продажи."""
        try:
            symbol = self.symbol_input.text()
            quantity = float(self.quantity_input.text())
            res = self.scalper.sell(symbol, quantity)
            self.log_text.append(f"Продажа: {res}")
            QMessageBox.information(self, 'Продать', str(res))
        except Exception as e:
            self.log_text.append(f"Ошибка продажи: {e}")
            QMessageBox.critical(self, 'Ошибка', str(e))

    def start_auto(self):
        """Запуск автоматического скальпинга."""
        try:
            symbol = self.symbol_input.text()
            quantity = float(self.quantity_input.text())
            if self.strategy_combo.currentText() == "Авто-скальпинг":
                self.log_text.append(f"Запуск авто-скальпинга для {symbol}...")
                self.scalper.auto_scalp(symbol, quantity)
                self.log_text.append("Авто-скальпинг завершён")
        except Exception as e:
            self.log_text.append(f"Ошибка авто-скальпинга: {e}")
            QMessageBox.critical(self, 'Ошибка', str(e))

    def cancel_all(self):
        """Отмена всех ордеров."""
        try:
            symbol = self.symbol_input.text()
            self.scalper.cancel_all_orders(symbol)
            self.log_text.append(f"Все ордера для {symbol} отменены")
            QMessageBox.information(self, 'Отмена', "Все ордера отменены")
        except Exception as e:
            self.log_text.append(f"Ошибка отмены: {e}")
            QMessageBox.critical(self, 'Ошибка', str(e))

    def closeEvent(self, event):
        """Остановка WebSocket при закрытии."""
        self.scalper.api.stop_websocket()
        event.accept()