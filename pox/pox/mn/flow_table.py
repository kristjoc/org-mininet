#!/usr/bin/python
# Copyright 2012 William Yu
# wyu@ateneo.edu
#
# This file is part of POX.
#
# POX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# POX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with POX. If not, see <http://www.gnu.org/licenses/>.
#

"""
This is a demonstration file created to show how to obtain flow 
and port statistics from OpenFlow 1.0-enabled switches. The flow
statistics handler contains a summary of web-only traffic.
"""

# standard includes
from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of

# include as part of the betta branch
from pox.openflow.of_json import *

log = core.getLogger()

# handler for timer function that sends the requests to all the
# switches connected to the controller.
def _timer_func ():
  for connection in core.openflow._connections.values():
    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
    log.debug("Sent %i flow stats request(s)", len(core.openflow._connections))

# handler to display flow statistics received in JSON format
# structure of event.stats is defined by ofp_flow_stats()
def _handle_flowstats_received (event):
  stats = flow_stats_to_list(event.stats)
  log.debug("FlowStatsReceived from %s: %s", 
            dpidToStr(event.connection.dpid), stats)

  for f in event.stats:

    print('Flow Table Entry')
    print('----------------')
    print(' - In Port: ', f.match.in_port) 
    print(' - Ethernet Source: ', f.match.dl_src)
    print(' - Ethernet Destination: ', f.match.dl_dst)
    print(' - TCP src port: ', f.match.tp_src)
    print(' - TCP dest port: ', f.match.tp_dst)
    # print other match fields

    print('Actions:')
    for action in f.actions:
      print(' - ', action)

    print('Stats:')
    print(' - Byte Count:', f.byte_count)
    print(' - Packet Count:', f.packet_count)

    log.info("IP traffic from %s", 
             dpidToStr(event.connection.dpid))

    
# main functiont to launch the module
def launch ():
  from pox.lib.recoco import Timer

  # attach handsers to listners
  core.openflow.addListenerByName("FlowStatsReceived", 
                                  _handle_flowstats_received) 

  # timer set to execute every five seconds
  Timer(5, _timer_func, recurring=True)
