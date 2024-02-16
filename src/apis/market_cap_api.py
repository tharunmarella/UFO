import requests


def get_market_cap(apikey, symbol):
    marketCap_url = 'https://financialmodelingprep.com/api/v3/market-capitalization/' + symbol + '?apikey=' + apikey
    result = requests.get(marketCap_url).json()
    if len(result) == 0:
        return {'marketCap': -1}
    return {'marketCap': result[0]['marketCap']}
