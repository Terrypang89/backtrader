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
    prev_detected_type = 0
    prev_prediction_time = 0
    def __init__(self):
        self.p.x1 = time2date("2005-01-28")
        self.p.y1 = dataframe.loc[self.p.x1, "Close"]
        self.p.x1_begin = time2date("2005-01-28")
        x1_time_stamp = bt.date2num(self.p.x1)

        self.p.x2 = time2date("2006-05-31")
        self.p.x2_last = time2date("2006-05-31")
        self.p.y2 = dataframe.loc[self.p.x2, "Close"]
        x2_time_stamp = bt.date2num(self.p.x2)

        # initialize the self.m and self.B before the peak is detected
        self.m = 1
        self.B = 0

    def next(self):
        date_ori = self.data0.datetime.datetime()
        date_timestamp = bt.date2num(date_ori)
        date_back = bt.num2date(date_timestamp).date()

        prev_prediction_time, prev_detected_type,  = detect_peak(data_timestamp, -15, prev_detected_type, prev_prediction_time, self.p.x2_last)
        # plotting with defined self.B and self.m  in detect_peak function
        self.lines.trend[0] = self.get_y(date_timestamp)

    def get_slope(self, x1,x2,y1,y2):
        m = (y2-y1)/(x2-x1)
        return m

    def get_y_intercept(self, m, x1, y1):
        c=y1-m*x1
        return c

    def get_y(self,ts):
        Y = self.m * ts + self.B
        return Y

    def detect_peak(self, cur_date_timestamp, offset_val, prev_prediction_time, prev_detected_type, min_datetime, max_datetime):
        ret_val = 0

        if offset_val is None or not offset_val or offset_val == "":
            offset_val = -15
        detect_highpeak_true = 1
        detect_lowpeak_true = 1

        #to check if current peak is less than others, if yes then detect 0
        for x1 in range(-1, offset_val):
            #to detect the current high is the peak high and prevent maximan of datetime
            if data.high[abs(x1)].datetime() == max_datetime || data.high[abs(x1)].datetime() == min_datetime:
                if detect_highpeak_true == 0:
                    detect_highpeak_true = 0
                else if detect_lowpeak_true == 0:
                    detect_lowpeak_true = 0
            else:
                if data.high[0] < data.high[x1] || data.high[0] < data.high[abs(x1)]:
                    detect_highpeak_true = 0
                if data.low[0] > data.low[x1] || data.low[0] > data.low[abs(x1)]:
                    detect_lowpeak_true = 0

        #highest peak detected
        if detect_highpeak_true == 1 and detect_lowpeak_true == 0:
            #start drawing x1, y1
            self.p.x1 = data.high[0].datetime()
            self.p.y1 = dataframe.loc[self.p.x1, "High"]
            x1_time_stamp = bt.date2num(self.p.x1)

            advance2high = 1
            advance_detect_type = 0

            while True:
                for x2 in range(-1, offset_val):
                    #if data.low[advance2high].datetime() == max_datetime || data.low[advance2high].datetime() == min_datetime:
                    #    break
                    #else:
                    #detected max_datetime in the middle of next lower detection, so just get the lowest in between:
                    if data.low[advance2high+abs(x2)].datetime() == max_datetime:
                        end_low_detection = data.low[advance2high]
                        end_low_datetime = data.low[advance2high].datetime()
                        for x4 in range(advance2high, advance2high+abs(x2)):
                            if end_low_detection < data.low[x4]:
                                end_low_detection = data.low[x4]
                                end_low_datetime = data.low[x4].datetime()
                        self.p.x2 = end_low_detection
                        self.p.y2 = end_low_datetime
                        x2_time_stamp = bt.date2num(self.p.x2)
                        break
                    else if data.low[advance2high+x2].datetime() == min_datetime:
                        begin_low_detection = data.low[advance2high]
                        begin_low_datetime = data.low[advance2high].datetime()
                        for x5 in range(advance2high, advance2high+x2):
                            if begin_low_detection < data.low[x5]:
                                begin_low_detection = data.low[x5]
                                begin_low_datetime = data.low[x5].datetime()
                        self.p.x2 = begin_low_detection
                        self.p.y2 = begin_low_datetime
                        x2_time_stamp = bt.date2num(self.p.x2)
                        break
                    # to detect next lowest peak
                    else if data.low[advance2high] < data.low[advance2high+abs(x2)] and data.low[advance2high] < data.low[advance2high+x2]:
                        advance_detect_type = "low"
                        prev_detected_type = "low"
                        prev_prediction_time = data.low[x2].datetime()

                        # start drawing x2, y2
                        self.p.x2 = data.low[advance2high].datetime()
                        self.p.y2 = dataframe.loc[self.p.x2, "Low"]
                        x2_time_stamp = bt.date2num(self.p.x2)
                        break

                    if data.high[advance2high+abs(x2)].datetime() == max_datetime:
                        if advance_detect_type == 0: # didnt detected low so
                            end_highlow_detection = data.low[advance2high]
                            end_highlow_datetime = data.low[advance2high].datetime()
                            for x6 in range(advance2high, advance2high+abs(x2)):
                                if end_highlow_detection < data.low[x6]:
                                    end_highlow_detection = data.low[x6]
                                    end_highlow_datetime = data.low[x6].datetime()
                            self.p.x2 = end_highlow_detection
                            self.p.y2 = end_highlow_datetime
                            x2_time_stamp = bt.date2num(self.p.x2)
                            break
                    else if data.high[advance2high+x2].datetime() == min_datetime:
                        if advance_detect_type == 0: # didnt detected low
                            begin_highlow_detection = data.low[advance2high]
                            begin_highlow_datetime = data.low[advance2high].datetime()
                            for x7 in range(advance2high, advance2high+x2):
                                if begin_highlow_detection < data.low[x7]:
                                    begin_highlow_detection = data.low[x7]
                                    begin_highlow_datetime = data.low[x7].datetime()
                            self.p.x2 = begin_highlow_detection
                            self.p.y2 = begin_highlow_datetime
                            x2_time_stamp = bt.date2num(self.p.x2)
                            break
                    else if data.high[advance2high] > data.high[advance2high+abs(x2)] and data.high[advance2high] > data.high[advance2high+x2]:
                        #if detect highest first not the lowest, as detection must be currect high, then low, then high
                        if advance_detect_type == 0:
                            middle_low_detection = data.low[0]
                            middle_low_datetime = data.low[0].datetime()
                            # get the lowest low compared in between current high and detected next high
                            for x3 in range(0, advance2high):
                                if data.low[x3] < middle_low_detection:
                                    middle_low_detection = data.low[x3]
                                    middle_low_datetime = data.low[x3].datetime()
                                prev_detected_type = "low"
                                prev_prediction_time = data.low[x3].datetime()
                                # start drawing x2, y2
                                self.p.x2 = data.low[x3].datetime()
                                self.p.y2 = dataframe.loc[self.p.x2, "Low"]
                                x2_time_stamp = bt.date2num(self.p.x2)
                        else:
                            #got detected prev is low so this high is acceptable
                            advance_detect_type = "high"
                            break
                #loop for until low and high detected
                advance2high = advance2high+1

            # change plotting gradient m and y_intercept B
            self.m = self.get_slope(x1_time_stamp, x2_time_stamp, self.p.y1, self.p.y2)
            self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)

            return prev_prediction_time, prev_detected_type

        else if detect_highpeak_true == 0 and detect_lowpeak_true == 1: #detected high peak
            advance2low = 1
            advance_detect_type = 0

            #start drawing x1, y1
            self.p.x1 = data.low[0].datetime()
            self.p.y1 = dataframe.loc[self.p.x1, "Low"]
            x1_time_stamp = bt.date2num(self.p.x1)

            while True:
                for x2 in range(1, offset_val):
                    if data.high[advance2low+abs(x2)].datetime() == max_datetime:
                        end_high_detection = data.high[advance2low]
                        end_high_datetime = data.high[advance2low].datetime()
                        for x4 in range(advance2low, advance2low+abs(x2)):
                            if end_high_detection > data.high[x4]:
                                end_high_detection = data.high[x4]
                                end_high_datetime = data.high[x4].datetime()
                        self.p.x2 = end_high_detection
                        self.p.y2 = end_high_datetime
                        x2_time_stamp = bt.date2num(self.p.x2)
                        break
                    else if data.high[advance2high+x2].datetime() == min_datetime:
                        begin_high_detection = data.high[advance2low]
                        begin_high_datetime = data.high[advance2low].datetime()
                        for x5 in range(advance2low, advance2low+x2):
                            if begin_high_detection > data.high[x5]:
                                begin_high_detection = data.high[x5]
                                begin_high_datetime = data.high[x5].datetime()
                        self.p.x2 = begin_high_detection
                        self.p.y2 = begin_high_datetime
                        x2_time_stamp = bt.date2num(self.p.x2)
                        break
                    # to detect next lowest
                    if data.high[advance2low] > data.high[advance2low+abs(x2)] and data.high[advance2low] > data.high[advance2low+x2]:
                        advance_detect_type = "high"
                        prev_detected_type = "high"
                        prev_prediction_time = data.low[x2].datetime()
                    if data.low[advance2low] < data.low[advance2low+abs(x2)] and data.low[advance2low] < data.low[advance2low+x2]:
                        if advance_detect_type == 0:
                            middle_high_detection = data.high[0]
                            middle_high_datetime = data.high[0].datetime
                            for x3 in range(0, advance2low):
                                if data.high[x3] < middle_high_detection:
                                    middle_high_detection = data.high[x3]
                                    middle_high_datetime = data.high[x3].datetime()
                                prev_detected_type = "high"
                                prev_prediction_time = data.low[x3].datetime()
                        else:
                            advance_detect_type = "low"
                            break
                advance2low = advance2low+1

            # change plotting gradient m and y_intercept B
            self.m = self.get_slope(x1_time_stamp, x2_time_stamp, self.p.y1, self.p.y2)
            self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
            return prev_prediction_time, prev_detected_type

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
              ('x1_begin', None),
              ('x2', None),
              ('y2', None),
              ('x2_last', None))

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
