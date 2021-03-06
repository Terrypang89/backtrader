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
        self.p.x1 = time2date("2005-01-28")
        self.p.y1 = dataframe.loc[self.p.x1, "Close"]
        self.p.x1_begin = time2date("2005-01-28")
        x1_time_stamp = bt.date2num(self.p.x1)

        self.p.x2 = time2date("2006-05-31")
        self.p.x2_last = time2date("2006-05-31")
        self.p.y2 = dataframe.loc[self.p.x2, "Close"]
        x2_time_stamp = bt.date2num(self.p.x2)
        self.p.prev_time = '1'
        self.p.prev_type = '1'
        self.m = 1
        self.B = 0

    def next(self):
        date_ori = self.data0.datetime.datetime()
        date_timestamp = bt.date2num(date_ori)
        date_back = bt.num2date(date_timestamp).date()
        prev_type = self.p.prev_type
        prev_time = self.p.prev_time
        print("datetime = %s, timestamp = %d, prev_type = %s, prev_time = %s" %(date_ori,date_timestamp, prev_type, prev_time))
        if date_timestamp != "732041":
            self.p.prev_time, self.p.prev_type = self.detect_peak(date_ori, date_timestamp, -15, prev_time, prev_type, self.p.x1_begin, self.p.x2_last)
        self.lines.trend[0] = self.get_y(date_timestamp)

    def detect_peak(self, cur_date, cur_date_timestamp, offset_val, prev_predicted_time, prev_detected_type, min_datetime, max_datetime):
        debug = 1
        #if debug == 1:
            #print("cur_datetime = %s, cur_date_timestamp = %s, offset_val = %s, prev_predicted_time = %s, prev_detected_type = %s, min_datetime = %s, min_datetimestamp = %s, max_datetime = %s, max_datetimestamp = %s" %(cur_date, cur_date_timestamp, offset_val, prev_predicted_time, prev_detected_type, min_datetime, bt.date2num(min_datetime), max_datetime, bt.date2num(max_datetime)))

        if int(cur_date_timestamp) < bt.date2num(min_datetime) or int(cur_date_timestamp) > bt.date2num(max_datetime):
            return "-1", "-1"
        #else:
            #if prev_detected_type == "-1":
                #prev_detected_type == "-2"
                #print("prev_detect_type = 2 detected")

        if offset_val is None or not offset_val or offset_val == "":
            offset_val = -15

        #start assigning for high or low detection based on prev detected result
        detect_highpeak_true = 1
        detect_lowpeak_true = 1
        for x1 in range(offset_val, 0):
            if self.data0.datetime.date(abs(x1)) == max_datetime or self.data0.datetime.date(x1) == min_datetime:
                if detect_highpeak_true == 0:
                    detect_highpeak_true = 0
                elif detect_lowpeak_true == 0:
                    detect_lowpeak_true = 0
            else:
                if prev_detected_type == "high": #detected prev is high, must goes through the same the detect_highpeak_true detection for real next high peak detected
                    if data.high[0] < data.high[x1] or data.high[0] < data.high[abs(x1)]:
                        detect_highpeak_true = 0
                elif prev_detected_type == "low": #detected prev is low, must goes through the same the detect_lowpeak_true detection for real next low peak detected
                    if data.low[0] > data.low[x1] or data.low[0] > data.low[abs(x1)]:
                        detect_lowpeak_true = 0
                else:                              #if just starting, see which detection comes first
                    if data.high[0] < data.high[x1] or data.high[0] < data.high[abs(x1)]:
                        detect_highpeak_true = 0
                    if data.low[0] > data.low[x1] or data.low[0] > data.low[abs(x1)]:
                        detect_lowpeak_true = 0

        # get high to low line and high, low, high for
        if detect_highpeak_true == 1 and detect_lowpeak_true == 0:
            self.p.x1 = self.data0.datetime.date(0)
            self.p.y1 = data.high[0]
            x1_time_stamp = bt.date2num(self.p.x1)

            advance2high = 1
            loop2low_detect = 0
            loop2lowhigh_detect = 0

            # high is detected so start detect low.
            while loop2low_detect == 0:
                advance_detect_type = "low"
                for x2 in range(offset_val, 0):
                    """
                    if self.data0.datetime.date(advance2high+abs(x2)) == max_datetime:
                        end_high_detection = data.low[advance2high]
                        end_high_datetime = self.data0.datetime.date(advance2high)
                        for x4 in range(advance2high, advance2high+abs(x2)):
                            if end_high_detection < data.low[x4]:
                                end_high_detection = data.low[x4]
                                end_high_datetime = self.data0.datetime.date(x4)
                        self.p.x2 = end_high_datetime
                        self.p.y2 = end_high_detection
                        x2_time_stamp = bt.date2num(self.p.x2)
                        if debug == 1:
                            print("ist1 advance2high = %d, x2 = %d, abs(x2) = %d, data.date(%d) = %s == max_date = %s, end_high_detection = %d, end_high_datetime = %s, x2_time_stamp = %d" %(advance2high, x2, abs(x2), advance2high+abs(x2), self.data0.datetime.date(advance2high+abs(x2)), max_datetime, end_high_detection ,end_high_datetime, x2_time_stamp))
                        break
                    elif self.data0.datetime.date(advance2high+x2) == min_datetime:
                        begin_high_detection = data.low[advance2high]
                        begin_high_datetime = self.data0.datetime.date(advance2high)
                        for x5 in range(advance2high+x2, advance2high):
                            if begin_high_detection < data.low[x5]:
                                begin_high_detection = data.low[x5]
                                begin_high_datetime = self.data0.datetime.date(x5)
                        self.p.x2 = begin_high_datetime
                        self.p.y2 = begin_high_detection
                        x2_time_stamp = bt.date2num(self.p.x2)
                        if debug == 1:
                            print("1st2 advance2high = %d, data.date(%d) = %s == min_date = %s, end_low_detection = %d, end_low_datetime = %s, x2_time_stamp = %d " %(advance2high, advance2high+x2, self.data0.datetime.date(advance2high+x2), min_datetime, begin_high_detection ,begin_high_datetime, x2_time_stamp))
                        break
                    else:
                    """
                    #detecting low for line draw, high to low and make sure 15 left and right has no lower value
                    if data.low[advance2high] > data.low[advance2high+abs(x2)] or data.low[advance2high] > data.low[advance2high+x2]:
                        advance_detect_type = "0"
                #low detected then line draw from high to low
                if advance_detect_type == "low":
                    loop2low_detect = 1 #break the loop

                    self.p.x2 = self.data0.datetime.date(advance2high)
                    self.p.y2 = data.low[advance2high]
                    x2_time_stamp = bt.date2num(self.p.x2)
                    if debug == 1:
                        #print("1st3 low detected advance2high = %d, data.date(%d) = %s, x2 = %s, y2= %d, x2_time_stamp = %d " %(advance2high, advance2high+x2, self.data0.datetime.date(advance2high), self.p.x2 , self.p.y2, x2_time_stamp))
                        print("1st3 low detected    advance2high = %d, x1 = %s, y1= %d, x2 = %s, y2= %d, x2_time_stamp = %d " %(advance2high, self.p.x1, self.p.y1, self.p.x2 , self.p.y2, x2_time_stamp))
                advance2high = advance2high+1

            #start detecting Highs from high-midlow-Highs
            advance2high = 2
            while loop2lowhigh_detect == 0:
                advance_detect_type = "high"
                for x2 in range(offset_val, 0):
                    """
                    if self.data0.datetime.date(advance2high+abs(x2)) == max_datetime:
                        if advance_detect_type == "0": # didnt detected low so
                            end_highlow_detection = data.low[advance2high]
                            end_highlow_datetime = self.data0.datetime.date(advance2high)
                            for x6 in range(advance2high, advance2high+abs(x2)):
                                if end_highlow_detection < data.low[x6]:
                                    end_highlow_detection = data.low[x6]
                                    end_highlow_datetime = self.data0.datetime.date(x6)
                            self.p.x2 = end_highlow_datetime
                            self.p.y2 = end_highlow_detection
                            x2_time_stamp = bt.date2num(self.p.x2)
                            if debug == 1:
                                print("2nd1 advance2high = %d, x2 = %d, abs(x2) = %d, data.date(%d) = %s == max_date = %s, end_highlow_detection = %d, end_highlow_datetime = %s, x2_time_stamp = %d" %(advance2high, x2, abs(x2), advance2high+abs(x2), self.data0.datetime.date(advance2high+abs(x2)), max_datetime, end_highlow_detection ,end_highlow_datetime, x2_time_stamp))

                    elif self.data0.datetime.date(advance2high+x2) == min_datetime:
                        if advance_detect_type == "0": # didnt detected low
                            begin_highlow_detection = data.low[advance2high]
                            begin_highlow_datetime = self.data0.datetime.date(advance2high)
                            for x7 in range(advance2high+x2, advance2high):
                                if begin_highlow_detection < data.low[x7]:
                                    begin_highlow_detection = data.low[x7]
                                    begin_highlow_datetime = self.data0.datetime.date(x7)
                            self.p.x2 = begin_highlow_datetime
                            self.p.y2 = begin_highlow_detection
                            x2_time_stamp = bt.date2num(self.p.x2)
                            if debug == 1:
                                print("2nd2 advance2high = %d, data.date(%d) = %s == min_date = %s, begin_highlow_detection = %d, begin_highlow_datetime = %s, x2_time_stamp = %d " %(advance2high, advance2high+x2, self.data0.datetime.date(advance2high+x2), min_datetime, begin_highlow_detection ,begin_highlow_datetime, x2_time_stamp))
                    else:
                    """
                    #start detecting high - low - Highs, ensure Highs 15 left and right no higher value
                    if data.high[advance2high] < data.high[advance2high+abs(x2)] or data.high[advance2high] < data.high[advance2high+x2]:
                        advance_detect_type = "0"
                #Highs detected so break the loop
                if advance_detect_type == "high":
                    loop2lowhigh_detect = 1 #Highs detected break from loop
                    if debug == 1:
                        #print("2nd3 highhigh detected advance2high = %d, data.date(%d) = %s, data.date(%d) = %s, prev_detected_type = %s, self.p.x2 = %s, self.p.y2 = %d, x2_time_stamp = %d " %(advance2high, advance2high, self.data0.datetime.date(advance2high), advance2high+x2, self.data0.datetime.date(advance2high+x2), prev_detected_type, self.p.x2, self.p.y2, x2_time_stamp))
                        print("2nd3 highhigh detected   advance2high = %d, prev_detected_type = %s, self.p.x2 = %s, self.p.y2 = %d, x2_time_stamp = %d " %(advance2high, prev_detected_type, self.p.x2, self.p.y2, x2_time_stamp))
                advance2high = advance2high+1

            #check high-midlow-Highs, either Highs detected early or midlow detected early
            if advance_detect_type == "high":
                advance2high = advance2high-1
                middle_low_detection = data.low[0]
                middle_low_datetime = self.data0.datetime.date(0)

                #start capture the midlow from high-Highs
                for x3 in range(1, advance2high):
                    if data.low[x3] < middle_low_detection:
                        middle_low_detection = data.low[x3]
                        middle_low_datetime = self.data0.datetime.date(x3)
                prev_detected_type = "low"
                prev_predicted_time = self.data0.datetime.date(advance2high)

                #use timstamp to compare, high - Highs detected first or high - midlow detected first
                if bt.date2num(middle_low_datetime) < x2_time_stamp:
                    self.p.x2 = middle_low_datetime
                    self.p.y2 = middle_low_detection
                    x2_time_stamp = bt.date2num(self.p.x2)
                    if debug == 1:
                        #print("2nd3 highlowhigh, get low - detected advance2high = %d, data.date(%d) = %s, data.date(%d) = %s, prev_detected_type = %s, self.p.x2 = %s, self.p.y2 = %d, x2_time_stamp = %d " %(advance2high, advance2high+abs(x2), self.data0.datetime.date(advance2high+abs(x2)), advance2high+x2, self.data0.datetime.date(advance2high+x2), prev_detected_type, self.p.x2, self.p.y2, x2_time_stamp))
                        print("2nd3 highlowhigh, get low - detected     advance2high = %d, prev_detected_type = %s, x1 = %s, y1 = %d, x2 = %s, y2 = %d, x2_time_stamp = %d " %(advance2high, prev_detected_type, self.p.x1, self.p.y1, self.p.x2, self.p.y2, x2_time_stamp))

            #start the
            self.m = self.get_slope(x1_time_stamp, x2_time_stamp, self.p.y1, self.p.y2)
            self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
            print("")
            return prev_predicted_time, prev_detected_type

        elif detect_highpeak_true == 0 and detect_lowpeak_true == 1:
            advance2low = 1
            advance_detect_type = 0

            self.p.x1 = self.data0.datetime.date(0)
            self.p.y1 = data.low[0]
            x1_time_stamp = bt.date2num(self.p.x1)

            loop2high_detect = 0
            loop2highlow_detect = 0
            while loop2high_detect == 0:
                advance_detect_type = "high"
                for x2 in range(offset_val, 0):
                    """
                    if self.data0.datetime.date(advance2low+abs(x2)) == max_datetime:
                        end_low_detection = data.high[advance2low]
                        end_low_datetime = self.data0.datetime.date(advance2low)
                        for x4 in range(advance2low, advance2low+abs(x2)):
                            if end_low_detection < data.high[x4]:
                                end_low_detection = data.high[x4]
                                end_hlow_datetime = self.data0.datetime.date(x4)
                        self.p.x2 = end_low_datetime
                        self.p.y2 = end_low_detection
                        x2_time_stamp = bt.date2num(self.p.x2)
                        if debug == 1:
                            print("ist1 advance2low = %d, x2 = %d, abs(x2) = %d, data.date(%d) = %s == max_date = %s, end_low_detection = %d, end_low_datetime = %s, x2_time_stamp = %d" %(advance2low, x2, abs(x2), advance2low+abs(x2), self.data0.datetime.date(advance2low+abs(x2)), max_datetime, end_low_detection ,end_low_datetime, x2_time_stamp))
                        break
                    elif self.data0.datetime.date(advance2low+x2) == min_datetime:
                        begin_low_detection = data.high[advance2low]
                        begin_low_datetime = self.data0.datetime.date(advance2low)
                        for x5 in range(advance2low+x2, advance2low):
                            if begin_low_detection < data.high[x5]:
                                begin_low_detection = data.high[x5]
                                begin_low_datetime = self.data0.datetime.date(x5)
                        self.p.x2 = begin_low_datetime
                        self.p.y2 = begin_low_detection
                        x2_time_stamp = bt.date2num(self.p.x2)
                        if debug == 1:
                            print("1st2 advance2low = %d, data.date(%d) = %s == min_date = %s, begin_low_detection = %d, begin_low_datetime = %s, x2_time_stamp = %d " %(advance2low, advance2low+x2, self.data0.datetime.date(advance2low+x2), min_datetime, begin_low_detection ,begin_low_datetime, x2_time_stamp))
                        break
                    else:
                    """
                    if data.high[advance2low] < data.high[advance2low+abs(x2)] or data.high[advance2low] < data.high[advance2low+x2]:
                        advance_detect_type = "0"
                if advance_detect_type == "high":
                    loop2high_detect = 1
                    self.p.x2 = self.data0.datetime.date(advance2low)
                    self.p.y2 = data.high[advance2low]
                    x2_time_stamp = bt.date2num(self.p.x2)
                    if debug == 1:
                        #print("1st3 high detected advance2low = %d, data.date(%d) = %s, x2 = %s, y2= %d, x2_time_stamp = %d " %(advance2low, advance2low+x2, self.data0.datetime.date(advance2low), self.p.x2 , self.p.y2, x2_time_stamp))
                        print("1st3 high detected   advance2low = %d, x1 = %s, y1= %d, x2 = %s, y2= %d, x2_time_stamp = %d " %(advance2low, self.p.x1 , self.p.y1, self.p.x2 , self.p.y2, x2_time_stamp))
                advance2low = advance2low+1

            advance2low = 2

            while loop2highlow_detect == 0:
                advance_detect_type = "low"
                for x2 in range(offset_val, 0):
                    """
                    if self.data0.datetime.date(advance2low+abs(x2)) == max_datetime:
                        if advance_detect_type == "0": # didnt detected low
                            end_lowhigh_detection = data.high[advance2low]
                            end_lowhigh_datetime = self.data0.datetime.date(advance2low)
                            for x6 in range(advance2low, advance2low+abs(x2)):
                                if end_lowhigh_detection < data.high[x6]:
                                    end_lowhigh_detection = data.high[x6]
                                    end_lowhigh_datetime = self.data0.datetime.date(x6)
                            self.p.x2 = end_lowhigh_datetime
                            self.p.y2 = end_lowhigh_detection
                            x2_time_stamp = bt.date2num(self.p.x2)
                            if debug == 1:
                                print("2nd1 advance2low = %d, x2 = %d, abs(x2) = %d, data.date(%d) = %s == max_date = %s, end_lowhigh_detection = %d, end_highlowhigh_datetime = %s, x2_time_stamp = %d" %(advance2low, x2, abs(x2), advance2low+abs(x2), self.data0.datetime.date(advance2low+abs(x2)), max_datetime, end_lowhigh_detection ,end_lowhigh_datetime, x2_time_stamp))

                    elif self.data0.datetime.date(advance2low+x2) == min_datetime:
                        if advance_detect_type == "0": # didnt detected low
                            begin_lowhigh_detection = data.high[advance2low]
                            begin_lowhigh_datetime = self.data0.datetime.date(advance2low)
                            for x7 in range(advance2low+x2, advance2low):
                                if end_lowhigh_detection < data.high[x7]:
                                    begin_lowhigh_detection = data.high[x7]
                                    begin_lowhigh_datetime = self.data0.datetime.date(x7)
                            self.p.x2 = begin_lowhigh_datetime
                            self.p.y2 = begin_lowhigh_detection
                            x2_time_stamp = bt.date2num(self.p.x2)
                            if debug == 1:
                                print("2nd2 advance2low = %d, data.date(%d) = %s == min_date = %s, begin_lowhigh_detection = %d, begin_lowhigh_datetime = %s, x2_time_stamp = %d " %(advance2low, advance2low+x2, self.data0.datetime.date(advance2low+x2), min_datetime, begin_lowhigh_detection ,begin_lowhigh_datetime, x2_time_stamp))
                    else:
                    """
                    if data.high[advance2low] < data.high[advance2low+abs(x2)] or data.high[advance2low] < data.high[advance2low+x2]:# high, low, high detected
                        advance_detect_type = "0"
                if advance_detect_type == "low":
                    loop2highlow_detect = 1
                    if debug == 1:
                        #print("2nd3 lowlow detected advance2low = %d, data.date(%d) = %s, data.date(%d) = %s, prev_detected_type = %s, self.p.x2 = %s, self.p.y2 = %d, x2_time_stamp = %d " %(advance2low, advance2low, self.data0.datetime.date(advance2low), advance2low+x2, self.data0.datetime.date(advance2low+x2), prev_detected_type, self.p.x2, self.p.y2, x2_time_stamp))
                        print("2nd3 lowlow detected     advance2low = %d, prev_detected_type = %s, self.p.x2 = %s, self.p.y2 = %d, x2_time_stamp = %d " %(advance2low, prev_detected_type, self.p.x2, self.p.y2, x2_time_stamp))

                advance2low = advance2low+1

            if advance_detect_type == "low":
                advance2low = advance2low-1
                middle_high_detection = data.high[0]
                middle_high_datetime = self.data0.datetime.date(0)
                for x3 in range(0, advance2low):
                    if data.high[x3] > middle_high_detection:
                        middle_high_detection = data.high[x3]
                        middle_high_datetime = self.data0.datetime.date(x3)
                prev_detected_type = "high"
                prev_predicted_time = self.data0.datetime.date(advance2low)

                if bt.date2num(middle_high_datetime) < x2_time_stamp:
                    self.p.x2 = middle_high_datetime
                    self.p.y2 = middle_high_detection
                    x2_time_stamp = bt.date2num(self.p.x2)
                    if debug == 1:
                        #print("2nd3 lowhighlow, get high - detected advance2low = %d, data.date(%d) = %s, data.date(%d) = %s, prev_detected_type = %s, self.p.x2 = %s, self.p.y2 = %d, x2_time_stamp = %d " %(advance2low, advance2low+abs(x2), self.data0.datetime.date(advance2low+abs(x2)), advance2low+x2, self.data0.datetime.date(advance2low+x2), prev_detected_type, self.p.x2, self.p.y2, x2_time_stamp))
                        print("2nd3 lowhighlow, get high - detected     advance2low = %d, prev_detected_type = %s, x1 = %s, y1 = %d, x2 = %s, y2 = %d, x2_time_stamp = %d " %(advance2low, prev_detected_type, self.p.x1, self.p.y1, self.p.x2, self.p.y2, x2_time_stamp))
            self.m = self.get_slope(x1_time_stamp, x2_time_stamp, self.p.y1, self.p.y2)
            self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
            print("")
            return prev_predicted_time, prev_detected_type
            #return "-4", "-4"
        return prev_predicted_time, prev_detected_type

    def get_slope(self, x1,x2,y1,y2):
        m = (y2-y1)/(x2-x1)
        return m

    def get_y_intercept(self, m, x1, y1):
        c=y1-m*x1
        return c

    def get_y(self,ts):
        Y = self.m * ts + self.B
        return Y

    def get_body_size(opendata, closedata):
        if opendata > closedata:
            return opendata - closedata
        else:
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
              ('x2_last', None),
              ('prev_time', None),
              ('prev_type', None),)

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
        #print(txt)

if __name__ == '__main__':
    args = parse_args()

    cerebro = bt.Cerebro(stdstats=False)

    datapath = "../../datas/2005-2006-day-001.txt"
    print("datapath =%s" %datapath)
    header = ['Date','Open','High','Low','Close','Volume','OpenInterest']
    skiprows = 0
    header = 0
    dataframe = pd.read_csv(datapath,
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
