# DX Cluster Server Info

There are a few different DX cluster software packages.

* PacketCLuster
* DX Spider
* CC Cluster
* Clusse (older deprecated?)

## Verified Servers

* [dx.k3lr.com](telnet://dx.k3lr.com) running AR-Cluster Version 6
* [dxc.w3lpl.net](telnet://dxc.w3lpl.net)

## Protocol Information

The DX cluster messages are line-oriented and can be accessed via telnet. 

The station reports are in the following format:

<pre>
DX de S53M:       7064.6  KL7SB        rtty, ufb sig                  0302Z
DX de CT7AUT:    28074.0  VK2JJM       ft8 tnx 73                     0305Z
DX de N6DW:       3586.4  KE0L         WW RTTY                        0306Z
</pre>

These messages are fairly simple because these systems were originally designed
to operate over 1200 baud packet radio in the 1980s. 

The fields of the message are:

* Reporting station callsign
* Frequency in kilohertz
* Station being spotted
* A free form note or description of the signals
* Time of report in UTC/GMT

## Reverse Beacon Network

TODO

## Python Script

The initial AI generated version of this script used the deprecated telnetlib. 

Had to re-write for just sockets or use compatibility lib.

## References

* https://en.wikipedia.org/wiki/DX_cluster
* http://www.dxcluster.org
