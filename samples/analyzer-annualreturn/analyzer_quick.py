from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime

import backtrader as bt
import backtrader.analyzers as btanalyzers
import backtrader.feeds as btfeeds
import backtrader.strategies as btstrats

cerebro = bt.Cerebro()

# data
dataname = '../../datas/yhoo-1996-2014.txt'
data = btfeeds.BacktraderCSVData(dataname=dataname)

cerebro.adddata(data)

# strategy
cerebro.addstrategy(btstrats.SMA_CrossOver)

# Analyzer
cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
cerebro.addanalyzer(btanalyzers.TimeReturn, data=data, _name='myret')

thestrats = cerebro.run()
thestrat = thestrats[0]

print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis())
#print(thestrats.datas[5])

tmp = thestrat.analyzers.myret.get_analysis()
#for item in tmp.items()[-12:]:
    #for i in item:
        #print("i = %d, j = %d" %(i,j))
    #print(item)
    #print("j = %d" %(j))
