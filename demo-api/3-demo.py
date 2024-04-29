#!/usr/bin/env python

"""
Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from time import sleep
import os
import signal


class MyTopo(Topo):
    "Simple topology example."

    def build(self):
        "Create custom topo."

        # Add hosts and switches
        leftHost = self.addHost('h1')
        rightHost = self.addHost('h2')
        leftSwitch = self.addSwitch('s3')
        rightSwitch = self.addSwitch('s4')

        # Add links
        self.addLink(leftHost, leftSwitch)
        self.addLink(leftSwitch, rightSwitch)
        self.addLink(rightSwitch, rightHost)


topos = {'mytopo': (lambda: MyTopo())}


def openTerm(node, title, geometry, cmd="bash"):
    # display, tunnel = tunnelX11(node)
    return node.popen(["xterm",
                       "-hold",
                       "-title", "'%s'" % title,
                       "-geometry", geometry,
                       # "-display", display,
                       "-e", cmd])


def monitorHosts():
    "Create a Linear topology of k switches, with n hosts per switch."
    net = Mininet(topo=MyTopo(), waitConnected=True, link=TCLink)

    # Get host objects
    h1 = net.get('h1')
    h2 = net.get('h2')

    # Start network
    net.start()

    # Start iperf server at host2
    h2.cmd('iperf -s &')

    # Launch xterm in host h1 and start iperf client immediately
    cmd = "iperf -c %s -t 10; bash" % h2.IP()

    h1.cmd('xterm -e "%s" &' % cmd)

    # Start Mininet CLI (just a hack so that h1 xterm does not
    # disappear after iperf terminates)
    CLI(net)

    # Kill existing iperfs
    for host in net.hosts:
        host.cmd('killall iperf')

    # Done
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    monitorHosts()
