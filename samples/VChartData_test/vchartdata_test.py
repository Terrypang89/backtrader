from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime

import backtrader as bt
from vchart import VChartData


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    cerebro.addstrategy(bt.Strategy)

    ###########################################################################
    # Note:
    # The goog.fd file belongs to VisualChart and cannot be distributed with
    # backtrader
    #
    # VisualChart can be downloaded from www.visualchart.com
    ###########################################################################
    # Create a Data Feed
    datapath = '../../datas/goog.fd'
    data = VChartData(
        dataname=datapath,
        fromdate=datetime.datetime(2006, 1, 1),
        todate=datetime.datetime(2006, 12, 31),
        timeframe=bt.TimeFrame.Days
    )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Run over everything
    cerebro.run()

    # Plot the result
    cerebro.plot(style='bar')
