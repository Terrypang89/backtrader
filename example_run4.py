#Our First Strategy
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        print("init teststrategy")
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        print("next teststrategy")
        self.log('Close, %.2f' % self.dataclose[0])

if __name__ == '__main__':

    #Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'datas/orcl-1995-2014.txt')

    print('Data at: %s' % str(datapath))

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2000, 1, 1),
        # Do not pass values after this date
        todate=datetime.datetime(2000, 12, 31),
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    #setting Cash
    cerebro.broker.setcash(50000.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #resulting cerebro instance was told to run (loop over data)
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

