import requests


def get_earning_calender(start, end, apikey):
    earnings_url = 'https://financialmodelingprep.com/api/v3/earning_calendar?from=' + start + '&to=' + end + '&apikey=' + apikey
    result = requests.get(earnings_url).json()
    return result
