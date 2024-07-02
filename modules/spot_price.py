import okx.MarketData as MarketData
from threading import Thread
from functools import partial

def loop1(market, token_base, local_tokens):
    tokens = token_base["tokens"]
    try:
        for i in range(0, len(tokens), 3):
            local_tokens[tokens[i]] = format(float(market.get_orderbook(
                instId=f"{tokens[i]}-{token_base['fiat_token']}"
            )["data"][0]["asks"][0][0]), '.10f').rstrip('0').rstrip('.')
    except:
        print("Error loop1")
        local_tokens.clear()
        loop1(market, token_base, local_tokens)

def loop2(market, token_base,local_tokens):
    tokens = token_base["tokens"]
    try:
        for i in range(1, len(tokens), 3):
            local_tokens[tokens[i]] = format(float(market.get_orderbook(
                instId=f"{tokens[i]}-{token_base['fiat_token']}"
            )["data"][0]["asks"][0][0]), '.10f').rstrip('0').rstrip('.')
    except:
        print("Error loop2")
        local_tokens.clear()
        loop2(market, token_base, local_tokens)


def loop3(market, token_base, local_tokens):
    tokens = token_base["tokens"]
    try:
        for i in range(2, len(tokens), 3):
            local_tokens[tokens[i]] = format(float(market.get_orderbook(
                instId=f"{tokens[i]}-{token_base['fiat_token']}"
            )["data"][0]["asks"][0][0]), '.10f').rstrip('0').rstrip('.')
    except:
        print("Error loop3")
        local_tokens.clear()
        loop3(market, token_base, local_tokens)

def get_price(token_base):
    tokens = {}

    local_tokens1 = {}
    local_tokens2 = {}
    local_tokens3 = {}

    marketDataAPI = MarketData.MarketAPI(flag="0")

    partial_func1 = partial(loop1, marketDataAPI, token_base, local_tokens1)
    partial_func2 = partial(loop2, marketDataAPI, token_base, local_tokens2)
    partial_func3 = partial(loop3, marketDataAPI, token_base, local_tokens3)

    tokens1 = Thread(target=partial_func1)
    tokens2 = Thread(target=partial_func2)
    tokens3 = Thread(target=partial_func3)

    tokens1.start()
    tokens2.start()
    tokens3.start()

    tokens1.join()
    tokens2.join()
    tokens3.join()

    tokens = local_tokens1 | local_tokens2 | local_tokens3

    return tokens


