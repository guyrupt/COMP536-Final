#!/usr/bin/env python3
import random
import socket
import sys

from scapy.all import IP, TCP, Ether, get_if_hwaddr, get_if_list, sendp, Packet, BitField,bind_layers,XByteField,ShortField
class KVS(Packet):
    name = "KVS"
    fields_desc = [ XByteField("operation",0),
                    ShortField("first",2000),
                    BitField("second",2000,32),
                    BitField("version",0,32),
                    BitField("responseStatus",0,1),
                    BitField("reserved", 0,15),
                    ]

bind_layers(TCP, KVS)

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def main():

    if len(sys.argv)<3:
        print('pass 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print("sending on interface %s to %s" % (iface, str(addr)))
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    op=0
    fir=0
    sec=0
    if sys.argv[2]=='GET':
        op=1
        fir=int(sys.argv[3])
    elif sys.argv[2]=='PUT':
        op=2
        fir=int(sys.argv[3])
        sec=int(sys.argv[4])
    elif sys.argv[2]=='RANGE':
        op=3
        fir=int(sys.argv[3])
        sec=int(sys.argv[4])
    elif sys.argv[2]=='SELECT':
        op=3
        operand = ''.join(i for i in sys.argv[3] if not i.isdigit())
        import re
        val=int(re.findall('\d+', sys.argv[3] )[0])
        if operand=='=':
            fir=val
            sec=val
        elif operand=='<':
            fir=0
            sec=val-1
        elif operand=='<=':
            fir=0
            sec=val
        elif operand=='>':
            fir=val+1
            sec=1024
        elif operand=='>=':
            fir=val
            sec=1024


    pkt = pkt /IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) /KVS(operation=op,first=fir,second=sec) / 'test'
    pkt.show2()
    print('packet size',len(pkt))
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
