#Adding an indicator
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import time
from pprint import pprint

# Import the backtrader platform
import backtrader as bt

class TrendLine(bt.Indicator):

    lines = ('signal','trend')
    params = (
        ('x1', None),
        ('y1', None),
        ('x2', None),
        ('y2', None)
    )

    def __init__(self):
        #x1 = datetime.datetime.strptime("1995-07-20", "%Y-%m-%d")
        #x2 = datetime.datetime.strptime("1995-03-21", "%Y-%m-%d")
        print("self.data.close[0] = %s" % self.data.close[0])
        #pprint(vars(self.data.close))
        #pprint(vars(self.data))
        #pprint(vars(self))
        pprint(vars(self.strategy))
        #dir(self.data)
        self.p.x1 = datetime.datetime.strptime("1996-07-20", "%Y-%m-%d")
        self.p.x2 = datetime.datetime.strptime("1996-03-21", "%Y-%m-%d")
        print("self = %s" %self)

        #for i,j,k,l,m,n,o in self.datas[0]:
        #    print("i = %s, j = %s" %(m,n))
        #print("self.m = %s" % self.m)
        y1 = self.data.datetime[-10]
        y2 = self.data.close[0]
        print("self.data.datetime.time()  = %s" % self.data.datetime.time() )
        print("self.p.x1 = %s, self.p.x2= %s " %(self.p.x1 ,self.p.x2))
        print("y1 = %s, y2= %s " %(y1 ,y2))
        #print("data value = " % datetime.datetime.fromordinal(int(self.getdatabyname(ticker).datetime[-10]))
        print("self.p.x1.timetuple() = %s" %self.p.x1.timetuple())
        x1_time_stamp = time.mktime(self.p.x1.timetuple())
        x2_time_stamp = time.mktime(self.p.x2.timetuple())
        self.m = self.get_slope(x1_time_stamp,x2_time_stamp,self.p.y1,self.p.y2)
        self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
        self.plotlines.trend._plotskip = True

    def next(self):

        date = self.data0.datetime.datetime()
        date_timestamp = time.mktime(date.timetuple())
        Y = self.get_y(date_timestamp)
        print("y in next= %s" % y)
        self.lines.trend[0] = Y

        #Check if price has crossed up / down into it.
        if self.data0.high[-1] < Y and self.data0.high[0] > Y:
            self.lines.signal[0] = -1
            return

        #Check for cross downs (Into support)
        elif self.data0.low[-1] > Y and self.data0.low[0] < Y:
            self.lines.signal[0] = 1
            return

        else:
            self.lines.signal[0] = 0

    def get_slope(self, x1,x2,y1,y2):
        print("y2 = %s, y1 = %s, x2 = %s, x1 = %s" %(y2, y1, x2, x1))
        m = (y2-y1)/(x2-x1)
        return m

    def get_y_intercept(self, m, x1, y1):
        b=y1-m*x1
        return b

    def get_y(self,ts):
        Y = self.m * ts + self.B
        print("y at get_y = %s" %y)
        return Y

# Create a Stratey
class TestStrategy(bt.Strategy):

    #add parameters
    params = (
        ('maperiod', 15),
        ('exitbars', 5),
        #('x1', None),
        #('y1', None),
        #('x2', None),
        #('y2', None)
    )

    #lines = ('signal','trend')


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

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

        #self.p.x1 = datetime.datetime.strptime("1995-03-21", "%Y-%m-%d")
        #self.p.x2 = datetime.datetime.strptime("1995-07-28", "%Y-%m-%d")
        #x1_time_stamp = time.mktime(self.p.x1.timetuple())
        #x2_time_stamp = time.mktime(self.p.x2.timetuple())
        #self.m = self.get_slope(x1_time_stamp,x2_time_stamp,self.p.y1,self.p.y2)
        #self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
        #self.plotlines.trend._plotskip = True

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
                        # this to add sum to cerebro.broker.cashvalue

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
		        # Not yet ... we MIGHT BUY if ...
                if self.dataclose[0] > self.sma[0]:

			            # BUY, BUY, BUY!!! (with all possible default parameters)
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])

                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy()
                        #Methods buy and sell return the created (not yet executed) order, which is notify_order

                        # self.position.opened = 1 after self.order = self.buy()
                        # self.position.size = 0, self.position.closed = 0

        # when self.position.opened == 1, self.position.closed = 0
        else:
                if self.dataclose[0] < self.sma[0]:
             		# SELL, SELL, SELL!!! (with all possible default parameters)
                        self.log('SELL CREATE, %.2f' % self.dataclose[0])

                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.sell()
                        # #Methods buy and sell return the created (not yet executed) order, which is notify_order

                        #  self.position.closed = -1 after self.order = self.sell()
                        #  self.position.size = 0, self.position.opened = 0

        # default buy function
        # def buy(self, data=None, size=None, price=None, plimit=None, exectype=None, valid=None, tradeid=0, **kwargs):

        #date = self.data0.datetime.datetime()
        #date_timestamp = time.mktime(date.timetuple())
        #Y = self.get_y(date_timestamp)
        #self.lines.trend[0] = Y

        #Check if price has crossed up / down into it.
        #if self.data0.high[-1] < Y and self.data0.high[0] > Y:
        #    self.lines.signal[0] = -1
        #    return

        #Check for cross downs (Into support)
        #elif self.data0.low[-1] > Y and self.data0.low[0] < Y:
        #    self.lines.signal[0] = 1
        #    return

        #else:
        #    self.lines.signal[0] = 0

    #def get_slope(self, x1,x2,y1,y2):
    #    m = (y2-y1)/(x2-x1)
    #    return m

    #def get_y_intercept(self, m, x1, y1):
    #    b=y1-m*x1
    #    return b

    #def get_y(self,ts):
    #    Y = self.m * ts + self.B
    #    return Y

if __name__ == '__main__':

    #Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    #cerebro.addstrategy(TestStrategy)
    cerebro.addstrategy(TrendLine)
    # cerebro.addstrategy(TestStrategy, myparam=20, exitbars=7) for alternative add parameters values

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'datas/yhoo-1996-2014.txt')

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

    #self.p = data

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    #setting Cash
    cerebro.broker.setcash(50000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    # Sizer simply buys/sells using a stake of 1 units (be it shares, contracts, …)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #resulting cerebro instance was told to run (loop over data)
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot(style='candlestick')
