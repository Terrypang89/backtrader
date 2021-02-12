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
# This program is distributed in the hope that it will be useful
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
    lines = ('p', 's1', 's2', 'r1', 'r2', 'p2', 'signal','trend', 'test')
    plotinfo = dict(subplot=False)
    def __init__(self):
        #set the starting time and end time
        self.p.x1 = time2date("2005-01-28")
        self.p.y1 = dataframe.loc[self.p.x1, "Close"]
        x1_time_stamp = bt.date2num(self.p.x1)
        print("x1_time_stamp = %s" %x1_time_stamp)
        print("self.p.x1 = %s" %self.p.x1)
        print("self.p.y1 = %s" %self.p.y1)

        #x2 must be detect atg eary stage to have curve drawing started.
        self.p.x2 = time2date("2006-05-31")
        self.p.y2 = dataframe.loc[self.p.x2, "Close"]
        x2_time_stamp = bt.date2num(self.p.x2)
        print("self.p.x2 = %s" %self.p.x2)
        print("self.p.y2 = %s" %self.p.y2)
        print("x2_time_stamp = %s" %x2_time_stamp)

        print("total data len=%s" %len(self.data.low))
        self.m = self.get_slope(x1_time_stamp, x2_time_stamp, self.p.y1, self.p.y2)
        self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
        self.PREV_Y = self.get_y(x2_time_stamp)
        self.PREV_Y_state = "highest"
        #print("self.data0.low[1]=%s" %self.data0.low[1])
        self.PREV_X = x2_time_stamp

    def next(self):
        offset_value = -6
        date_ori = self.data0.datetime.datetime()
        date_timestamp = bt.date2num(date_ori)
        date_back = bt.num2date(date_timestamp).date()
        print("date_ori=%s" %date_ori)
        self.lines.trend[0] = self.data0.low[0]
        #at least double length distance from current value must be applied
        if len(self.data0) >= abs(offset_value):
            date_offset = self.get_offset_val(offset_value)
            date_timestamp_offset = bt.date2num(date_offset)
            date_back_offset = bt.num2date(date_timestamp_offset).date()

            k = self.detect_lowest(date_ori, offset_value)
            j = self.detect_highest(date_ori, offset_value)
            if k == "lowest": # this detection is the past offset value
                self.p.y1 = self.PREV_Y
                self.p.y2 = self.data0.low[offset_value]
                x1_time_stamp = self.PREV_X
                x2_time_stamp = date_timestamp_offset
                self.PREV_Y = self.p.y1
                self.PREV_Y_state = k
                self.PREV_X = x2_time_stamp
            elif j == "highest":
                self.p.y1 = self.PREV_Y
                self.p.y2 = self.data0.high[offset_value]
                x1_time_stamp = self.PREV_X
                x2_time_stamp = date_timestamp_offset
                self.PREV_Y = self.p.y1
                self.PREV_Y_state = j
                self.PREV_X = x2_time_stamp
            else:
                if self.PREV_Y_state == "lowest":
                    self.p.y2 = self.data0.high[0]
                elif self.PREV_Y_state == "highest":
                    self.p.y2 = self.data0.low[0]

                self.p.y1 = self.PREV_Y
                x1_time_stamp = self.PREV_X
                x2_time_stamp = date_timestamp

            self.m = self.get_slope(x1_time_stamp, x2_time_stamp, self.p.y1, self.p.y2)
            self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
            self.lines.test[offset_value] = self.get_y(date_timestamp_offset)
        else:
            self.lines.test[0] = self.get_y(date_timestamp)


    def get_offset_val(self, offset_val):
        if offset_val or offset_val < 0:
            #print("get_offset_val: len = %s, offset_val=%s, get_offset_val=%s" %(len(self.data0), offset_val, self.data0.datetime.date(offset_val)))
            return self.data0.datetime.date(offset_val)
        else:
            return None

    def get_x_time(self, y_val, index_type):
        #print("get_x_timestamp: y_val=%s, index_type=%s, get_x_time=%s" %(y_val, index_type, dataframe[dataframe["close"]==y_val].index.item()))
        print("get_x_timestamp: y_val=%s, index_type=%s" %(y_val, index_type))
        return dataframe[dataframe[index_type]==y_val].index.item()

    def get_slope(self, x1,x2,y1,y2):
        m = (y2-y1)/(x2-x1)
        return m

    def get_y_intercept(self, m, x1, y1):
        b=y1-m*x1
        return b

    def get_y(self,ts):
        Y = self.m * ts + self.B
        return Y

    def detect_lowest(self, cur_date, offset_val):
        # to detect the lowest, this must not be used for first
        # assume the prev 5 are 0 when at the start datetime of data
        #sequence = [-1, -2, -3, -4, -5 ]
        ret_val = 0
        if offset_val is None or not offset_val or offset_val == "":
            offset_val = -6

        for x1 in range(offset_val, -1):
            if len(self.data0) <= 2*abs(offset_val):
                ret_val = ret_val + 1
            else:
                if self.data0.low[offset_val] <= self.data0.low[x1+offset_val]:
                    ret_val = ret_val + (abs(offset_val) + x1 )
                if self.data0.low[offset_val] <= self.data0.low[abs(x1)+ offset_val]:
                    ret_val = ret_val + abs(x1)
                print("detect_lowest: ret_val=%s at date=%s, ori_date=%s" %(ret_val, self.data0.datetime.date(offset_val), cur_date))

        if ret_val >= abs(offset_val)*3:
            #print("detect_lowest: ret_val=%s" %ret_val)
            return "lowest" # return true to current -6 value from
        else:
            return None

    def detect_highest(self, cur_date, offset_val):
        ret_val = 0
        if offset_val is None or not offset_val or offset_val == "":
            offset_val = -6

        for x3 in range(offset_val, -1):
            if len(self.data0) <= abs(offset_val)*4:
                ret_val = ret_val + 1
            else:
                if self.data0.high[offset_val] >= self.data0.high[x3+offset_val]:
                    ret_val = ret_val + (abs(offset_val) + x3 )
                if self.data0.high[offset_val] >= self.data0.high[abs(x3)+ offset_val]:
                    ret_val = ret_val + abs(x3)
                print("detect_highest: ret_val=%s at date=%s, ori_date=%s" %(ret_val, self.data0.datetime.date(offset_val), cur_date))

        if ret_val >= abs(offset_val)*3:
            #print("detect_highest: ret_val=%s" %ret_val)
            return "highest" # return true to current -6 value from
        else:
            return None

class St(bt.Strategy):
    '''
    params = (('usepp1', False),
              ('plot_on_daily', False),
              ('x1', None),
              ('y1', None),
              ('x2', None),
              ('y2', None))
    '''
    def __init__(self):
        #if self.p.usepp1:
        #    self.pp = PivotPoint1(self.data1)
        #else:
        self.pp = PivotPoint2(self.data1)

        #if self.p.plot_on_daily:
        #    self.pp.plotinfo.plotmaster = self.data0

        pprint(vars(self.pp))
    '''
    def next(self):
        txt = ','.join(
            ['%04d' % len(self),
             '%04d' % len(self.data0),
             '%04d' % len(self.data1),
             #'%04d' % 3000,
             self.data.datetime.date(0).isoformat(),
             '%s' %self.datas[0].datetime.datetime(0),
             '%04d' % len(self.pp),
             '%.2f' % self.pp[0]],
             )
        print(txt)
    '''
if __name__ == '__main__':
    args = parse_args()

    cerebro = bt.Cerebro(stdstats=False)

    cerebro.addstrategy(St,
                        #usepp1=args.usepp1,
                        #plot_on_daily=args.plot_on_daily
                        )

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
