from datetime import datetime, timedelta

from src.apis.avg_price_target_api import get_avg_price_target
from src.apis.company_profile_api import get_company_profile
from src.apis.earning_calender_api import get_earning_calender
from src.apis.filtered_company_profile_api import get_filtered_company_profile_doc
from src.apis.historical_chart_api import get_historical_chart
from src.apis.market_cap_api import get_market_cap
from src.apis.news_sentiment_api import get_news_sentiment
from src.utils.prepared_price_data_util import get_prepared_price_data
from src.utils.db_util import db_init
from src.utils.db_util import insert_many

API_KEY = 'crdM7JgRp4dTR20Cva5iNakMhXs9zQCy'
billion = 100000000

if __name__ == "__main__":

    resultList = []

    db_init()

    earnings_list = get_earning_calender('2023-01-01', '2023-12-30', API_KEY)

    for company in earnings_list:
        if ('.' not in company['symbol']) and company['date']:
            marketcap_doc = get_market_cap(API_KEY, company['symbol'])
            if marketcap_doc['marketCap'] > billion:
                company['date'] = datetime.strptime(company['date'], "%Y-%m-%d")

                news_sentiment_doc = get_news_sentiment(company['symbol'], API_KEY, company['date'])
                if news_sentiment_doc['news_sentiment'] == -99:
                    continue

                price_target_doc = get_avg_price_target(company['symbol'], API_KEY)
                if price_target_doc['price_target'] == -1:
                    continue

                company_chart_list = get_historical_chart((company['date'] + timedelta(days=-7)).strftime("%Y-%m-%d"),
                                                          (company['date'] + timedelta(days=-1)).strftime("%Y-%m-%d"),
                                                          company['symbol'], API_KEY)

                company_profile_doc = get_filtered_company_profile_doc(
                    get_company_profile(company['symbol'], API_KEY))

                price_gain_doc = get_prepared_price_data(company_chart_list, price_target_doc['price_target'])

                resultList.append(
                    company | company_profile_doc | marketcap_doc | price_gain_doc | price_target_doc | news_sentiment_doc)

                print(resultList)
    insert_many(resultList)
