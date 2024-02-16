from dateutil.parser import parse
import requests


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
            return {'price_target': -1}

        return {'price_target': sum(price_list.values()) / len(price_list)}
    else:
        return {'price_target': -1}
