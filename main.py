import indicators as ind
import logging
import time
import os

from tinkoff.invest import Client
from datetime import datetime, timedelta
from pytz import timezone

TOKEN = " "

# -----------------------------------------------------------------------------------------------------
# OPTIONS

CANDLE_INTERVAL = 5  # Интервалы свечей (0=UNSPECIFIED, 1=1_MIN, 2=5_MIN, 3=15_MIN, 4=HOUR, 5=DAY)
DAYS = 100  # Глубина архива свечей в днях
POINTS_TO_ENTER = 7  # Сколько баллов должна набрать свеча для покупки

# -----------------------------------------------------------------------------------------------------

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)-5.5s] %(message)s",
    handlers=[
        logging.FileHandler(
            "{path}/logs/{fname}.log".format(
                path=os.path.dirname(os.path.abspath(__file__)),
                fname="tinkoff_ST")),
        logging.StreamHandler()
    ])

logger = logging.getLogger('')

all_stocks = []


def candles_info(figi):
    now = datetime.now(tz=timezone('Europe/Moscow'))
    yesterday = now - timedelta(days=DAYS)
    klines = client.market_data.get_candles(
        figi=figi,
        from_=yesterday,
        to=now,
        interval=CANDLE_INTERVAL
    )
    return klines.candles


while True:
    with Client(TOKEN) as client:
        time.sleep(0.1)
        TICKER = str(input("Введите тикер акции: "))
        stocks_list = client.instruments.shares().instruments  # Делим все акции на три списка, по валютно
        time.sleep(0.1)
        for x in stocks_list:
            if x.ticker == TICKER:
                figi_stock = x.figi
                name_stock = x.name

                closes = []
                high = []
                low = []

                klines2 = candles_info(figi=figi_stock)
                for i in klines2:
                    closes.append(i.close.units)
                    high.append(i.high.units)
                    low.append(i.low.units)

                # Скользящая средняя
                sma_5 = ind.SMA(closes, 5)
                sma_100 = ind.SMA(closes, 100)

                ema_5 = ind.EMA(closes, 5)
                ema_100 = ind.EMA(closes, 100)

                enter_points = 0

                if ema_5[-1] > ema_100[-1] and sma_5[-1] > sma_100[-1]:
                    # Быстрая EMA выше медленной и быстрая SMA выше медленной, считаем, что можно входить
                    enter_points += 1

                macd, macdsignal, macdhist = ind.MACD(closes, 12, 26, 9)
                if macd[-1] > macdsignal[-1] and macdhist[-1] > 0:
                    # Линия макд выше сигнальной и на гистограмме они выше нуля
                    enter_points += 1.3

                rsi_9 = ind.RSI(closes, 9)
                rsi_14 = ind.RSI(closes, 14)
                rsi_21 = ind.RSI(closes, 21)

                if rsi_9[-1] < 70 and rsi_14[-1] < 70 and rsi_21[-1] < 70:
                    # RSI не показывает перекупленности
                    enter_points += 2

                fast, slow = ind.STOCH(high, low, closes, 5, 3, 3)
                if fast[-1] > slow[-1]:
                    # Быстрая линия стохастика выше медленной, вход
                    enter_points += 1.5

                fast, slow = ind.STOCHRSI(closes, 14, 3, 3)
                if fast[-1] > slow[-1]:
                    # Быстрая линия STOCHRSI выше медленной, вход
                    enter_points += 1.8

                upper, middle, lower = ind.BBANDS(closes, ma_period=21)
                if high[-1] > upper[-1]:
                    # Свеча пробила верхнюю полосу Боллинджера
                    enter_points += 3

                if enter_points >= POINTS_TO_ENTER:
                    logger.warning("Акция {c} ({a}) - набрала {b} балла(ов), стоит к ней присмотреться".format(
                        a=TICKER, b=enter_points, c=name_stock))
                else:
                    logger.warning("Акция {c} ({a}) - набрала {b} балла(ов), не лучшее время её покупать".format(
                        a=TICKER, b=enter_points, c=name_stock))
    time.sleep(0.1)
