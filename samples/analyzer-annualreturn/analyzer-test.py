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
from pprint import pprint
# The above could be sent to an independent module
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
from backtrader.analyzers import (SQN, AnnualReturn, TimeReturn, SharpeRatio,
                                  TradeAnalyzer)


class LongShortStrategy(bt.Strategy):
    '''This strategy buys/sells upong the close price crossing
    upwards/downwards a Simple Moving Average.

    It can be a long-only strategy by setting the param "onlylong" to True
    '''
    params = dict(
        period=15,
        stake=1,
        printout=False,
        onlylong=False,
        csvcross=False,
    )

    def start(self):
        pass

    def stop(self):
        pass

    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print("Test_PIG_PIG %s, %s" % (dt.isoformat(), txt))

    def __init__(self):
        # To control operation entries
        self.orderid = None


        # Create SMA on 2nd data
        sma = btind.MovAv.SMA(self.data, period=self.p.period)
        # Create a CrossOver Signal from close an moving average
        self.signal = btind.CrossOver(self.data.close, sma)
        self.signal.csv = self.p.csvcross

    def start(self):
        print("hello start")
        #pprint(vars(self.analyzers))
        #pprint(vars(self.data.line))
        #2005-01-03 until 2006-12-29, as 2006-12-29 which will be data[0]
        print("data[0] 25.540001 = %s" %self.data.line[0])
        #print("data[-1] 25.360001 = %s" %self.data.line[-1])
        print("self.data.line6[0] = %s" %self.data.line6[0])
        print("self.data.line6[0] to date = %s" %bt.num2date(self.data.line6[0]))
        #print("test = %s" %datetime.datetime(2012, 6, 10, 16, 36, 20))
        #print("test date2num value = $s" %bt.date2num(datetime.datetime.strptime("2008-12-01T00:00:59.000000", '%Y-%m-%dT%H:%M:%S.%f')))
        print("convert to timestamep = %d" %time.mktime(datetime.datetime.strptime("2014-12-30 23:59:59.999989", "%Y-%m-%d %H:%M:%S.%f").timetuple()))
        #print("convert2timestamep = %d" %time.mktime(datetime.datetime.strptime("2014-12-30 23:59:59.999989", "%Y-%m-%d %H:%M:%S.%f").timetuple()))
        print("date convert datetime: %s" %datetime.datetime.strptime("2014-12-30 23:59:59.999989", "%Y-%m-%d %H:%M:%S.%f"))
        print("convert2timestamep = %s" %bt.date2num(datetime.datetime.strptime("2014-12-30 23:59:59.999989", "%Y-%m-%d %H:%M:%S.%f")))

    def prenext(self):
        #pprint(vars(self.data))
        #print("hello prenext") # which run 15 times
        pass

    def next(self):
        #print("next")
        #pprint(vars(self.analyzers))
        #print(" next self.data.line6[0] = %s" %bt.num2date(self.data.line6[0]))
        if self.orderid:
            return  # if an order is active, no new orders are allowed

        if self.signal > 0.0:  # cross upwards
            if self.position:
                self.log('CLOSE SHORT , %.2f' % self.data.close[0])
                self.close()

            self.log('BUY CREATE , %.2f' % self.data.close[0])
            self.buy(size=self.p.stake)

        elif self.signal < 0.0:
            if self.position:
                self.log('CLOSE LONG , %.2f' % self.data.close[0])
                self.close()

            if not self.p.onlylong:
                self.log('SELL CREATE , %.2f' % self.data.close[0])
                self.sell(size=self.p.stake)

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications

        if order.status == order.Completed:
            if order.isbuy():
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
            else:
                selltxt = 'SELL COMPLETE, %.2f' % order.executed.price
                self.log(selltxt, order.executed.dt)

        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            self.log('%s ,' % order.Status[order.status])
            pass  # Simply log

        # Allow new orders
        self.orderid = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('TRADE PROFIT, GROSS %.2f, NET %.2f' %
                     (trade.pnl, trade.pnlcomm))

        elif trade.justopened:
            self.log('TRADE OPENED, SIZE %2d' % trade.size)

    def stop(self):
        print("stop--------------------------------------------------------------")
        #pprint(vars(self.data.line6))
        #print("self.data.line6[0] = %s" %bt.num2date(self.data.line6[0]))

