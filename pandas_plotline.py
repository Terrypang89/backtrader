
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime
import time
import os
import sys
from pprint import pprint
import pandas as pd
# The above could be sent to an independent module
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
from backtrader.analyzers import (SQN, AnnualReturn, TimeReturn, SharpeRatio,
                                  TradeAnalyzer)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Pandas test script')

    parser.add_argument('--noheaders', action='store_true', default=False,
                        required=False,
                        help='Do not use header rows')

    parser.add_argument('--noprint', action='store_true', default=False,
                        help='Print the dataframe')

    return parser.parse_args()

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
        print("hello")
        self.p.x1 = datetime.datetime.strptime("1996-04-12", "%Y-%m-%d").date()
        self.p.x2 = datetime.datetime.strptime("2014-12-31", "%Y-%m-%d").date()
        #print("convert2timestamep = %s" %bt.date2num(datetime.datetime.strptime("2014-12-30 23:59:59.999989", "%Y-%m-%d %H:%M:%S.%f")))
        print("self.p.x1 = %s" %self.p.x1)
        print("self.p.x2 = %s" %self.p.x2)
        print("len(self) = %s" %len(self.data.line6))
        #print("value from pandas = %S" % self.data.iloc["2014-12-31"])
        #pprint(vars(dataframe["2014-12-31"]))
        print("dataframe.index = %s" % dataframe.index )
        print("dataframe.loc[2014-12-31, :] = %s" % dataframe.loc["2014-12-31", :] )
        print("dataframe.loc[2014-12-31, Close] = %s" % dataframe.loc["2014-12-31", "Close"] )
        #print("dataframe.index = %s" % dataframe.at[12, ""] )
        #print("self.data.close.get(size=1, ago=-1)[0] = %s" % self.data0.get(size=1))
        #pprint(vars(pandas.DataFrame({'Date': ["1996-04-23", "1996-04-27"]})))
        #pprint(vars(self.data.get()))
        #pprint(vars(pandas.data_range(start='23/04/1996', period=0)))
        x1_time_stamp = bt.date2num(self.p.x1)
        x2_time_stamp = bt.date2num(self.p.x2)
        print("x1_time_stamp = %s" %x1_time_stamp)
        print("x2_time_stamp = %s" %x2_time_stamp)
        self.p.y1 = dataframe.loc[self.p.x1, "Close"]
        self.p.y2 = dataframe.loc[self.p.x2, "Close"]
        self.m = self.get_slope(x1_time_stamp,x2_time_stamp,self.p.y1,self.p.y2)
        print("self.m = %s" %self.m)
        self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
        print("self.B = %s" %self.B)
        #pprint(vars(self.plotlines.trend))
        self.plotlines.trend._plotskip = False

    def next(self):
        print("start next")
        date = self.data0.datetime.datetime()

        print("date_timestamp = %s" %date_timestamp)
        Y = self.get_y(date_timestamp)
        print("Y = %s" %Y)
        self.lines.trend[0] = Y

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

    args = parse_args()

    cerebro = bt.Cerebro(stdstats=False)

    cerebro.addstrategy(TrendLine)

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'datas/yhoo-1996-2014.txt')

    print('Data at: %s' % str(datapath))

    skiprows = 1 if args.noheaders else 0
    header = None if args.noheaders else 0

    print("skiprows = %s , header = %s" %(skiprows,header))
    dataframe = pd.read_csv(datapath,
                                skiprows=skiprows,
                                header=header,
                                parse_dates=True,
                                index_col=0)

    dataframe.index = pd.to_datetime(dataframe.index, format='%Y-%m-%d')

    #if not args.noprint:
    print('--------------------------------------------------')
    print(dataframe)
    print('--------------------------------------------------')


    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=dataframe)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    cerebro.run()

    cerebro.plot(style='candlestick')
