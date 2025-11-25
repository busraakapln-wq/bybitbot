import json
import time
import requests
import websocket
from threading import Thread

# ================= TELEGRAM AYARLARI =================
TELEGRAM_BOT_TOKEN = "8302795386:AAGF2FujJfS58EIvC4ONsI5SsrOACgT5Uo4"
TELEGRAM_CHAT_ID = "5949944956"  # senin chat id'in

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        r = requests.post(url, data=data, timeout=10)
        if r.status_code != 200:
            print("Telegram hata:", r.status_code, r.text)
    except Exception as e:
        print("Telegram exception:", e)


# ================= BYBIT AYARLARI =================
WS_URL = "wss://stream.bybit.com/v5/public/spot"

SYMBOLS = [
    "AVNTUSDT",
    "PIEVERSEUSDT",
    "ZIGUSDT",
    "GAIBUSDT",
]

MIN_USD = 10000  # 10.000 USDT ve üzeri ALIM işlemleri


def on_message(ws, message):
    try:
        msg = json.loads(message)

        topic = msg.get("topic", "")
        if not topic.startswith("publicTrade."):
            return

        symbol = topic.replace("publicTrade.", "")

        trades = msg.get("data", [])
        for t in trades:
            side = t.get("S")
            price = float(t.get("p", "0"))
            qty = float(t.get("v", "0"))
            notional = price * qty

            if side == "Buy" and notional >= MIN_USD:
                text = (
                    "🔥 BYBIT – BÜYÜK MARKET ALIŞ!\n"
                    f"Parite : {symbol}\n"
                    f"Yön    : {side}\n"
                    f"Fiyat  : {price}\n"
                    f"Miktar : {qty}\n"
                    f"Hacim  : {notional:.2f} USDT\n"
                )
                print(text)
                send_telegram_message(text)

    except Exception as e:
        print("on_message hata:", e)


def on_open(ws):
    print("Bybit WS bağlandı!")
    for s in SYMBOLS:
        sub_msg = {"op": "subscribe", "args": [f"publicTrade.{s}"]}
        ws.send(json.dumps(sub_msg))
        print(f"Abone olundu → {s}")


def start_ws():
    while True:
        try:
            ws = websocket.WebSocketApp(
                WS_URL,
                on_open=on_open,
                on_message=on_message,
            )
            ws.run_forever()
        except Exception as e:
            print("Bağlantı koptu, tekrar deneniyor...", e)
            time.sleep(5)


if __name__ == "__main__":
    t = Thread(target=start_ws, daemon=True)
    t.start()

    print("Bot başlatıldı! 🚀")

    while True:
        time.sleep(60)
