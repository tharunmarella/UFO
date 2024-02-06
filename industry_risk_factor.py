from datetime import datetime, timedelta

import requests
import pymongo as pym

API_KEY = 'crdM7JgRp4dTR20Cva5iNakMhXs9zQCy'
billion = 100000000


def db_init():
    global earnings_collection
    client = pym.MongoClient("mongodb://localhost:27017")
    db = client.local
    earnings_collection = db["earningsTest"]


if __name__ == "__main__":
    resultList = []

    db_init()

    industry_total_count = {}
    industry_profit_count = {}
    industry_rank = {}

    all_companies = list(earnings_collection.find({'percentage_change': {'$exists': 1}}))

    for company in all_companies:

        if company['industry'] in industry_total_count:
            industry_total_count[company['industry']] = industry_total_count[company['industry']] + 1
        else:
            industry_total_count[company['industry']] = 1
            industry_profit_count[company['industry']] = 0

        if company['percentage_change'] >= 0:
            industry_profit_count[company['industry']] = industry_profit_count[company['industry']] + 1

    for key, value in industry_total_count.items():
        industryRank = (industry_profit_count[key] / value) * 100
        industry_rank[key] = industryRank

    industry_rank = dict(sorted(industry_rank.items(), key=lambda item: item[1], reverse=True))

    print(industry_rank)
