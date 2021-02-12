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

class PivotPoint2(bt.Indicator):
    lines = ('p', 's1', 's2', 'r1', 'r2', 'p2')
    plotinfo = dict(subplot=False)

    def __init__(self):
        h = self.data.high  # current high
        l = self.data.low  # current high
        c = self.data.close  # current high

        self.lines.p = p = (h + l + c) / 3.0

        print("type = %s" % type(self.lines.p))
        p2 = p * 2.0
        self.lines.s1 = p2 - h  # (p x 2) - high
        self.lines.r1 = p2 - l  # (p x 2) - low
        self.p.x2 = datetime.datetime.strptime("2005-04-22", "%Y-%m-%d").date()
        self.p.y2 = dataframe.loc[self.p.x2, "Close"]
        print("self.p.y2 = %s" %self.p.y2)
        self.lines.p2 = int(self.p.y2) * p2 / p2

        hilo = h - l
        self.lines.s2 = p - hilo  # p - (high - low)
        self.lines.r2 = p + hilo  # p + (high - low)


class St(bt.Strategy):
    lines = ('signal','trend')
    params = (('usepp1', False),
              ('plot_on_daily', False),
              ('x1', None),
              ('y1', None),
              ('x2', None),
              ('y2', None))

    def __init__(self):
        self.p.x1 = datetime.datetime.strptime("2005-01-28", "%Y-%m-%d").date()
        self.p.x2 = datetime.datetime.strptime("2005-04-22", "%Y-%m-%d").date()

        self.p.y1 = dataframe.loc[self.p.x1, "Close"]
        self.p.y2 = dataframe.loc[self.p.x2, "Close"]
        print("self.p.x1 = %s" %self.p.x1)
        print("self.p.x2 = %s" %self.p.x2)
        print("self.p.y1 = %s" %self.p.y1)
        print("self.p.y2 = %s" %self.p.y2)
        if self.p.usepp1:
            self.pp = PivotPoint1(self.data1)
        else:
            self.pp = PivotPoint2(self.data1)

        if self.p.plot_on_daily:
            self.pp.plotinfo.plotmaster = self.data0
        #pprint(vars(self.p))
        #pprint(vars(self.pp.lines))

    def next(self):
        txt = ','.join(
            ['%04d' % len(self),
             '%04d' % len(self.data0),
             '%04d' % len(self.data1),
             '%04d' % 3000,
             self.data.datetime.date(0).isoformat(),
             '%04d' % len(self.pp),
             '%.2f' % self.pp[0]],
             )
        print("lines = %s, %s, %s, %s, %s, %s" %(self.pp.lines.p[0], self.pp.lines.s1[0], self.pp.lines.s2[0], self.pp.lines.r1[0], self.pp.lines.r2[0], self.pp.lines.p2[0]))
        #print(txt)

if __name__ == '__main__':
    args = parse_args()

    cerebro = bt.Cerebro(stdstats=False)

    cerebro.addstrategy(St,
                        usepp1=args.usepp1,
                        plot_on_daily=args.plot_on_daily)

    datapath = "../../datas/2005-2006-day-001.txt"
    print("datapath =%s" %datapath)
    dataframe = pd.read_csv(datapath,
                                skiprows=0,
                                header=0,
                                parse_dates=True,
                                index_col=0)

    dataframe.index = pd.to_datetime(dataframe.index, format='%Y-%m-%d')

    #if not args.noprint:
    print('--------------------------------------------------')
    #print(dataframe)
    print('--------------------------------------------------')

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=dataframe)

    cerebro.adddata(data)

    cerebro.resampledata(data, timeframe=bt.TimeFrame.Months)
    #cerebro.run()
    cerebro.run(runonce=False)
    if args.plot:
        cerebro.plot(style='bar')


#if __name__ == '__main__':
#    runstrat()
