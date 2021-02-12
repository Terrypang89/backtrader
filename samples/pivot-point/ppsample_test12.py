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
    offset_value = -6
    def __init__(self):
        self.p.x1 = time2date("2005-01-28")
        self.p.y1 = dataframe.loc[self.p.x1, "Close"]
        x1_time_stamp = bt.date2num(self.p.x1)

        self.p.x2 = time2date("2006-05-31")
        self.p.y2 = dataframe.loc[self.p.x2, "Close"]
        x2_time_stamp = bt.date2num(self.p.x2)

        self.m = self.get_slope(x1_time_stamp, x2_time_stamp, self.p.y1, self.p.y2)
        self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
        self.PREV_Y = self.get_y(x2_time_stamp)
        self.PREV_Y_state = "highest"
        self.PREV_X = x2_time_stamp

    def next(self):
        date_ori = self.data0.datetime.datetime()
        date_timestamp = bt.date2num(date_ori)
        date_back = bt.num2date(date_timestamp).date()
        self.lines.trend[0] = self.data0.low[0]

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
        self.lines.trend[0] = self.data0.low[0]

    def get_offset_val(self, offset_val):
        if offset_val or offset_val < 0:
            return self.data0.datetime.date(offset_val)
        else:
            return None

    def get_x_time(self, y_val, index_type):
        return dataframe[dataframe[index_type]==y_val].index.item()

    def get_slope(self, x1,x2,y1,y2):
        m = (y2-y1)/(x2-x1)
        return m

    def get_y_intercept(self, m, x1, y1):
        c=y1-m*x1
        return c

    def get_y(self,ts):
        Y = self.m * ts + self.B
        return Y

    def detect_prev_lowest(self, cur_date_timestamp, offset_val, lowest_time):
        ret_val = 0
        if offset_val is None or not offset_val or offset_val == "":
            offset_val = -6

        #check Data.high[0] > data.high[-1] and Data.high[0] > data.high[1] and data.high[0] > data.high[2]
        if data.high[0] > data.high[-1] and data.high[0] > data.high[1]:
            rollback2high = 0
            advance2high = 0
            largest_body = 0
            #look for previous highest
            while True:
                #ensure now lowest, must compare prev highest, so search highest
                if data.open[rollback2high] > data.open[rollback2high-1] and data.open[rollback2high] > data.open[rollback2high + 1]:
                    largest_prevhighbody = rollback2high
                    self.largest_prevhighbody_date = date.high[rollback2low].datetime
                    #compare with prev_largest_body through date, it is same?
                    prev_high_area = get_area(data.high[rollback2high].datetime, cur_dafe_timestamp, data.open[0], data.close[rollback2high])

                    #get the 2nd prev_high
                    break
                else:
                    rollback2high = rollback2high-1

            advance_low_area_detected = 1
            advance_high_area_detected = 0
            advance_high_area = 0
            larger_body_area = 0

            prev_low_close = []
            prev_low_time = []
            prev_high_time = []
            prev_high_open = []
            detected_advance_high_area = []

            while True:
                if data.high[advance2high] > data.high[advance2high-1]  data.high[advance2high] > data.high[advance2high-2] and data.high[advance2high] > data.high[advance2high-3]and advance_large_high_body_detected == 1_and data.open[advance2high] > data.open[advance2high+1] and data.high[advance2high+1] > data.high[advance2high+2] and data.high[advance2high+2] > data.high[advance2high+3]:
                    #largest_advancehighbody = advance2high
                    #self.largest_advancehighbody_date = date.high[advance2high].datetime
                    advance_high_area = get_area(prev_low_time(len(prev_low_time)-1), data.high[advance2high].datetime, prev_low_close[len(prev_low_close)-1], data.high[advance2high]))
                    # we unsure this is the area we want so must compare with future area by getting the lowest again
                    prev_high_open.append(data.open[advance2high])
                    prev_high_time.append(data.open[advance2high].datetime())
                    detected_advance_low_area = 0
                else if data.low[advance2high] > data.low[advance2high-1] and data.low[advance2high] > data.low[advance2high-2] and data.low[advance2high] > data.low[advance2high-3] and advance_large_high_body_detected == 1_and data.close[advance2high] < data.close[advance2high+1] and data.close[advance2high+1] < data.close[advance2high+2] and data.close[advance2high+2] < data.close[advance2high+3]:
                    advance_large_high_body_detected = 0
                    advance_low_area.append(get_area(prev_high_time[len(prev_high_time)-1], data.low[advance2high].datetime, prev_high_open[len(prev_high_open)-1], data.close[advance2high]))
                    prev_low_close.append(data.close[advance2high])
                    prev_low_time.append(data.close[advance2high].datetime())
                    detected_advance_low_area = 1
                else
                    if get_body_size(advance2high)/largest_body_future > 2:
                        advance_large_high_body_detected = 1
                    if get_body_size(data.high[advance2high], data.low[advance2high]) > largest_body_future and data.open[advance2high] > data.open[advance2high - 1]:
                        largest_body_future = get_body_size(data.high[advance2high], data.low[advance2high])
                    advance2high = advance2high+1


            total_low_area = prev_high_area + advance_high_area
            #same the date or mart as point for
        else:
            return None

    def get_body_size(opendata, closedata):
        if opendata > closedata:
            return opendata - closedata
        else
            return None

    def get_area(t1, t2, data2, data1):
        if t2 > t1:
            area = ((t2 - t1) * abs((data2 - data1)))/2
            return area
        else:
            return None


class St(bt.Strategy):

    params = (('usepp1', False),
              ('plot_on_daily', False),
              ('x1', None),
              ('y1', None),
              ('x2', None),
              ('y2', None))

    def __init__(self):
        self.pp = PivotPoint2(self.data0)

        if self.p.plot_on_daily:
            self.pp.plotinfo.plotmaster = self.data0

    def next(self):
        txt = ','.join(
            ['%04d' % len(self),
             '%04d' % len(self.data0),
             self.data.datetime.date(0).isoformat(),
             '%04d' % len(self.pp),
             '%.2f' % self.pp[0],
             'St current time =%s' %self.datas[0].datetime.date()]
             )
        print(txt)

if __name__ == '__main__':
    args = parse_args()

    cerebro = bt.Cerebro(stdstats=False)

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
    print('---------------s-----------------------------------')
    print(dataframe)
    print('--------------------------------------------------')

    data = bt.feeds.PandasData(dataname=dataframe)

    cerebro.adddata(data)
    cerebro.addstrategy(St)
    cerebro.run(runonce=False)
    if args.plot:
        cerebro.plot(style='bar')
