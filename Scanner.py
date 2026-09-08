import os
import requests

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
    )


def get_quote(symbol):
    url = "https://finnhub.io/api/v1/quote"

    params = {
        "symbol": symbol,
        "token": FINNHUB_API_KEY
    }

    response = requests.get(url, params=params)
    return response.json()


symbols = [
    "NVDA",
    "AAPL",
    "AMD",
    "TSLA",
    "AMZN",
    "META",
    "MSFT"
]


for symbol in symbols:
    try:
        data = get_quote(symbol)

        price = data.get("c", 0)
        change = data.get("dp", 0)

        if price and change:

            print(
                f"{symbol}: ${price:.2f} | "
                f"{change:.2f}%"
            )

            if abs(change) >= 1:

                direction = (
                    "🟢 BULLISH"
                    if change > 0
                    else "🔴 BEARISH"
                )

                message = (
                    f"🔥 NASDAQ BOT TEST\n\n"
                    f"{symbol}\n"
                    f"Fiyat: ${price:.2f}\n"
                    f"Değişim: {change:.2f}%\n"
                    f"{direction}"
                )

                send_telegram(message)

    except Exception as e:
        print(f"{symbol} hata: {e}")
