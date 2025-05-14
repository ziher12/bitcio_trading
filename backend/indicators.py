from typing import List
import statistics

def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Расчёт индекса относительной силы (RSI)."""
    if len(prices) < period + 1:
        return 50.0  # Нейтральное значение, если данных мало

    gains = []
    losses = []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            losses.append(-diff)
            gains.append(0)

    avg_gain = statistics.mean(gains[-period:]) if gains else 0
    avg_loss = statistics.mean(losses[-period:]) if losses else 0

    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_sma(prices: List[float], period: int = 20) -> float:
    """Расчёт простой скользящей средней (SMA)."""
    if len(prices) < period:
        return statistics.mean(prices) if prices else 0.0
    return statistics.mean(prices[-period:])

def calculate_ema(prices: List[float], period: int = 20) -> float:
    """Расчёт экспоненциальной скользящей средней (EMA)."""
    if len(prices) < period:
        return statistics.mean(prices) if prices else 0.0

    k = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema