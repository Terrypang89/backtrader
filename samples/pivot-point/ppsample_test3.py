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

    return parser.parse_args()

class PivotPoint2(bt.Indicator):
    lines = ('p', 's1', 's2', 'r1', 'r2', 'p2', 'signal','trend')
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

        hilo = h - l
        self.lines.s2 = p - hilo  # p - (high - low)
        self.lines.r2 = p + hilo  # p + (high - low)

        self.p.x1 = time2date("2005-01-28")
        self.p.x2 = time2date("2006-05-31")

        self.p.y1 = dataframe.loc[self.p.x1, "Close"]
        self.p.y2 = dataframe.loc[self.p.x2, "Close"]
        #bb = dataframe.loc[int(2962.28), "Date"]
        #dfb = dataframe[dataframe["Close"]==self.p.y1].index.values
        dfb = dataframe[dataframe["Close"]==self.p.y1].index.item().date()
        print("dfb =%s" %dfb)
        tt = bt.date2num(dfb)
        print("tt = %s" %tt)
        #print("test get back date:=%s" %)
        #self.log('Stock 1 Close, %.2f' % self.Stock1close[0])
        print("self.p.x1 = %s" %self.p.x1)
        print("self.p.x2 = %s" %self.p.x2)
        print("self.p.y1 = %s" %self.p.y1)
        print("self.p.y2 = %s" %self.p.y2)

        x1_time_stamp = bt.date2num(self.p.x1)
        x2_time_stamp = bt.date2num(self.p.x2)
        print("x1_time_stamp = %s" %x1_time_stamp)
        print("x2_time_stamp = %s" %x2_time_stamp)
        print("total data len=%s" %len(self.data.low))
        self.m = self.get_slope(x1_time_stamp, x2_time_stamp, self.p.y1, self.p.y2)
        self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
        self.PREV_Y = self.get_y(x1_time_stamp)

    def next(self):
        date_ori = self.data0.datetime.datetime()
        date_timestamp = bt.date2num(date_ori)
        date_back = bt.num2date(date_timestamp).date()

        Y = self.get_y(date_timestamp)
        self.lines.trend[0] = Y

        k = self.detect_lowest(date_ori, -6)
        j = self.detect_highest(date_ori, -6)
        if k == True or j == True:

            self.p.y1 = self.PREV_Y
            self.p.y2 = self.data0.low[0]
            x1_time_stamp = get_x_timestamp(self.p.y1, "close")
            x2_time_stamp = date_timestamp
            self.m = self.get_slope(x1_time_stamp, x2_time_stamp, self.p.y1, self.p.y2)
            self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
            self.PREV_Y = self.p.y1

        if self.data0.high[-1] < Y and self.data0.high[0] > Y:
            self.lines.signal[0] = 0
        elif self.data0.low[-1] > Y and self.data0.low[0] < Y:
            self.lines.signal[0] = Y
        else:
            self.lines.signal[0] = 0
        #print("[%s], (%s), trend=%s, self.B=%s, high=%s, low=%s, signal=%s, length=%s" %(date_timestamp, date_back, Y, self.B, self.data0.high[0], self.data0.low[0], self.lines.signal[0], len(self.data0)))
        return

    def get_slope(self, x1,x2,y1,y2):
        print("x1 = %s" %x1)
        print("y1 = %s" %y1)
        print("x2 = %s" %x2)
        print("y2 = %s" %y2)
        m = (y2-y1)/(x2-x1)
        return m

    def get_x_timestamp(self, y_val, index_type):
        dfb = dataframe[dataframe[index_type]==y_val].index.item()
        return bt.date2num(dfb)

    def __bt_to_pandas__(self, btdata, len):
        get = lambda mydata: mydata.get(ago=0, size=len)

        fields = {
            'open': get(btdata.open),
            'high': get(btdata.high),
            'low': get(btdata.low),
            'close': get(btdata.close),
            'volume': get(btdata.volume)
        }
        time = [btdata.num2date(x) for x in get(btdata.datetime)]

        return pd.DataFrame(data=fields, index=time)

    def get_y_intercept(self, m, x1, y1):
        b=y1-m*x1
        return b

    def get_y(self,ts):
        Y = self.m * ts + self.B
        return Y

    def detect_lowest(self, cur_date, offtset_val):
        # to detect the lowest, this must not be used for first
        # assume the prev 5 are 0 when at the start datetime of data
        #sequence = [-1, -2, -3, -4, -5 ]
        ret_val = 0
        if offtset_val is None or not offtset_val or offtset_val == "":
            offtset_val = -6

        for x1 in range(offtset_val, -1):
            if len(self.data0) <= 2*abs(offtset_val):
                ret_val = ret_val + 1
            else:
                if self.data0.low[offtset_val] <= self.data0.low[x1+offtset_val]:
                    ret_val = ret_val + 1
                if self.data0.low[offtset_val] <= self.data0.low[abs(x1)+ offtset_val]:
                    ret_val = ret_val + 1

        if ret_val == abs(offtset_val)*2:
            return True # return true to current -6 value from
        else:
            return False

    def detect_highest(self, cur_date, offset_val):
        ret_val = 0
        if offset_val is None or not offset_val or offset_val == "":
            offset_val = -6

        for x3 in range(offset_val, -1):
            if len(self.data0) <= abs(offset_val)*2:
                ret_val = ret_val + 1
            else:
                if self.data0.high[offset_val] >= self.data0.high[x3+offset_val]:
                    ret_val = ret_val + 1
                if self.data0.high[offset_val] >= self.data0.low[abs(x3)+ offset_val]:
                    ret_val = ret_val + 1
        if ret_val == abs(offset_val)*2:
            return True # return true to current -6 value from
        else:
            return False

class St(bt.Strategy):
    params = (('usepp1', False),
              ('plot_on_daily', False),
              ('x1', None),
              ('y1', None),
              ('x2', None),
              ('y2', None))

    def __init__(self):

        if self.p.usepp1:
            self.pp = PivotPoint1(self.data1)
        else:
            self.pp = PivotPoint2(self.data1)
            print("<vars(self.pp)------------------------------------------------------------->")
            pprint(vars(self.pp))
            print("<vars(self.pp.lines)------------------------------------------------------------->")
            pprint(vars(self.pp.lines))
            print("<vars(self.pp.lines[7])------------------------------------------------------------->")
            pprint(vars(self.pp.lines[7]))
            print("<vars(self.pp.lines[7].p)------------------------------------------------------------->")
            pprint(vars(self.pp.lines[7].p))
            print("<vars(self.pp.lines[7].lines)------------------------------------------------------------->")
            pprint(vars(self.pp.lines[7].lines))
            print("<vars(self.pp.plotinfo)------------------------------------------------------------->")
            pprint(vars(self.pp.plotinfo))
            print("<vars(self.pp.plotlines)------------------------------------------------------------->")
            pprint(vars(self.pp.plotlines))
            print("<vars(self.pp.plotlines.signal)------------------------------------------------------------->")
            pprint(vars(self.pp.plotlines.signal))

        if self.p.plot_on_daily:
            self.pp.plotinfo.plotmaster = self.data0
        # must convert self.p.x1 and x2 to timestamp

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

if __name__ == '__main__':
    args = parse_args()

    cerebro = bt.Cerebro(stdstats=False)

    cerebro.addstrategy(St,
                        usepp1=args.usepp1,
                        plot_on_daily=args.plot_on_daily)

    datapath = "../../datas/2005-2006-day-001.txt"
    print("datapath =%s" %datapath)
    header = ['Date','Open','High','Low','Close','Volume','OpenInterest']
    skiprows = 0
    header = 0
    dataframe = pd.read_csv(datapath,
                                skiprows=skiprows,
                                header=header,
                                parse_dates=True,
                                index_col=0)
    print(dataframe.index)
    dataframe.index = pd.to_datetime(dataframe.index, format='%Y-%m-%d')
    #dataframe.test = pd.DataFrame(datapath, index = ['Date','Open','High','Low','Close','Volume','OpenInterest'])

    print('--------------------------------------------------')
    print(dataframe)
    print('--------------------------------------------------')

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=dataframe)

    cerebro.adddata(data)

    cerebro.resampledata(data, timeframe=bt.TimeFrame.Months)
    #cerebro.run()
    cerebro.run(runonce=False)
    if args.plot:
        cerebro.plot(style='bar')
