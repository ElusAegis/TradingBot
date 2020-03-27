# IMPORTS
import pandas as pd
import math
import os.path
import time
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser

### API
binance_api_key = 'usSziTXvOCyDwC3foIlDHwH89DYJzbV6p0SrZ5MW9vKS6egRbfkLu21RYNur2AjI'    #Enter your own API-key here
binance_api_secret = 'bdli147dBckDvLgKaul5N4dfaxTEcCAKoRdF6JbbbVza6FlHOa0ro3y34h0RISHE' #Enter your own API-secret here

### CONSTANTS
binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
batch_size = 999
binance_client = Client(api_key=binance_api_key, api_secret=binance_api_secret)
start_time = datetime.strptime('1 Jan 2017', '%d %b %Y')
backup_frequency = 20

### FUNCTIONS
def minutes_of_new_data(symbol, kline_size, data):
    if len(data) > 0:
        old = parser.parse(data["timestamp"].iloc[-1])
    else:
        old = start_time
    new = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms')
    return old, new

def get_all_binance(symbol, kline_size, save = False, verbose = False):
    filename = 'stock_data/crypto_currency/%s-%s-%s-data.csv' % (symbol, kline_size, start_time)
    if os.path.isfile(filename):
        data_df = pd.read_csv(filename)
    else:
        data_df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
        data_df.to_csv(filename)

    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df)
    delta_min = (newest_point - oldest_point).total_seconds()/60
    request_frame = timedelta(minutes=binsizes[kline_size] * batch_size)
    available_data = math.ceil(delta_min/binsizes[kline_size])

    if available_data == 0:
        print('Already all caught up..!')
        return data_df

    if oldest_point == start_time:
        print('Downloading all available %s data for %s. Be patient..!' % (kline_size, symbol))
    else:
        print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.'
              % (delta_min, symbol, available_data, kline_size))

    average_time = 0
    round_number = 0
    rounds_left = math.ceil(float((newest_point - oldest_point).total_seconds())/request_frame.total_seconds())

    while oldest_point < newest_point:

        if verbose:
            round_time = time.time()

        next_oldest_point = min(newest_point, oldest_point + request_frame)

        klines = binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"),
                                                      next_oldest_point.strftime("%d %b %Y %H:%M:%S"), limit=batch_size)
        data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        if len(data_df) > 0:
            temp_df = pd.DataFrame(data)
            data_df = data_df.append(temp_df)
        else:
            data_df = data
        data_df.set_index('timestamp', inplace=True)
        if save and not round_number % backup_frequency:
            data_df.to_csv(filename, mode='a', header=False)

        oldest_point = next_oldest_point

        round_number += 1

        if verbose:
            round_time = time.time() - round_time
            average_time = (average_time * round_number + round_time) / (round_number + 1)

            rounds_left -= 1

            left_time = rounds_left * average_time

            time_multipliers = {1: "seconds", 60: "minutes", 3600: "hours"}
            time_multiplier = 1
            while left_time // time_multiplier > 180 and time_multiplier < 3600:
                time_multiplier *= 60

            print("Average time for a round is {:.1f} sec. It will take {:.1f} {} more, {:.1f}% done.".format(
                  average_time, left_time / time_multiplier, time_multipliers[time_multiplier],
                    round_number * 100. / (rounds_left + round_number)))

    print('All caught up..!')
    return data_df


if __name__ == "__main__":
    print(get_all_binance("BNBBTC", "1m", save=True, verbose=True))