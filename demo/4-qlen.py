
""" Simple mininet script to create the following topology
    H1 ---- R ---- H3
            |
            |
            H2
    Usage: sudo -E mn --custom topo.py --topo mytopo
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
                     bw=10, delay='10ms', max_queue_size=100)


def progress(t):
    while t > 0:
        print('  %3d seconds left  \r' % (t))
        t -= 1
        sys.stdout.flush()
        sleep(1)
    print('\r\n')


def main():
    "Create a topology"
    net = Mininet(topo=MyTopo(), waitConnected=True, switch=Switch,
                  autoStaticArp=True)
    net.start()

    h3 = net.get('h3')
    h3.cmd('iperf -s &')

    monitors = []
    monitor = multiprocessing.Process(target=monitor_qlen,
                                      args=('s1-h3', 0.01, 'data/qlen_s1-h3.dat'))

    monitor.start()
    monitors.append(monitor)

    for i in range(1, 3):
        host = 'h%d' % (i)
        cmd = 'iperf -c %s -t 10 -i 1 -Z reno > data/iperf_%s.dat' % (h3.IP(), host)
        h = net.getNodeByName(host)
        h.cmd(cmd)

    progress(10)

    for monitor in monitors:
        monitor.terminate()

    h3.cmd('killall iperf')

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()

    # Define the command and the user under which you want to run the command
    command = "python util/plot_qdisc.py data/qlen_s1-h3.dat"
    user = "kristjoc"

    # Use 'sudo -u' to run the command as a specific user
    subprocess.call(["sudo", "-u", user] + command.split())
