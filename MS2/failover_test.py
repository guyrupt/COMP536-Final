#!/usr/bin/env python3
import random
import socket
import sys

from scapy.all import (
    IP,
    TCP,
    Ether,
    get_if_hwaddr,
    get_if_list,
    sendp,
    Packet,
    BitField,
    bind_layers,
    XByteField,
    ShortField,
    IntField,
)

from send import KVS, Response

RESPONSE_PTC = 0x1234
KVS_PTC = 145

bind_layers(Ether, Response, type=RESPONSE_PTC)
bind_layers(Response, Response, nextHeader=0)
bind_layers(Response, IP, nextHeader=1)
bind_layers(IP, KVS, proto=KVS_PTC)
bind_layers(KVS, TCP, protocol=6)


def get_if():
    ifs = get_if_list()
    iface = None  # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface = i
            break
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface


def main():
    addr = "10.0.1.1"
    iface = get_if()

    print("sending on interface %s to %s" % (iface, str(addr)))
    pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff")
    pkt = pkt / Response()
    pkt = pkt / IP(dst=addr)
    for i in range(0, 200):  # 200 PUT requests targeting s1
        pkt0 = pkt.copy()
        pkt0 = pkt0 / KVS(operation=2, first=i, second=i)
        pkt0 = pkt0 / TCP(dport=1234, sport=random.randint(49152, 65535))
        sendp(pkt, iface=iface, verbose=False)


if __name__ == "__main__":
    main()
