import requests
import json
import websocket
import threading
import time
from typing import Dict, List, Optional

class BitcioAPI:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.bitcio.com"
        self.ws_url = "wss://ws.bitcio.com"
        self.ws = None
        self.price_callback = None
        self.orderbook_cache: Dict[str, Dict] = {}
        self.trade_history_callback = None

    def get_orderbook(self, symbol: str) -> Dict:
        """Получение стакана ордеров."""
        r = requests.get(f"{self.base_url}/orderbook?symbol={symbol}")
        return r.json()

    def get_balance(self, asset: str) -> float:
        """Получение баланса по активу."""
        headers = {"X-API-KEY": self.api_key}
        r = requests.get(f"{self.base_url}/balance?asset={asset}", headers=headers)
        return float(r.json().get("balance", 0))

    def place_order(self, symbol: str, side: str, quantity: float, price: Optional[float] = None) -> Dict:
        """Размещение ордера."""
        payload = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "type": "limit" if price else "market"
        }
        headers = {"X-API-KEY": self.api_key}
        r = requests.post(f"{self.base_url}/order", json=payload, headers=headers)
        return r.json()

    def cancel_order(self, order_id: str, symbol: str) -> Dict:
        """Отмена ордера."""
        headers = {"X-API-KEY": self.api_key}
        payload = {"order_id": order_id, "symbol": symbol}
        r = requests.delete(f"{self.base_url}/order", json=payload, headers=headers)
        return r.json()

    def get_order_history(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Получение истории ордеров."""
        headers = {"X-API-KEY": self.api_key}
        r = requests.get(f"{self.base_url}/orders?symbol={symbol}&limit={limit}", headers=headers)
        return r.json()

    def get_historical_trades(self, symbol: str, limit: int = 1000) -> List[Dict]:
        """Получение исторических сделок для индикаторов."""
        headers = {"X-API-KEY": self.api_key}
        r = requests.get(f"{self.base_url}/trades?symbol={symbol}&limit={limit}", headers=headers)
        return r.json()

    def start_websocket(self, symbol: str, price_callback=None, trade_history_callback=None):
        """Запуск WebSocket для цен и сделок."""
        self.price_callback = price_callback
        self.trade_history_callback = trade_history_callback
        self.ws = websocket.WebSocketApp(
            f"{self.ws_url}/ticker/{symbol}",
            on_message=self.on_ws_message,
            on_error=self.on_ws_error,
            on_close=self.on_ws_close
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def on_ws_message(self, ws, message):
        """Обработка сообщений WebSocket."""
        data = json.loads(message)
        if data.get('type') == 'ticker':
            self.orderbook_cache[data['symbol']] = data
            if self.price_callback:
                self.price_callback(data)
        elif data.get('type') == 'trade':
            if self.trade_history_callback:
                self.trade_history_callback(data)

    def on_ws_error(self, ws, error):
        """Обработка ошибок WebSocket."""
        print(f"WebSocket error: {error}")

    def on_ws_close(self, ws, close_status_code, close_msg):
        """Обработка закрытия WebSocket."""
        print("WebSocket closed. Reconnecting...")
        time.sleep(5)
        self.start_websocket()

    def stop_websocket(self):
        """Остановка WebSocket."""
        if self.ws:
            self.ws.close()