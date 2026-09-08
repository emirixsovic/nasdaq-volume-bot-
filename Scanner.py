import os
import requests
from datetime import datetime, timezone

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

SYMBOLS = [
    "NVDA", "AMD", "TSLA", "AAPL", "AMZN",
    "META", "MSFT", "GOOGL", "AVGO", "NFLX",
    "PLTR", "MU", "INTC", "MSTR", "QCOM",
    "AMAT", "LRCX", "SMCI", "ARM", "MRVL",
    "CRWD", "PANW", "APP", "COIN", "HOOD",
    "MARA", "RIOT", "SOFI", "RIVN", "NIO"
]

RVOL_MIN = 5.0
VOLUME_ACCEL_MIN = 1.5
PRICE_5M_MIN = 0.5
PRICE_15M_MIN = 1.0


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        },
        timeout=15
    )

    print("Telegram:", response.status_code, response.text)


def get_candles(symbol):
    url = "https://finnhub.io/api/v1/stock/candle"

    now = int(datetime.now(timezone.utc).timestamp())
    start = now - (60 * 60 * 8)

    params = {
        "symbol": symbol,
        "resolution": "5",
        "from": start,
        "to": now,
        "token": FINNHUB_API_KEY
    }

    response = requests.get(url, params=params, timeout=15)
    return response.json()


def analyze(symbol):

    data = get_candles(symbol)

    if data.get("s") != "ok":
        print(f"{symbol}: veri alınamadı")
        return None

    closes = data["c"]
    opens = data["o"]
    highs = data["h"]
    lows = data["l"]
    volumes = data["v"]

    if len(closes) < 30:
        return None

    i = len(closes) - 2

    current_open = opens[i]
    current_high = highs[i]
    current_low = lows[i]
    current_close = closes[i]
    current_volume = volumes[i]

    previous_volumes = volumes[i - 20:i]

    avg_volume = sum(previous_volumes) / len(previous_volumes)

    if avg_volume <= 0:
        return None

    rvol = current_volume / avg_volume

    previous_volume = volumes[i - 1]

    if previous_volume > 0:
        volume_acceleration = current_volume / previous_volume
    else:
        volume_acceleration = 0

    price_5m = (
        (current_close - current_open)
        / current_open
    ) * 100

    close_15m_ago = closes[i - 3]

    price_15m = (
        (current_close - close_15m_ago)
        / close_15m_ago
    ) * 100

    candle_range = current_high - current_low

    if candle_range > 0:
        body_strength = (
            abs(current_close - current_open)
            / candle_range
        )
    else:
        body_strength = 0

    volume_explosion = (
        rvol >= RVOL_MIN
        and volume_acceleration >= VOLUME_ACCEL_MIN
    )

    bullish = (
        volume_explosion
        and price_5m >= PRICE_5M_MIN
        and price_15m >= PRICE_15M_MIN
        and current_close > current_open
        and body_strength >= 0.50
    )

    bearish = (
        volume_explosion
        and price_5m <= -PRICE_5M_MIN
        and price_15m <= -PRICE_15M_MIN
        and current_close < current_open
        and body_strength >= 0.50
    )

    if not bullish and not bearish:
        return None

    direction = "🟢 BULLISH" if bullish else "🔴 BEARISH"

    return (
        f"🔥 NASDAQ VOLUME EXPLOSION\n\n"
        f"{direction}\n"
        f"📊 {symbol}\n\n"
        f"💵 Fiyat: ${current_close:.2f}\n"
        f"📈 RVOL: {rvol:.1f}x\n"
        f"⚡ Hacim ivmesi: {volume_acceleration:.1f}x\n"
        f"⏱ 5M: {price_5m:+.2f}%\n"
        f"⏱ 15M: {price_15m:+.2f}%\n"
        f"💪 Mum gücü: {body_strength:.0%}\n\n"
        f"⚠️ İlk aşama sinyali"
    )


def main():

    print("NASDAQ Volume Scanner başladı.")

    # TELEGRAM TEST
    send_telegram(
        "🟢 NASDAQ BOT TEST\n\n"
        "Telegram bağlantısı başarılı.\n"
        "Volume Scanner çalışıyor."
    )

    signals = 0

    for symbol in SYMBOLS:

        try:
            signal = analyze(symbol)

            if signal:
                print(signal)
                send_telegram(signal)
                signals += 1

        except Exception as e:
            print(f"{symbol} hata: {e}")

    print(f"Tarama tamamlandı. Sinyal: {signals}")


if __name__ == "__main__":
    main()
