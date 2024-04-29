# Hands-on Demo session: The BIRD Internet Routing Daemon

In this session we will talk about BIRD, the BIRD Internet Routing Daemon,
which was developed as a school project at Faculty of Math and Physics, Charles
University Prague.

## BIRD ##

The BIRD project aims to develop a fully functional dynamic IP routing daemon
primarily targeted on (but not limited to) Linux, FreeBSD and other UNIX-like
systems and distributed under the GNU General Public License. Read more about
BIRD [here](https://bird.network.cz/).  


Using
[this](https://github.com/kristjoc/org-mininet/blob/main/bird/init_mn.py)
mininet script, we will build a BIRD topology as shown in
[this](https://github.com/kristjoc/org-mininet/blob/main/bird/bird_topology.pdf)
figure.  

### Installation ###

To install `bird` in your computer use `sudo apt install bird`
command, which will install `BIRD version 1.6.8`. The config files for r1, r2,
and r3 are written for this version.  

### Usage ###

To run the mininet script use the following command:

```
   $ sudo -E python3 init_mn.py
```

Inside the mininet CLI, launch xterms of the nodes with `xterm A B r1 r2 r3`.
Inside the xterms, one can connect to the BIRD controller using `birdc -s
bird.ctl` in the r1, r2, or r3 directories and apply Cisco-like commands (`show
routes`, `show rip/ospf neighbors`, etc.).  

Use `wireshark`, `tshark` or `tcpdump` to capture HELLO and UPDATEs packets of
the routing protocols.  

When the routing protocol has converged, you should be able to ping from A to B
`ping 162.168.3.100`.  

Try `link r1 r3 down` inside the Mininet CLI. The Routing protocol
should converge in about 20s and the ICMP packets will be sent via the
r1 - r2 link.

