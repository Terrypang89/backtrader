#Setting Cash
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
#backtrader was imported

if __name__ == '__main__':

    #Cerebro engine was instantiated
    cerebro = bt.Cerebro()

    #setting Cash
    cerebro.broker.setcash(50000.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #resulting cerebro instance was told to run (loop over data)
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

