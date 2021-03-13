from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import struct

from backtrader.feed import DataBase
from backtrader import date2num
from backtrader import TimeFrame


class VChartData(DataBase):
    def __init__(self):
        super(VChartData, self).__init__()

        # Use the informative "timeframe" parameter to understand if the
        # code passed as "dataname" refers to an intraday or daily feed
        if self.p.timeframe >= TimeFrame.Days:
            self.barsize = 28
            self.dtsize = 1
            self.barfmt = 'IffffII'
        else:
            self.dtsize = 2
            self.barsize = 32
            self.barfmt = 'IIffffII'

    def start(self):
        # the feed must start ... get the file open (or see if it was open)
        self.f = None
        if hasattr(self.p.dataname, 'read'):
            # A file has been passed in (ex: from a GUI)
            self.f = self.p.dataname
        else:
            # Let an exception propagate
            self.f = open(self.p.dataname, 'rb')

    def stop(self):
        # Close the file if any
        if self.f is not None:
            self.f.close()
            self.f = None

    def _load(self):
        if self.f is None:
            # if no file ... no parsing
            return False

        # Read the needed amount of binary data
        bardata = self.f.read(self.barsize)
        if not bardata:
            # if no data was read ... game over say "False"
            return False

        # use struct to unpack the data
        bdata = struct.unpack(self.barfmt, bardata)

        # Years are stored as if they had 500 days
        y, md = divmod(bdata[0], 500)
        # Months are stored as if they had 32 days
        m, d = divmod(md, 32)
        # put y, m, d in a datetime
        dt = datetime.datetime(y, m, d)

        if self.dtsize > 1:  # Minute Bars
            # Daily Time is stored in seconds
            hhmm, ss = divmod(bdata[1], 60)
            hh, mm = divmod(hhmm, 60)
            # add the time to the existing atetime
            dt = dt.replace(hour=hh, minute=mm, second=ss)

        self.lines.datetime[0] = date2num(dt)

        # Get the rest of the unpacked data
        o, h, l, c, v, oi = bdata[self.dtsize:]
        self.lines.open[0] = o
        self.lines.high[0] = h
        self.lines.low[0] = l
        self.lines.close[0] = c
        self.lines.volume[0] = v
        self.lines.openinterest[0] = oi

        # Say success
        return True
