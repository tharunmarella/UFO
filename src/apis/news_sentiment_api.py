from datetime import timedelta
import requests
from dateutil.parser import parse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


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