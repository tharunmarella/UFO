import requests


def get_filtered_company_profile_doc(company_profile):
    if len(company_profile) != 0:
        company_profile = company_profile[0]
        filtered_doc = {'cik': company_profile['cik'], 'country': company_profile['country'],
                        'sector': company_profile['sector'], 'industry': company_profile['industry']}
        return filtered_doc
    return {}
