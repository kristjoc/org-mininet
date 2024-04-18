#!/usr/bin/env python

"""
This example monitors a number of hosts using host.popen() and
pmonitor()

Topology:
          h1s1           h1s2
              \         /
               s1 --- s2
              /         \
          h2s1           h2s2
"""

from mininet.net import Mininet
from mininet.topo import LinearTopo
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.util import pmonitor


def monitorHosts(k=2, n=2):
    "Create a Linear topology of k switches, with n hosts per switch."
    mytopo = LinearTopo(k, n)
    net = Mininet(topo=mytopo, waitConnected=True, link=TCLink)

    # Get switch objects
    s1, s2 = net.switches

    # Modify link parameters between switches
    net.delLinkBetween(s1, s2)
    net.addLink(s1, s2, cls=TCLink, bw=10, delay='10ms')

    net.start()

    servers = []
    for host in net.hosts:
        if 's2' in host.name:
            servers.append(host)
            # Start iperf server at h1s2 h2s2
            host.cmd('iperf -s &')

    # Start iperf clients
    popens = {}
    for host in net.hosts:
        if 'h1s1' in host.name:
            popens[host] = host.popen("iperf -c %s -t 10" % servers[0].IP())
        if 'h2s1' in host.name:
            popens[host] = host.popen("iperf -c %s -t 10" % servers[1].IP())

    # Monitor them and print output
    for host, line in pmonitor(popens):
        if host:
            info("<%s>: %s" % (host.name, line))

    # Stop any iperf instances running on the hosts
    for host in net.hosts:
        host.cmd('killall iperf')

    # Done
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    monitorHosts(2, 2)
