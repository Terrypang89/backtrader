'''
Author: www.backtest-rookies.com

MIT License

Copyright (c) 2019 backtest-rookies.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import numpy as np
import backtrader as bt
from datetime import datetime

# IMPORTANT!
# ----------
# Register for an API at:
# https://www.alphavantage.co/support/#api-key
# Then insert it here.
# Apikey = 'INSERT YOUR API KEY'
Apikey = "XCPIF0EE4CIZ0UUP"


def alpha_vantage_eod(symbol_list, compact=False, debug=False, *args, **kwargs):
    '''
    Helper function to download Alpha Vantage Data.

    This will return a nested list with each entry containing:
        [0] pandas dataframe
        [1] the name of the feed.
    '''
    data_list = list()

    size = 'compact' if compact else 'full'

    for symbol in symbol_list:

        if debug:
            print('Downloading: {}, Size: {}'.format(symbol, size))

        # Submit our API and create a session
        alpha_ts = TimeSeries(key=Apikey, output_format='pandas')

        data, meta_data = alpha_ts.get_daily(symbol=symbol, outputsize=size)

        #Convert the index to datetime.
        data.index = pd.to_datetime(data.index)
        data.columns = ['Open', 'High', 'Low', 'Close','Volume']

        if debug:
            print(data)

        data_list.append((data, symbol))

    return data_list

class TestStrategy(bt.Strategy):

    def __init__(self):

        pass

    def next(self):

        for i, d in enumerate(self.datas):

            bar = len(d)
            dt = d.datetime.datetime()
            dn = d._name
            o = d.open[0]
            h = d.high[0]
            l = d.low[0]
            c = d.close[0]
            v = d.volume[0]


            print('{} Bar: {} | {} | O: {} H: {} L: {} C: {} V:{}'.format(dt, bar,dn,o,h,l,c,v))


# Create an instance of cerebro
cerebro = bt.Cerebro()

# Add our strategy
cerebro.addstrategy(TestStrategy)

# Download our data from Alpha Vantage.
symbol_list = ['LGEN.L','LLOY.L']
data_list = alpha_vantage_eod(
                symbol_list,
                compact=False,
                debug=False)

for i in range(len(data_list)):

    data = bt.feeds.PandasData(
                dataname=data_list[i][0], # This is the Pandas DataFrame
                name=data_list[i][1], # This is the symbol
                timeframe=bt.TimeFrame.Days,
                compression=1,
                fromdate=datetime(2018,1,1),
                todate=datetime(2019,1,1)
                )

    #Add the data to Cerebro
    cerebro.adddata(data)

print('Starting to run')
# Run the strategy
cerebro.run()
