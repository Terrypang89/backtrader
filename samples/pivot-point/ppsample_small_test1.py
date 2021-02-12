#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2020 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

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
from pivotpoint import PivotPoint, PivotPoint1

def time2date(cus_time):
    return datetime.datetime.strptime(cus_time, "%Y-%m-%d").date()

def df2time():
    pass

def time2df(cust_time):
    pass

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

    parser.add_argument('--noheaders', action='store_true', default=False,
                        required=False,
                        help='Do not use header rows')

    parser.add_argument('--noprint', action='store_true', default=False,
                        help='Print the dataframe')

    return parser.parse_args()


class St(bt.Strategy):
    params = (('usepp1', False),
              ('plot_on_daily', False),
              ('x1', None),
              ('y1', None),
              ('x2', None),
              ('y2', None))

    def __init__(self):
        pass
        #if self.p.usepp1:
        #    self.pp = PivotPoint1(self.data1)
        #else:
        #    self.pp = PivotPoint2(self.data1)

        #if self.p.plot_on_daily:
        #    self.pp.plotinfo.plotmaster = self.data0
        # must convert self.p.x1 and x2 to timestamp

    def next(self):
        txt = ','.join(
            ['%04d' % len(self),
             '%04d' % len(self.data0),
             '%04d' % len(self.data1),
             #'%04d' % 3000,
             self.data.datetime.date(0).isoformat(),
             '%s' %self.data0.datetime.datetime()]
             )
        print(txt)

if __name__ == '__main__':
    args = parse_args()

    cerebro = bt.Cerebro(stdstats=False)

    cerebro.addstrategy(St, plot_on_daily=args.plot_on_daily)

    datapath = "../../datas/2005-2006-day-001.txt"
    print("datapath =%s" %datapath)
    skiprows = 1 if args.noheaders else 0
    header = None if args.noheaders else 0
    dataframe = pd.read_csv(datapath,
                                index_col=0)
    print(dataframe.index)
    dataframe.index = pd.to_datetime(dataframe.index, format='%Y-%m-%d')
    #dataframe.test = pd.DataFrame(datapath, index = ['Date','Open','High','Low','Close','Volume','OpenInterest'])

    print('--------------------------------------------------')
    print(dataframe)
    print('--------------------------------------------------')

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=dataframe)

    print('--------------------------------------------------')
    #pprint(data)
    print('--------------------------------------------------')

    cerebro.adddata(data)

    cerebro.resampledata(data, timeframe=bt.TimeFrame.Months)
    #cerebro.run()
    cerebro.run(runonce=False)
    if args.plot:
        cerebro.plot(style='bar')
