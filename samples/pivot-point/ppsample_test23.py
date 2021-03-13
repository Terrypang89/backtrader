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
        self.p.y2 = bt.date2num(self.p.x2)
        self.p.prev_value = []
        self.p.prev_time = []
        self.p.prev_type = []
        self.m = 1
        self.B = 0

    def next(self):
        date_ori = self.data0.datetime.datetime()
        date_timestamp = bt.date2num(date_ori)
        date_back = bt.num2date(date_timestamp).date()
        print("datetime = %s, timestamp = %d" %(date_ori,date_timestamp))
        print("prev_type[%d]: %s" %(len(self.p.prev_type), self.p.prev_type))
        print("prev_time[%d]: %s" %(len(self.p.prev_time), self.p.prev_time))
        print("")
        self.p.prev_value, self.p.prev_time, self.p.prev_type = self.detect_peak(date_ori, date_timestamp, -15, self.p.prev_value, self.p.prev_time, self.p.prev_type, self.p.x1_begin, self.p.x2_last)
        self.lines.trend[0] = self.get_y(date_timestamp)

    def detect_peak(self, cur_date, cur_date_timestamp, offset_val, prev_predicted_value, prev_predicted_time, prev_detected_type, min_datetime, max_datetime):
        debug = 1

        advance_detect_type = 0
        #break from loop if detected not in region
        if int(cur_date_timestamp) < bt.date2num(min_datetime) or int(cur_date_timestamp) > bt.date2num(max_datetime):
            prev_detected_type.append("-1")
            return prev_predicted_value, prev_predicted_time, prev_detected_type

        if offset_val is None or not offset_val or offset_val == "":
            offset_val = -15

        if len(prev_detected_type) > 2:
            #check prev_detected_type[-2] = midlow, prev_detected_type[-1] = low
            if prev_detected_type[len(prev_detected_type)-2] == "midlow" and prev_detected_type[len(prev_detected_type)-1] == "low":
                prev_date_timestamp = bt.date2num(self.data0.datetime.date(0))
                print("prev_detected_type[-2] = midlow, prev_detected_type[-1] = low, prev_date_timestamp = %d, prev_date_time = %s" %(prev_date_timestamp, self.data0.datetime.date(-1)))
                #cur_date < high_midlow_datetime, cur_date < high_midlow_Highs_datetime
                if prev_date_timestamp < prev_predicted_time[len(prev_predicted_time)-2] and prev_date_timestamp < prev_predicted_time[len(prev_predicted_time)-1]:
                    #cur_date remain in high_midlow region
                    return prev_predicted_value, prev_predicted_time, prev_detected_type
                #cur_date == high_midlow_datetime, cur_date < high_midlow_Highs_datetime
                elif prev_date_timestamp == prev_predicted_time[len(prev_predicted_time)-2] and prev_date_timestamp < prev_predicted_time[len(prev_predicted_time)-1]:
                    self.p.x1 = prev_predicted_time[len(prev_predicted_time)-2]
                    self.p.y1 = prev_predicted_value[len(prev_predicted_value)-2]
                    self.p.x2 = prev_predicted_time[len(prev_predicted_time)-1]
                    self.p.y2 = prev_predicted_value[len(prev_predicted_value)-1]
                    self.m = self.get_slope(self.p.x1, self.p.x2, self.p.y1, self.p.y2)
                    self.B = self.get_y_intercept(self.m, self.p.x1, self.p.y1)
                    return prev_predicted_value, prev_predicted_time, prev_detected_type
                #cur_date > high_midlow_datetime, cur_date < high_midlow_Highs_datetime
                elif prev_date_timestamp > prev_predicted_time[len(prev_predicted_time)-2] and prev_date_timestamp < prev_predicted_time[len(prev_predicted_time)-1]:
                    #cur_date in high_midlow_Highs region
                    return prev_predicted_value, prev_predicted_time, prev_detected_type
            #check prev_detected_type[-2] = midhigh, prev_detected_type[-1] = high,
            elif prev_detected_type[len(prev_detected_type)-2] == "midhigh" and prev_detected_type[len(prev_detected_type)-1] == "high":
                prev_date_timestamp = bt.date2num(self.data0.datetime.date(0))
                print("prev_detected_type[-2] = midhigh, prev_detected_type[-1] = high, prev_date_timestamp = %d, prev_date_time = %s" %(prev_date_timestamp, self.data0.datetime.date(-1)))
                #cur_date < low_midhigh_datetime, cur_date < low_midhigh_Lows_datetime
                if prev_date_timestamp < prev_predicted_time[len(prev_predicted_time)-2] and prev_date_timestamp < prev_predicted_time[len(prev_predicted_time)-1]:
                    return prev_predicted_value, prev_predicted_time, prev_detected_type
                #cur_date == low_midhigh_datetime, cur_date < low_midhigh_Lows_datetime
                elif prev_predicted_time[len(prev_predicted_time)-2] == prev_date_timestamp and prev_date_timestamp < prev_predicted_time[len(prev_predicted_time)-1]:
                    self.p.x1 = prev_predicted_time[len(prev_predicted_time)-2]
                    self.p.y1 = prev_predicted_value[len(prev_predicted_value)-2]
                    self.p.x2 = prev_predicted_time[len(prev_predicted_time)-1]
                    self.p.y2 = prev_predicted_value[len(prev_predicted_value)-1]
                    self.m = self.get_slope(self.p.x1, self.p.y2, self.p.y1, self.p.y2)
                    self.B = self.get_y_intercept(self.m, self.p.x1, self.p.y1)
                    return prev_predicted_value, prev_predicted_time, prev_detected_type
                #cur_date > low_midhigh_datetime, cur_date < low_midhigh_Lows_datetime
                elif prev_date_timestamp > prev_predicted_time[len(prev_predicted_time)-2] and prev_date_timestamp < prev_predicted_time[len(prev_predicted_time)-1]:
                    return prev_predicted_value, prev_predicted_time, prev_detected_type

        detect_highpeak_true = 1
        detect_lowpeak_true = 1
        for x1 in range(offset_val, 0):
            if self.data0.datetime.date(abs(x1)) == max_datetime or self.data0.datetime.date(x1) == min_datetime:
                    detect_highpeak_true = 0
                    detect_lowpeak_true = 0
            else:
                if data.high[0] < data.high[x1] or data.high[0] < data.high[abs(x1)]:
                    detect_highpeak_true = 0
                if data.low[0] > data.low[x1] or data.low[0] > data.low[abs(x1)]:
                    detect_lowpeak_true = 0

        #start assigning for high or low detection based on prev detected type
        if detect_highpeak_true == 1 and detect_lowpeak_true == 0:
            #if prev_detected_type[len(prev_detected_type)-1] == "high":
            if prev_detected_type[len(prev_detected_type)-1] == "low": #or prev_predicted_time[len(prev_predicted_time)-1] == bt.date2num(self.data0.datetime.date(-1)):
                detect_highpeak_true = 1
                detect_lowpeak_true = 0
            elif prev_detected_type[len(prev_detected_type)-1] == "-1":
                detect_highpeak_true = 1
                detect_lowpeak_true = 0
            else:
                prev_detected_type.append("-1")
                #prev_predicted_time.append("-1")
                return prev_predicted_value, prev_predicted_time, prev_detected_type
        elif detect_highpeak_true == 0 and detect_lowpeak_true == 1:
            #if prev_detected_type[len(prev_detected_type)-1] == "low":
            if prev_detected_type[len(prev_detected_type)-1] == "high": #or prev_predicted_time[len(prev_predicted_time)-1] == bt.date2num(self.data0.datetime.date(-1)):
                detect_highpeak_true = 0
                detect_lowpeak_true = 1
            elif prev_detected_type[len(prev_detected_type)-1] == "-1":
                detect_highpeak_true = 0
                detect_lowpeak_true = 1
            else:
                prev_detected_type.append("-1")
                return prev_predicted_value, prev_predicted_time, prev_detected_type

        # get high to midlow line and high, midlow, Highs for
        if detect_highpeak_true == 1 and detect_lowpeak_true == 0:
            self.p.x1 = self.data0.datetime.date(0)
            self.p.y1 = data.high[0]
            print("detect_highpeak_true x1 = %s, y1=%d, x1_datetime = %s " %(self.p.x1, self.p.y1, self.data0.datetime.date(0)))
            self.p.x1 = bt.date2num(self.p.x1)
            x1_datetime = self.data0.datetime.date(0)

            advance2high = 1
            loop2low_detect = 0
            loop2lowhigh_detect = 0

            # high is detected so start detect midlow.
            while loop2low_detect == 0:
                advance_detect_type = "low"
                for x2 in range(offset_val, 0):
                    #detecting low for line draw, high to midlow and make sure midlow 15 left and right has no lower value
                    if data.low[advance2high] > data.low[advance2high+abs(x2)] or data.low[advance2high] > data.low[advance2high+x2]:
                        advance_detect_type = "0"
                #midlow detected then line draw from high to midlow
                if advance_detect_type == "low":
                    loop2low_detect = 1 #break the loop
                    midlow_value = data.low[advance2high]
                    midlow_datetime = bt.date2num(self.data0.datetime.date(advance2high))
                    midlow_date = self.data0.datetime.date(advance2high)
                    x2_datetime = self.data0.datetime.date(advance2high)
                    if debug == 1:
                        print("1st3 midlow detected    advance2high = %d, x1 = %s, y1= %d, midlow_datetime = %d, midlow_date = %s"
                        %(advance2high, self.p.x1, self.p.y1, midlow_datetime, midlow_date))
                advance2high = advance2high+1

            #start detecting Highs from high-midlow-Highs
            advance2high = 2
            while loop2lowhigh_detect == 0:
                advance_detect_type = "high"
                for x2 in range(offset_val, 0):
                    #start detecting high - midlow - Highs, ensure Highs 15 left and right no higher value
                    if data.high[advance2high] < data.high[advance2high+abs(x2)] or data.high[advance2high] < data.high[advance2high+x2]:
                        advance_detect_type = "0"
                #Highs detected so break the loop
                if advance_detect_type == "high":
                    loop2lowhigh_detect = 1 #Highs detected break from loop
                    end_Highs_value = data.high[advance2high]
                    end_Highs_datetime = bt.date2num(self.data0.datetime.date(advance2high))
                    end_Highs_date = self.data0.datetime.date(advance2high)
                    #x2_datetime = self.data0.datetime.date(advance2high)
                    if debug == 1:
                        print("2nd3 high-Highs detected   advance2high = %d, x1 = %s, y1= %d, end_Highs_datetime = %d, end_Highs_date = %s"
                        %(advance2high, self.p.x1, self.p.y1, end_Highs_datetime, end_Highs_date))
                advance2high = advance2high+1

            #check high-midlow-Highs, either Highs detected early or midlow detected early
            if advance_detect_type == "high":
                advance2high = advance2high-1

                #use timstamp to compare, low - Lows detected first or low - midhigh detected first
                if end_Highs_datetime < midlow_datetime:
                    #low - Lows detected earlier, so get midhigh from low - Lows
                    midlow_Highs_value = data.low[0]
                    midlow_Highs_datetime = bt.date2num(self.data0.datetime.date(0))

                    #start capture the midhigh from low-Lows
                    for x3 in range(1, advance2high):
                        if data.low[x3] < midlow_Highs_value:
                            midlow_Highs_value = data.low[x3]
                            midlow_Highs_datetime = bt.date2num(self.data0.datetime.date(x3))
                            midlow_Highs_date = self.data0.datetime.date(x3)
                            x2_datetime = self.data0.datetime.date(x3)

                    # due to the Lows detected first, and midhigh get in between low - Lows
                    self.p.x2 = midlow_Highs_datetime
                    self.p.y2 = midlow_Highs_value
                    #self.p.y2 = self.p.x2

                    #line high-midlow-Highs, to let midlow capture first
                    prev_detected_type.append("midlow")
                    prev_predicted_value.append(midlow_Highs_value)
                    prev_predicted_time.append(midlow_Highs_datetime)

                    #line high-midlow-Highs, to let Highs capture but must named it as low as it is from low to high
                    prev_detected_type.append("low")
                    prev_predicted_value.append(end_Highs_value)
                    prev_predicted_time.append(end_Highs_datetime)

                    if debug == 1:
                        print("2nd3 high-midlow-Highs, Highs detect earlier than midlow   advance2high = %d, prev_detected_type = %s, x2 = %s, y2 = %d, x2_datetime = %s, midlow_Highs_datetime = %d, midlow_Highs_date = %s, end_Highs_datetime = %d, end_Highs_date = %s "
                        %(advance2high, prev_detected_type[len(prev_detected_type)-1], self.p.x2, self.p.y2, x2_datetime, midlow_Highs_datetime, midlow_Highs_date, end_Highs_datetime, end_Highs_date ))
                else:
                    #midlow detected earlier so start setting
                    self.p.x2 = midlow_datetime
                    self.p.y2 = midlow_value
                    #self.p.y2 = self.p.x2

                    #line high-midlow, to let midlow capture only
                    prev_detected_type.append("high")
                    prev_predicted_value.append(midlow_value)
                    prev_predicted_time.append(midlow_datetime)
                    if debug == 1:
                        print("2nd4 high-midlow-Highs, midlows detect earlier than Highs advance2high = %d, prev_detected_type = %s,  x2 = %s, y2 = %d, x1_datetime = %s, x2_datetime = %s, midlow_datetime = %d, midlow_date = %s "
                        %(advance2high, prev_detected_type[len(prev_detected_type)-1],  self.p.x2, self.p.y2, x1_datetime, x2_datetime, midlow_datetime, midlow_date ))

            #start the
            self.m = self.get_slope(self.p.x1, self.p.x2, self.p.y1, self.p.y2)
            self.B = self.get_y_intercept(self.m, self.p.x1, self.p.y1)
            print("")
            return prev_predicted_value, prev_predicted_time, prev_detected_type

        elif detect_highpeak_true == 0 and detect_lowpeak_true == 1:
            advance_detect_type = 0

            self.p.x1 = self.data0.datetime.date(0)
            self.p.y1 = data.low[0]
            print("detect_lowpeak_true x1 = %s, y1=%d, x1_datetime = %s " %(self.p.x1, self.p.y1, self.data0.datetime.date(0)))
            self.p.x1 = bt.date2num(self.p.x1)
            x1_datetime = self.data0.datetime.date(0)
            #x1_time_stamp = bt.date2num(self.p.x1)

            advance2low = 1
            loop2high_detect = 0
            loop2highlow_detect = 0

            # get low to midhigh line and low, midhigh, Lows for
            while loop2high_detect == 0:
                advance_detect_type = "high"
                for x2 in range(offset_val, 0):
                    #start detecting low - midhigh - Lows, ensure Lows 15 left and right no lower value
                    if data.high[advance2low] < data.high[advance2low+abs(x2)] or data.high[advance2low] < data.high[advance2low+x2]:
                        advance_detect_type = "0"
                if advance_detect_type == "high":
                    loop2high_detect = 1
                    midhigh_value = data.high[advance2low]
                    midhigh_datetime = bt.date2num(self.data0.datetime.date(advance2low))
                    midhigh_date = self.data0.datetime.date(advance2low)
                    x2_datetime = self.data0.datetime.date(advance2low)
                    if debug == 1:
                        print("1st3 midhigh detected   advance2low = %d, x2 = %s, y2= %d, midhigh_datetime = %d, midhigh_date = %s" %(advance2low,  self.p.x2 , self.p.y2, midhigh_datetime, midhigh_date))
                advance2low = advance2low+1

            #start detecting Lows from low-midhigh-Lows
            advance2low = 2
            while loop2highlow_detect == 0:
                advance_detect_type = "low"
                for x2 in range(offset_val, 0):
                    #start detecting low - midhigh - Lows, ensure Lows 15 left and right no lower value
                    if data.low[advance2low] > data.low[advance2low+abs(x2)] or data.low[advance2low] > data.low[advance2low+x2]:# high, low, high detected
                        advance_detect_type = "0"
                #Lows detected so break the loop
                if advance_detect_type == "low":
                    loop2highlow_detect = 1
                    end_Lows_value = data.low[advance2low]
                    end_Lows_datetime = bt.date2num(self.data0.datetime.date(advance2low))
                    end_Lows_date = self.data0.datetime.date(advance2low)
                    x2_datetime = self.data0.datetime.date(advance2low)
                    if debug == 1:
                        print("2nd3 low-Lows detected     advance2low = %d,x2 = %s, y2 = %d, end_Lows_datetime = %d, end_Lows_date = %s " %(advance2low, self.p.x2, self.p.y2, end_Lows_datetime, end_Lows_date))
                advance2low = advance2low+1

            #check low-midhigh-Lows, either Lows detected early or midhigh detected early
            if advance_detect_type == "low":
                advance2low = advance2low-1

                #use timstamp to compare, low - Lows detected first or low - midhigh detected first
                if end_Lows_datetime < midhigh_datetime:
                    #low - Lows detected earlier, so get midhigh from low - Lows
                    midhigh_Lows_value = data.high[0]
                    midhigh_Lows_datetime = bt.date2num(self.data0.datetime.date(0))
                    x2_datetime = 0

                    #start capture the midhigh from low-Lows
                    for x3 in range(1, advance2low):
                        if data.high[x3] > midhigh_Lows_value:
                            midhigh_Lows_value = data.high[x3]
                            midhigh_Lows_datetime = bt.date2num(self.data0.datetime.date(x3))
                            midhigh_Lows_date = self.data0.datetime.date(x3)
                            x2_datetime = self.data0.datetime.date(x3)

                    # due to the Lows detected first, and midhigh get in between low - Lows
                    self.p.x2 = midhigh_Lows_datetime
                    self.p.y2 = midhigh_Lows_value
                    #self.p.y2 = self.p.x2

                    #line low-midhigh-Lows, to let midhigh capture first
                    prev_detected_type.append("midhigh")
                    prev_predicted_value.append(midhigh_Lows_value)
                    prev_predicted_time.append(midhigh_Lows_datetime)

                    #line low-midhigh-Lows, to let Lows capture
                    prev_detected_type.append("high")
                    prev_predicted_value.append(end_Lows_value)
                    prev_predicted_time.append(end_Lows_datetime)

                    if debug == 1:
                        print("2nd3 low-midhigh-Lows, Lows detect earlier than midhigh    advance2low = %d, prev_detected_type = %s, x2 = %s, y2 = %d, x1_datetime = %s, x2_datetime = %s, midhigh_Lows_datetime = %d, midhigh_Lows_date = %s, end_Lows_datetime = %d, end_Lows_date = %s"
                        %(advance2low, prev_detected_type[len(prev_detected_type)-1],  self.p.x2, self.p.y2, x1_datetime, x2_datetime, midhigh_Lows_datetime, midhigh_Lows_date, end_Lows_datetime, end_Lows_date))
                else:
                    #midhigh detected earlier so start setting
                    self.p.x2 = midhigh_datetime
                    self.p.y2 = midhigh_value
                    #self.p.x2 = self.p.x2

                    #line low-midhigh, to let midhigh capture only
                    prev_detected_type.append("low")
                    prev_predicted_value.append(midhigh_value)
                    prev_predicted_time.append(midhigh_datetime)
                    if debug == 1:
                        print("2nd4 low-midhigh, midhigh detect earlier than Lows    advance2low = %d, prev_detected_type = %s, x2 = %s, y2 = %d, x1_datetime = %s, x2_datetime = %s, midhigh_datetime = %d, midhigh_date = %s"
                        %(advance2low, prev_detected_type[len(prev_detected_type)-1], self.p.x2, self.p.y2, x1_datetime, x2_datetime, midhigh_datetime, midhigh_date))

            #start the
            self.m = self.get_slope(self.p.x1, self.p.x2, self.p.y1, self.p.y2)
            self.B = self.get_y_intercept(self.m, self.p.x1, self.p.y1)
            print("")
            return prev_predicted_value, prev_predicted_time, prev_detected_type

        return prev_predicted_value, prev_predicted_time, prev_detected_type

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
              ('prev_value', None),
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
