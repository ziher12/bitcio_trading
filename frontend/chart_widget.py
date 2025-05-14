from PyQt5.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import time
from typing import Dict

class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prices = []
        self.times = []
        self.rsi = []
        self.sma = []
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(211)
        self.ax_rsi = self.figure.add_subplot(212, sharex=self.ax)
        self.init_ui()

    def init_ui(self):
        self.ax.set_title("Цена и SMA")
        self.ax.set_xlabel("Время")
        self.ax.set_ylabel("Цена")
        self.ax_rsi.set_title("RSI")
        self.ax_rsi.set_ylabel("RSI")
        self.figure.tight_layout()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_price(self, data: Dict):
        """Обновление цены."""
        price = float(data.get('price', 0))
        self.prices.append(price)
        self.times.append(time.time())
        if len(self.prices) > 100:
            self.prices.pop(0)
            self.times.pop(0)
        self.update_plot()

    def update_indicators(self, data: Dict):
        """Обновление индикаторов."""
        from backend.indicators import calculate_rsi, calculate_sma
        trades = self.prices[-100:]  # Последние 100 цен
        if len(trades) >= 14:
            self.rsi.append(calculate_rsi(trades, period=14))
            self.sma.append(calculate_sma(trades, period=20))
            if len(self.rsi) > 100:
                self.rsi.pop(0)
                self.sma.pop(0)
        self.update_plot()

    def update_plot(self):
        """Обновление графика."""
        self.ax.clear()
        self.ax_rsi.clear()
        self.ax.plot(self.times, self.prices, 'b-', label='Цена')
        if self.sma:
            self.ax.plot(self.times[-len(self.sma):], self.sma, 'r-', label='SMA')
        self.ax.legend()
        self.ax.grid(True)
        if self.rsi:
            self.ax_rsi.plot(self.times[-len(self.rsi):], self.rsi, 'g-', label='RSI')
            self.ax_rsi.axhline(70, color='red', linestyle='--')
            self.ax_rsi.axhline(30, color='green', linestyle='--')
            self.ax_rsi.legend()
        self.ax_rsi.grid(True)
        self.canvas.draw()