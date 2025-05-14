from .api import BitcioAPI
from .indicators import calculate_rsi, calculate_sma
from .risk_manager import RiskManager
from typing import Dict, Optional
import time

class Scalper:
    def __init__(self, api: BitcioAPI, risk_manager: RiskManager):
        self.api = api
        self.risk_manager = risk_manager
        self.profit = 0.0
        self.trades = []

    def buy(self, symbol: str, quantity: float) -> Dict:
        """Ручная покупка по лучшей цене."""
        if not self.risk_manager.can_trade(symbol, quantity, "buy"):
            return {"status": "rejected", "reason": "Risk limits exceeded"}
        orderbook = self.api.get_orderbook(symbol)
        best_ask = float(orderbook['asks'][0][0])
        order = self.api.place_order(symbol, "buy", quantity, price=best_ask)
        if order.get("status") == "filled":
            self.profit -= best_ask * quantity
            self.trades.append({"side": "buy", "price": best_ask, "quantity": quantity})
        return order

    def sell(self, symbol: str, quantity: float) -> Dict:
        """Ручная продажа по лучшей цене."""
        if not self.risk_manager.can_trade(symbol, quantity, "sell"):
            return {"status": "rejected", "reason": "Risk limits exceeded"}
        orderbook = self.api.get_orderbook(symbol)
        best_bid = float(orderbook['bids'][0][0])
        order = self.api.place_order(symbol, "sell", quantity, price=best_bid)
        if order.get("status") == "filled":
            self.profit += best_bid * quantity
            self.trades.append({"side": "sell", "price": best_bid, "quantity": quantity})
        return order

    def auto_scalp(self, symbol: str, base_quantity: float, duration: int = 3600) -> None:
        """Автоматический скальпинг с использованием индикаторов."""
        start_time = time.time()
        while time.time() - start_time < duration:
            if not self.risk_manager.can_trade(symbol, base_quantity, "buy"):
                time.sleep(5)
                continue

            orderbook = self.api.get_orderbook(symbol)
            best_bid = float(orderbook['bids'][0][0])
            best_ask = float(orderbook['asks'][0][0])
            spread = (best_bid - best_ask) / best_ask

            # Получение индикаторов
            trades = self.api.get_historical_trades(symbol)
            prices = [float(trade['price']) for trade in trades]
            rsi = calculate_rsi(prices, period=14)
            sma = calculate_sma(prices, period=20)

            if spread >= self.risk_manager.min_spread and rsi < 30:  # Покупка при перепроданности
                balance = self.api.get_balance(symbol.split("USDT")[0])
                quantity = min(base_quantity, balance * self.risk_manager.max_position / best_ask)
                if quantity > 0:
                    self.buy(symbol, quantity)
                    time.sleep(1)
                    if rsi > 70:  # Продажа при перекупленности
                        self.sell(symbol, quantity)
            time.sleep(5)

    def calculate_profit(self) -> float:
        """Расчёт текущей прибыли."""
        return self.profit

    def get_open_positions(self, symbol: str) -> List[Dict]:
        """Получение открытых позиций."""
        orders = self.api.get_order_history(symbol)
        return [order for order in orders if order.get("status") == "open"]

    def cancel_all_orders(self, symbol: str) -> None:
        """Отмена всех открытых ордеров."""
        open_orders = self.get_open_positions(symbol)
        for order in open_orders:
            self.api.cancel_order(order["order_id"], symbol)