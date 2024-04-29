#!/usr/bin/env python

"""
This example shows how to create a Mininet network (without a
topology object) and add nodes to it manually.

Topology: h1 -- s1 --- s2 -- h2
"""

from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from time import sleep


def setupNet():
    "Create a network and add nodes to it."

    info('*** Creating network object\n')
    net = Mininet(controller=OVSController, waitConnected=True, link=TCLink)

    info('*** Adding controller c0\n')
    net.addController('c0')

    info('*** Adding hosts h1 h2\n')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')

    info('*** Adding switches s1 s2\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    info('*** Creating links: h1 -- s1 --- s2 -- h2\n')
    net.addLink(h1, s1, intfName1='h1-s1', intfName2='s1-h1', cls=TCLink)
    net.addLink(h2, s2, intfName1='h2-s2', intfName2='s2-h2', cls=TCLink)
    net.addLink(s1, s2, intfName1='s1-s2', intfName2='s2-s1',
                cls=TCLink, bw=10, delay='5ms')

    return net


def testPing(h1, h2):
    "Ping host2 from host1"

    # Store the ping results
    pingLog = 'ping.log'

    # Launch ping command at host1
    h1.cmd('ping -c 4 {} > {}'.format(h2.IP(), pingLog))


def startIperf(h1, h2):
    "Measure max. bandwidth between host1 and host2 using iperf"

    # Store the iperf results
    iperfLog = 'iperf.log'

    # Start iperf server at host2
    h2.cmd('iperf -s &')

    sleep(1)

    # Start iperf client at host1
    h1.cmd('iperf -c {} -t 10 > {}'.format(h2.IP(), iperfLog))


def stopIperf(*hosts):
    "Stop any iperf instances running on the specified hosts"

    for host in hosts:
        host.cmd('killall iperf')


if __name__ == '__main__':
    setLogLevel('info')

    # Prepare the network
    net = setupNet()

    # Get host objects
    h1, h2 = net.get('h1', 'h2')

    info('*** Starting network\n')
    net.start()

    info('*** Pinging host2 from host1\n')
    testPing(h1, h2)

    info('*** Starting iperf apps\n')
    startIperf(h1, h2)

    info('*** Stopping iperf apps\n')
    stopIperf(h1, h2)

    # CLI(net)

    info('*** Stopping network\n')
    net.stop()
