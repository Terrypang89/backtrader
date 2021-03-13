
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime
import time
import os
import sys
from pprint import pprint
# The above could be sent to an independent module
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
from backtrader.analyzers import (SQN, AnnualReturn, TimeReturn, SharpeRatio,
                                  TradeAnalyzer)

class TrendLine(bt.Indicator):
    '''
    This indicator shall produce a signal when price reaches a calculated trend line.

    The indicator requires two price points and date points to serve as X and Y
    values in calcuating the slope and the future expected price trend

    x1 = Date/Time, String in the following format "YYYY-MM-DD HH:MM:SS" of
    the start of the trend
    y1 = Float, the price (Y value) of the start of the trend.
    x2 = Date/Time, String in the following format "YYYY-MM-DD HH:MM:SS" of
    the end of the trend
    y2 = Float, the price (Y value) of the end of the trend.
    '''

    lines = ('signal','trend')
    params = (
        ('x1', None),
        ('y1', None),
        ('x2', None),
        ('y2', None)
    )

    def __init__(self):
        #if self.p.y1 is None:
            #self.p.y1 = self.data.line
        self.p.x1 = datetime.datetime.strptime("1996-04-12", "%Y-%m-%d").date()
        self.p.x2 = datetime.datetime.strptime("2014-12-31", "%Y-%m-%d").date()
        #print("convert2timestamep = %s" %bt.date2num(datetime.datetime.strptime("2014-12-30 23:59:59.999989", "%Y-%m-%d %H:%M:%S.%f")))
        print("self.p.x1 = %s" %self.p.x1)
        print("self.p.x2 = %s" %self.p.x2)
        print("len(self) = %s" %len(self.data.line6))
        #print("self.data.close.get(size=1, ago=-1)[0] = %s" % self.data.close.get(size=1)[0])
        #pprint(vars(self.l[0]))
        x1_time_stamp = bt.date2num(self.p.x1) + 0.9999999999
        x2_time_stamp = bt.date2num(self.p.x2) + 0.9999999999
        print("x1_time_stamp = %s" %x1_time_stamp)
        print("x2_time_stamp = %s" %x2_time_stamp)
        #x1_time_stamp = time.mktime(self.p.x1.timetuple())
        #x2_time_stamp = time.mktime(self.p.x2.timetuple())
        #pprint(vars(self.data.line6))
        self.m = self.get_slope(x1_time_stamp,x2_time_stamp,self.p.y1,self.p.y2)
        #print("self.m =%s" %self.m )
        self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
        #self.plotlines.trend._plotskip = True

    def next(self):
        print("test test")
        date = self.data0.datetime.datetime()

        #Y = self.get_y(date_timestamp)
        #self.lines.trend[0] = Y

        if self.data0.high[-1] < Y and self.data0.high[0] > Y:
            self.lines.signal[0] = -1
            return

        elif self.data0.low[-1] > Y and self.data0.low[0] < Y:
            self.lines.signal[0] = 1
            return

        else:
            self.lines.signal[0] = 0

    def get_slope(self, x1,x2,y1,y2):
        print("x1 = %s" %x1)
        print("y1 = %s" %y1)
        print("x2 = %s" %x2)
        print("y2 = %s" %y2)
        m = (y2-y1)/(x2-x1)
        return m

    def get_y_intercept(self, m, x1, y1):
        b=y1-m*x1
        return b

    def get_y(self,ts):
        Y = self.m * ts + self.B
        return Y

if __name__ == '__main__':
    #Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)

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
        fromdate=datetime.datetime(1996, 4, 12),
        # Do not pass values after this date
        todate=datetime.datetime(2014, 12, 31),
	    # do not pass values after this date
        reverse=False)

    cerebro.adddata(data)

    #cerebro.broker.setcash(50000.0)

    #cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    #cerebro.broker.setcommission(commission=0.0)

    #print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    #print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot(style='candlestick')
