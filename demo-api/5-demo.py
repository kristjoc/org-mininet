#!/usr/bin/env python

"""
This example starts two iperf flows in a Mininet network and
monitors the congestion window of the first sender.

Topology:

    H1 ---- S ---- H3
            |
            |
            H2

"""

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import Link, TCLink
from mininet.node import Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.node import OVSKernelSwitch as Switch

from time import sleep, time
import multiprocessing
import subprocess
from subprocess import Popen, PIPE
import re
import os
import sys
from util.monitor import monitor_cpu, monitor_qlen, monitor_devs_ng


class MyTopo(Topo):
    "Simple topology example."

    def __init__(self):
        "Create custom topology."

        # Initialize topology
        Topo.__init__(self)

        # Add hosts and router
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1')
        h3 = self.addHost('h3')

        # Add links
        self.addLink(h1, s1, intfName1='h1-s1', intfName2='s1-h1', cls=TCLink)
        self.addLink(h2, s1, intfName1='h2-s1', intfName2='s1-h2', cls=TCLink)
        self.addLink(h3, s1, intfName1='h3-s1', intfName2='s1-h3', cls=TCLink,
                     bw=10, delay='10ms', max_queue_size=17)


def progress(t):
    "Prints the progress of the experiment"

    while t > 0:
        if t == 1:
            msg = "{} second left".format(t)
        else:
            msg = "{} seconds left".format(t)

        print('  {:>3}  \r'.format(msg), end="")
        t -= 1
        sys.stdout.flush()
        sleep(1)
    print('\r\n')


def run_cwnd_script(host, srcIP, srcPort, dstIP, dstPort):
    "Launch the cwnd_logger script to collect tcp cwnd stats"

    # Define the command as a string
    cmd = 'bash util/cwnd_logger.sh data/cwnd.dat 1 %s %s %s %s & echo $!' \
        % (srcIP, srcPort, dstIP, dstPort)

    # Use cmd to run the command
    pid = host.cmd(cmd)

    return pid


def main():
    "Create a topology"
    net = Mininet(topo=MyTopo(), waitConnected=True, switch=Switch,
                  autoStaticArp=True)

    net.start()

    # Start iperf server at h3
    h3 = net.get('h3')
    h3.cmd('iperf -s -Z reno &')

    # Launch cwnd script at h1
    h1 = net.get('h1')
    pid = run_cwnd_script(h1, h1.IP(), '30001', h3.IP(), '5001')

    for i in range(1, 3):
        hostName = 'h%d' % (i)
        srcPort = '%d' % (30000 + i)

        host = net.getNodeByName(hostName)

        cmd = 'nohup iperf -c %s -t 10 -i 1 -Z reno -B %s:%s \
        > data/iperf_%s.dat 2>&1 &' % (h3.IP(), host.IP(), srcPort, hostName)

        if i == 2:
            sleep(5)

        host.cmd(cmd)

    # Show the progress
    progress(10)

    # Cleanup
    h1.cmd('kill -9 {}'.format(pid))
    h1.cmd('killall cwnd_logger.sh')
    h1.cmd('killall iperf')
    h3.cmd('killall iperf')

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()

    # Define the command and the user under which you want to run the command
    command = "python util/plot_cwnd.py cwnd.dat"
    user = "kristjoc"

    # Use 'sudo -u' to run the command as a specific user
    subprocess.call(["sudo", "-u", user] + command.split())
