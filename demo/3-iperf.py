"""Custom topology example

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
# from mininet.util import pmonitor

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )
        leftSwitch = self.addSwitch( 's3' )
        rightSwitch = self.addSwitch( 's4' )

        # Add links
        self.addLink( leftHost, leftSwitch )
        self.addLink( leftSwitch, rightSwitch )
        self.addLink( rightSwitch, rightHost )


topos = { 'mytopo': ( lambda: MyTopo() ) }


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

    h2 = net.get('h2')
    h1 = net.get('h1')

    net.start()

    h2.cmd('iperf -s &')

    # Launch xterm in host h1
    cmd = "iperf -c %s -t 10; bash" % h2.IP()

    h1.cmd('xterm -e "%s" &' % cmd)
    # Start iperf clients
    # terms = []
    # terms.append(openTerm(node=h1,
    #                       title="h1",
    #                       geometry="80x14+555+0",
    #                       cmd="iperf -c %s -t 10" % h2.IP()))

    # Stop any iperf instances running on the hosts

    CLI(net)

    # for t in terms:
    #     os.kill(t.pid, signal.SIGKILL)
    for host in net.hosts:
        host.cmd('killall iperf')

    # Done
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    monitorHosts()
