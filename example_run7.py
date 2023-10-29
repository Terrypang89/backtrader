#The broker says: Show me the money!
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
        self.dataclose = self.datas[0].close

	    # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def notify_order(self, order):
    #be notified through notify_order(order) of any status change in an order
        if order.status == order.Submitted:
                print("order.Submitted with notify order %s" % str(order.status))
        if order.status == order.Accepted:
                print("order.Accepted with notify order %s" % str(order.status))
        if order.status == order.Completed:
                print("order.Completed with notify order %s" % str(order.status))

        if order.status in [order.Submitted, order.Accepted]:
		# Buy/Sell order submitted/accepted to/by broker - Nothing to do
                return

	    # Check if an order has been completed
	    # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
                if order.isbuy():
                        self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f'
                            %(order.executed.price, order.executed.value, order.executed.comm))

                        self.buyprice = order.executed.price
                        self.buycomm = order.executed.comm

                else: # sell
                        self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                            (order.executed.price, order.executed.value, order.executed.comm))

                self.bar_executed = len(self)
                print("bar_executed: %d" % self.bar_executed)
                # len(self) is how many next function been through or bar bas been run through

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                self.log('order Canceled/Margin/Rejected')

	    # write down: no pending order so make next self.order skipped
        self.order = None

    def notify_trade(self, trade):
    # be notified through notify_trade(trade) of any opening/updating/closing trade
        #print("notify_trade trade: %s" % trade)
        if not trade.isclosed:
            return

        # when trade.isclosed == 1, so when buy trade.isopened, and sell trade.isclosed, to get the profit
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    #def notify_cashvalue(self, cash, value):
    #be notified through notify_cashvalue(cash, value) of the current cash and portfolio in the broker

    #def notify_fund(self, cash, value, fundvalue, shares):
    #be notified through notify_fund(cash, value, fundvalue, shares) of the current cash and portfolio in the broker and tradking of fundvalue and shares

    #notify_store(self, msg, *args, **kwargs):
    #Events (implementation specific) via notify_store(msg, *args, **kwargs)

    #See Cerebro for an explanation on the store notifications. These will delivered to the strategy even if they have also been delivered to a cerebro instance (with an overriden notify_store method or via a callback)

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        #self.log('Close, %.2f , position: %s' % (self.dataclose[0], self.position))

	    # check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
                return

	    # Check if we are in the market
        # when self.position.closed == -1 or self.position.opened == 0
        if not self.position:

		        # current close less than previous close
                if self.dataclose[0] < self.dataclose[-1]:

			            # current close less than previous close
                        if self.dataclose[-1] < self.dataclose[-2]:
                		# previous close less than the previous close

                		        # BUY, BUY, BUY!!! (with all possible default parameters)
                                self.log('BUY CREATE, %.2f' % self.dataclose[0])

				                # Keep track of the created order to avoid a 2nd order
                                self.order = self.buy()
                                #Methods buy and sell return the created (not yet executed) order, which is notify_order

                                # self.position.opened = 1 after self.order = self.buy()
                                # self.position.size = 0, self.position.closed = 0

        # when self.position.opened == 1, self.position.closed = 0
        else:
		        # Already in the market ... we might sell
                if len(self) >= (self.bar_executed + 5):
                # Exit after 5 bars (on the 6th bar) have elapsed for good or for worse

			            # SELL, SELL, SELL!!! (with all possible default parameters)
                        self.log('SELL CREATE, %.2f' % self.dataclose[0])

			            # Keep track of the created order to avoid a 2nd order
                        self.order = self.sell()
                        # #Methods buy and sell return the created (not yet executed) order, which is notify_order

                        #  self.position.closed = -1 after self.order = self.sell()
                        #  self.position.size = 0, self.position.opened = 0

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
	    # do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    #setting Cash
    cerebro.broker.setcash(50000.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #resulting cerebro instance was told to run (loop over data)
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot(style='candlestick')