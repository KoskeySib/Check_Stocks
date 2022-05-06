# Check Stocks

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tinkoff-investments)](https://www.python.org/downloads/)

Данный репозиторий предоставляет возможность клиентам [Тинькофф Инвестиции](https://www.tinkoff.ru/invest/) на языке Python проверить акции при помощи индикаторов.


## Начало работы

<!-- termynal -->

```
$ pip install tinkoff-investments
```

Для запуска проверки, нужно добавить токен в соответствующую строку

<!-- termynal -->

```
TOKEN=" "
```

## Возможности

<!-- termynal -->

```
Проверяет акцию индикаторами EMA, MACD, RSI, STOCH, STOCHRSI, BBANDS, за каждый индикатор присваивается балл, после всех 
вычислений программа выдает общий балл по проверке и рекомендует к покупке или нет.
```
