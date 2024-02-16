import requests


def get_company_profile(company_symbol, apikey):
    company_profile_url = 'https://financialmodelingprep.com/api/v3/profile/' + company_symbol + '?apikey=' + apikey
    result = requests.get(company_profile_url).json()
    return result
