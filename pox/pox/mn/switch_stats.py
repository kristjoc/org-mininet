#!/usr/bin/env python

"""
POX Component to get switch statistics about:
uint64_t matched_count; /* Number of packets that hit table. */

Usage:

1. Run the POX controller

~/org-mininet/pox/pox.py log.level --INFO forwarding.l2_learning samples.pretty_log mn.switch_stats

2. Create a Linear topology with two switches in Mininet

sudo mn --controller=remote --topo=linear,2

3. Inside Mininet CLI run:

h1 ping h2

iperf h1 h2

Adapted from: http://xuyansen.work/get-flow-table-information-in-pox/
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.recoco import Timer
from collections import defaultdict
import time


class tableStats(EventMixin):
    def __init__(self, interval=10):
        self.tableMatchedCount = {}
        self.interval = interval
        core.openflow.addListeners(self)

    def _handle_ConnectionUp(self, event):
        "Callback when switch is connected"

        print("Switch %s has connected" % event.dpid)
        self.sendTableStatsRequest(event)

    def _handle_TableStatsReceived(self, event):
        "Callback when TableStats are received"

        sw = 's%s' % event.dpid
        self.tableMatchedCount[sw] = event.stats[0].matched_count
        print("TableStatsReceived")
        print(self.tableMatchedCount)
        Timer(self.interval, self.sendTableStatsRequest, args=[event])

    def sendTableStatsRequest(self, event):
        "Send Table Stats Request when switch is connected"

        sr = of.ofp_stats_request()
        sr.type = of.OFPST_TABLE
        event.connection.send(sr)
        print("Sent TableStat request to Switch %s " % event.dpid)


def launch(interval='5'):
    interval = int(interval) 
    core.registerNew(tableStats, interval)
