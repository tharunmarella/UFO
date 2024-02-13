from datetime import datetime, timedelta
from dateutil.parser import parse
import requests
import pymongo as pym
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

API_KEY = 'crdM7JgRp4dTR20Cva5iNakMhXs9zQCy'
billion = 100000000


def db_init():
    global earnings_collection
    client = pym.MongoClient("mongodb://localhost:27017")
    db = client.local
    earnings_collection = db["earningsTest"]


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
    if len(company_profile) != 0:
        company_profile = company_profile[0]
        filtered_doc = {'cik': company_profile['cik'], 'country': company_profile['country'],
                        'sector': company_profile['sector'], 'industry': company_profile['industry']}
        return filtered_doc
    return {}


def get_avg_price_target(company_symbol, apikey):
    price_list = {}
    date_list = {}
    allowed_firms = ['Goldman Sachs', 'UBS', 'J.P. Morgan', 'Morgan Stanley', 'Bank of America Securities']
    price_target_url = 'https://financialmodelingprep.com/api/v4/price-target?symbol=' + company_symbol + '&apikey=' + apikey
    ratings = requests.get(price_target_url).json()
    if len(ratings) != 0:
        for rating in ratings:
            if not rating['analystCompany'] in allowed_firms:
                continue
            rating['publishedDate'] = parse(rating['publishedDate'])
            if not rating['analystCompany'] in date_list:
                date_list[rating['analystCompany']] = rating['publishedDate']
                price_list[rating['analystCompany']] = rating['priceTarget']

            if date_list[rating['analystCompany']] < rating['publishedDate']:
                date_list[rating['analystCompany']] = rating['publishedDate']
                price_list[rating['analystCompany']] = rating['priceTarget']

        if len(price_list) == 0:
            return {'price_target': 0}

        return {'price_target': sum(price_list.values()) / len(price_list)}
    else:
        return {'price_target': 0}


def get_news_sentiment(company_symbol, apikey, trigger_date):
    allowed_source = ['Zacks Investment Research', 'Market Watch', 'Forbes', 'Investors Business Daily', 'Barrons',
                      'Bloomberg Technology', 'Bloomberg Markets and Finance', 'Yahoo Finance']
    news_sentiment_url = 'https://financialmodelingprep.com/api/v3/stock_news?apikey=' + apikey + '&tickers=' + company_symbol + '&limit=2000'
    news_sentiments = requests.get(news_sentiment_url).json()
    analyzer = SentimentIntensityAnalyzer()

    sentiment_sum = 0
    total_sentiments = 0
    if len(news_sentiments) == 0:
        return {"news_sentiment": -99}
    for news in news_sentiments:
        if news['site'] in allowed_source:
            news['publishedDate'] = parse(news['publishedDate'])
            if trigger_date >= news['publishedDate'] > trigger_date + timedelta(days=-15):
                news_title = news["title"]
                vs_title = analyzer.polarity_scores(news_title)
                total_sentiments = total_sentiments + 1
                sentiment_sum = sentiment_sum + vs_title['compound']
    if total_sentiments == 0:
        return {"news_sentiment": -99}
    return {"news_sentiment": sentiment_sum / total_sentiments}


if __name__ == "__main__":

    resultList = []

    db_init()

    earnings_list = get_earning_calender('2023-01-01', '2023-12-30', API_KEY)

    for company in earnings_list:
        if ('.' not in company['symbol']) and company['date']:
            marketcap_data = get_market_cap(API_KEY, company['symbol'])
            if len(marketcap_data) != 0 and marketcap_data[0]['marketCap'] > billion:
                company['date'] = datetime.strptime(company['date'], "%Y-%m-%d")
                company_chart_list = get_historical_chart((company['date'] + timedelta(days=-7)).strftime("%Y-%m-%d"),
                                                          (company['date'] + timedelta(days=-1)).strftime("%Y-%m-%d"),
                                                          company['symbol'], API_KEY)

                company_profile_doc = get_filtered_company_profile_doc(
                    get_company_profile(company['symbol'], API_KEY))
                price_gain_doc = get_prepared_price_data(company_chart_list)
                price_target_doc = get_avg_price_target(company['symbol'], API_KEY)
                news_sentiment_doc = get_news_sentiment(company['symbol'], API_KEY, company['date'])
                resultList.append(
                    company | company_profile_doc | {
                        'marketCap': marketcap_data[0][
                            'marketCap']} | price_gain_doc | price_target_doc | news_sentiment_doc)
                print(resultList)

    earnings_collection.insert_many(resultList)
