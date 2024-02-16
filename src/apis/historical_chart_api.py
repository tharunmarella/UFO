import requests


def get_historical_chart(start, end, company_symbol, apikey):
    marketCap_url = 'https://financialmodelingprep.com/api/v3/historical-chart/1hour/' + company_symbol + '?from=' + start + '&to=' + end + '&apikey=' + apikey
    result = requests.get(marketCap_url).json()
    return result