def runstrategy():
    args = parse_args()

    # Create a cerebro
    cerebro = bt.Cerebro()

    # Get the dates from the args
    fromdate = datetime.datetime.strptime(args.fromdate, '%Y-%m-%d')
    todate = datetime.datetime.strptime(args.todate, '%Y-%m-%d')

    # Create the 1st data
    data = btfeeds.BacktraderCSVData(
        dataname=args.data,
        fromdate=fromdate,
        todate=todate)

    # Add the 1st data to cerebro
    cerebro.adddata(data)

    # Add the strategy
    cerebro.addstrategy(LongShortStrategy,
                        period=args.period,
                        onlylong=args.onlylong,
                        csvcross=args.csvcross,
                        stake=args.stake)

    # Add the commission - only stocks like a for each operation
    cerebro.broker.setcash(args.cash)

    # Add the commission - only stocks like a for each operation
    cerebro.broker.setcommission(commission=args.comm,
                                 mult=args.mult,
                                 margin=args.margin)

    tframes = dict(
        days=bt.TimeFrame.Days,
        weeks=bt.TimeFrame.Weeks,
        months=bt.TimeFrame.Months,
        years=bt.TimeFrame.Years)

    # Add the Analyzers
    cerebro.addanalyzer(SQN)
    if args.legacyannual:
        cerebro.addanalyzer(AnnualReturn)
        cerebro.addanalyzer(SharpeRatio, legacyannual=True)
    else:
        cerebro.addanalyzer(TimeReturn, timeframe=tframes[args.tframe])
        cerebro.addanalyzer(SharpeRatio, timeframe=tframes[args.tframe])

    cerebro.addanalyzer(TradeAnalyzer)

    cerebro.addwriter(bt.WriterFile, csv=args.writercsv, rounding=4)

    # And run it
    cerebro.run()

    # Plot if requested
    if args.plot:
        cerebro.plot(numfigs=args.numfigs, volume=False, zdown=False)

def parse_args():
    parser = argparse.ArgumentParser(description='TimeReturn')

    parser.add_argument('--data', '-d',
                        #default='../../datas/2005-2006-day-001.txt',
                        default='../../datas/yhoo-1996-2014.txt',
                        help='data to add to the system')

    parser.add_argument('--fromdate', '-f',
                        default='2005-01-01',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', '-t',
                        #default='2006-12-31',
                        default='2014-12-31',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--period', default=15, type=int,
                        help='Period to apply to the Simple Moving Average')

    parser.add_argument('--onlylong', '-ol', action='store_true',
                        help='Do only long operations')

    parser.add_argument('--writercsv', '-wcsv', action='store_true',
                        help='Tell the writer to produce a csv stream')

    parser.add_argument('--csvcross', action='store_true',
                        help='Output the CrossOver signals to CSV')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--tframe', default='years', required=False,
                       choices=['days', 'weeks', 'months', 'years'],
                       help='TimeFrame for the returns/Sharpe calculations')

    group.add_argument('--legacyannual', action='store_true',
                       help='Use legacy annual return analyzer')

    parser.add_argument('--cash', default=100000, type=int,
                        help='Starting Cash')

    parser.add_argument('--comm', default=2, type=float,
                        help='Commission for operation')

    parser.add_argument('--mult', default=10, type=int,
                        help='Multiplier for futures')

    parser.add_argument('--margin', default=2000.0, type=float,
                        help='Margin for each future')

    parser.add_argument('--stake', default=1, type=int,
                        help='Stake to apply in each operation')

    parser.add_argument('--plot', '-p', action='store_true',
                        help='Plot the read data')

    parser.add_argument('--numfigs', '-n', default=1,
                        help='Plot using numfigs figures')

    return parser.parse_args()


if __name__ == '__main__':
    runstrategy()
