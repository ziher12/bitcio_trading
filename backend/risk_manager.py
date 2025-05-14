from typing import List
import statistics
from .api import BitcioAPI

class RiskManager:
    def __init__(self, api: BitcioAPI, max_position: float = 0.1, min_spread: float = 0.001, max_loss: float = 0.05):
        self.api = api
        self.max_position = max_position  # Макс. доля баланса на сделку
        self.min_spread = min_spread      # Мин. спред
        self.max_loss = max_loss          # Макс. допустимый убыток (% от баланса)
        self.initial_balance = self.get_total_balance()

    def get_total_balance(self) -> float:
        """Получение общего баланса в USDT."""
        assets = ["BTC", "ETH", "USDT"]  # Пример активов
        total = 0.0
        for asset in assets:
            total += self.api.get_balance(asset)
        return total

    def can_trade(self, symbol: str, quantity: float, side: str) -> bool:
        """Проверка, можно ли открыть сделку."""
        # Проверка баланса
        balance = self.api.get_balance(symbol.split("USDT")[0])
        orderbook = self.api.get_orderbook(symbol)
        price = float(orderbook['asks'][0][0]) if side == "buy" else float(orderbook['bids'][0][0])
        position_value = quantity * price
        if position_value > balance * self.max_position:
            return False

        # Проверка убытков
        current_balance = self.get_total_balance()
        if (self.initial_balance - current_balance) / self.initial_balance > self.max_loss:
            return False

        # Проверка волатильности
        if self.is_high_volatility(symbol):
            return False

        return True

    def is_high_volatility(self, symbol: str, period: int = 100) -> bool:
        """Проверка высокой волатильности."""
        trades = self.api.get_historical_trades(symbol, limit=period)
        prices = [float(trade['price']) for trade in trades]
        if not prices:
            return False
        volatility = statistics.stdev(prices) / statistics.mean(prices)
        return volatility > 0.05  # Порог волатильности 5%