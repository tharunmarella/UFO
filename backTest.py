from datetime import datetime, timedelta

import requests
import pymongo as pym

import Russells_1000

API_KEY = 'crdM7JgRp4dTR20Cva5iNakMhXs9zQCy'
billion = 100000000


def db_init():
    global earnings_collection
    client = pym.MongoClient("mongodb://localhost:27017")
    db = client.local
    earnings_collection = db["earningsTest15"]


def get_earning_calender(start, end, apikey):
    earnings_url = 'https://financialmodelingprep.com/api/v3/earning_calendar?from=' + start + '&to=' + end + '&apikey=' + apikey
    result = requests.get(earnings_url).json()
    return result


def get_market_cap(apikey, symbol):
    marketCap_url = 'https://financialmodelingprep.com/api/v3/market-capitalization/' + symbol + '?apikey=' + apikey
    result = requests.get(marketCap_url).json()
    return result


def get_historical_chart(start, end, company_symbol, apikey):
    marketCap_url = 'https://financialmodelingprep.com/api/v3/historical-chart/1hour/' + company_symbol + '?from=' + start + '&to=' + end + '&apikey=' + apikey
    result = requests.get(marketCap_url).json()
    return result


def get_prepared_price_data(chart_list):
    company_chart_list_converted = []
    price_doc = {}
    for time in chart_list:
        time['date'] = datetime.strptime(time['date'], "%Y-%m-%d %H:%M:%S")
        company_chart_list_converted.append(time)
    company_chart_list_converted.sort(key=lambda r: r['date'])
    if len(company_chart_list_converted) > 1:
        price_difference = company_chart_list_converted[-1]['close'] - company_chart_list_converted[0]['open']
        percentage_change = (price_difference / company_chart_list_converted[0]['open']) * 100
        price_doc['price_difference'] = price_difference
        price_doc['percentage_change'] = percentage_change
    return price_doc


def get_company_profile(company_symbol, apikey):
    company_profile_url = 'https://financialmodelingprep.com/api/v3/profile/' + company_symbol + '?apikey=' + apikey
    result = requests.get(company_profile_url).json()
    return result


def get_filtered_company_profile_doc(company_profile):
    if company_profile:
        company_profile = company_profile[0]
        filtered_doc = {'cik': company_profile['cik'], 'country': company_profile['country'],
                        'sector': company_profile['sector'], 'industry': company_profile['industry']}
        return filtered_doc
    return {}


if __name__ == "__main__":

    resultList = []

    db_init()

    earnings_list = get_earning_calender('2023-11-10', '2024-02-10', API_KEY)
    russell_tickers = Russells_1000.top_1000_from_csv()

    filtered_earnings_list = []

    for obj in earnings_list:
        if russell_tickers.__contains__(obj["symbol"]):
            filtered_earnings_list.append(obj)

    for company in filtered_earnings_list:
        if (not '.' in company['symbol']) and company['date']:
            marketcap_data = get_market_cap(API_KEY, company['symbol'])
            if marketcap_data and marketcap_data[0]['marketCap'] > billion:
                company['date'] = datetime.strptime(company['date'], "%Y-%m-%d")
                company_chart_list = get_historical_chart((company['date'] + timedelta(days=-7)).strftime("%Y-%m-%d"),
                                                          (company['date'] + timedelta(days=-1)).strftime("%Y-%m-%d"),
                                                          company['symbol'], API_KEY)

                company_profile_doc = get_filtered_company_profile_doc(
                    get_company_profile(company['symbol'], API_KEY))
                price_gain_doc = get_prepared_price_data(company_chart_list)
                resultList.append(
                    company | company_profile_doc | {'marketCap': marketcap_data[0]['marketCap']} | price_gain_doc)
                print(resultList)

    earnings_collection.insert_many(resultList)
