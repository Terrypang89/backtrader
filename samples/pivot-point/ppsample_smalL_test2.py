
import argparse
import datetime
import time
import os
import sys
from pprint import pprint
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.utils.flushfile
import backtrader.indicators as btind
import pandas as pd
#from pivotpoint import PivotPoint, PivotPoint1

def time2date(cus_time):
    return datetime.datetime.strptime(cus_time, "%Y-%m-%d").date()

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Sample for pivot point and cross plotting')

    parser.add_argument('--data', required=False,
                        default='../../datas/2005-2006-day-001.txt',
                        help='Data to be read in')

    parser.add_argument('--usepp1', required=False, action='store_true',
                        help='Have PivotPoint look 1 period backwards')

    parser.add_argument('--plot', required=False, action='store_true',
                        help=('Plot the result'))

    parser.add_argument('--plot-on-daily', required=False, action='store_true',
                        help=('Plot the indicator on the daily data'))

    return parser.parse_args()

class MyStochastic2(bt.Indicator):
    lines = ('k', 'd', 'mystoc',)
    params = (
        ('k_period', 14),  # lookback period for highest/lowest
        ('d_period', 3),  # smoothing period for d with the SMA
    )
    def __init__(self):
        self.addminperiod(self.p.k_period + self.p.d_period)

    def next(self):
        # Get enough data points to calculate k and do it
        d = self.data.get(size=self.p.k_period)
        hi = max(d)
        lo = min(d)
        self.lines.k[0] = k0 = (self.data[0] - lo) / (hi - lo)
        # Get enough ks to calculate the SMA of k. Assign to d
        last_ks = self.l.k.get(size=self.p.d_period)
        self.lines.d[0] = sum(last_ks) / self.p.d_period
        # Now calculate mystoc
        self.lines.mystoc[0] = abs(k0 - self.l.k[-1]) / 2.0


if __name__ == '__main__':
    args = parse_args()
    cerebro = bt.Cerebro(stdstats=False)

    cerebro.addstrategy(MyStochastic2)

    datapath = "../../datas/2005-2006-day-001.txt"
    print("datapath =%s" %datapath)
    header = ['Date','Open','High','Low','Close','Volume','OpenInterest']
    skiprows = 0
    header = 0
    dataframe = pd.read_csv(datapath,
                                #skiprows=skiprows,
                                header=header,
                                parse_dates=True,
                                index_col=0)
    print(dataframe.index)
    dataframe.index = pd.to_datetime(dataframe.index, format='%Y-%m-%d')

    print('--------------------------------------------------')
    print(dataframe)
    print('--------------------------------------------------')

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=dataframe)

    cerebro.adddata(data)

    cerebro.resampledata(data)
    #cerebro.run()
    cerebro.run(runonce=False)


    if args.plot:
        cerebro.plot(style='bar')
