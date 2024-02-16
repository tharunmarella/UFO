import datetime
from dateutil.parser import parse
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

allowed_source = ['Zacks Investment Research', 'Market Watch', 'Forbes', 'Investors Business Daily', 'Barrons',
                  'Bloomberg Technology', 'Bloomberg Markets and Finance', 'Yahoo Finance']
company_symbol = 'ON'
news_sentiment_url = 'https://financialmodelingprep.com/api/v3/stock_news?apikey=crdM7JgRp4dTR20Cva5iNakMhXs9zQCy&tickers=' + company_symbol + '&limit=1000'
news_sentiments = requests.get(news_sentiment_url).json()

analyzer = SentimentIntensityAnalyzer()

sentiment_sum = 0
total_sentiments = 0

if len(news_sentiments) == 0:
    print("Nope")
for news in news_sentiments:
    if news['site'] in allowed_source:
        news['publishedDate'] = parse(news['publishedDate'])
        if datetime.datetime(2024, 1, 17) >= news['publishedDate'] > datetime.datetime(2024, 1, 3):
            print(news["publishedDate"])
            news_title = news["title"]
            vs_title = analyzer.polarity_scores(news_title)
            print(news['site'])
            print(news_title)
            print(vs_title)
            sentiment_sum = sentiment_sum + vs_title['compound']
            total_sentiments = total_sentiments + 1
            print("---------------------")
if total_sentiments != 0:
    print(sentiment_sum / total_sentiments)
