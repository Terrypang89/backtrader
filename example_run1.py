#Basic Setup
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
#backtrader was imported

if __name__ == '__main__':
	
    cerebro = bt.Cerebro()
	#Cerebro engine was instantiated
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()
	#resulting cerebro instance was told to run (loop over data)
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
	# resulting outcome was printed out
