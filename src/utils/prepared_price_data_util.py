from datetime import datetime, timedelta


def get_prepared_price_data(chart_list, price_target):
    company_chart_list_converted = []
    price_doc = {}
    for time in chart_list:
        time['date'] = datetime.strptime(time['date'], "%Y-%m-%d %H:%M:%S")
        company_chart_list_converted.append(time)
    company_chart_list_converted.sort(key=lambda r: r['date'])
    if len(company_chart_list_converted) > 1:
        price_difference = company_chart_list_converted[-1]['close'] - company_chart_list_converted[0]['open']
        percentage_change = (price_difference / company_chart_list_converted[0]['open']) * 100
        price_doc['price_buy'] = company_chart_list_converted[0]['open']
        price_doc['price_target_price_difference_percentage'] = ((price_target - company_chart_list_converted[0][
            'open']) /
                                                                 company_chart_list_converted[0]['open']) * 100
        price_doc['price_difference'] = price_difference
        price_doc['percentage_change'] = percentage_change
    return price_doc
