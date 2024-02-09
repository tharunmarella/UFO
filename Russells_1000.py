import csv
from datetime import datetime, timedelta
from itertools import chain
import backTest




def top_1000_from_csv():
    with open('resources/top_1000.csv', 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        list_of_rows = list(csv_reader)

    flattened_list = list(chain.from_iterable(list_of_rows))
    earnings_list = flattened_list
    return flattened_list;


if __name__ == "__main__":
    print(top_1000_from_csv())
