#!/usr/bin/env python3
import random
import socket
import sys

from scapy.all import IP, TCP, Ether, get_if_hwaddr, get_if_list, \
sendp, Packet, BitField,bind_layers,XByteField,ShortField, IntField

RESPONSE_PTC = 0x1234
KVS_PTC = 145

class KVS(Packet):
    name = "KVS"
    fields_desc = [ XByteField("operation",0),
                    ShortField("first",2000),
                    BitField("second",2000,32),
                    BitField("version",0,32),
                    BitField("protocol",0,8),
                    BitField("switch",0,8),
                    BitField("pingpong",0,8)]

class Response(Packet):
    name = "Response"
    fields_desc = [ IntField("value",0),
                    BitField("notNull", 0, 1),
                    BitField("nextHeader", 0, 1),
                    BitField("reserved", 0, 6),]

bind_layers(Ether, Response, type=RESPONSE_PTC)
bind_layers(Response, Response, nextHeader=0)
bind_layers(Response, IP, nextHeader=1)
bind_layers(IP, KVS, proto=KVS_PTC)
bind_layers(KVS, TCP, protocol=6)
     
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

    if len(sys.argv)<2:
        print('pass arguments: <operation> <options>')
        exit(1)
    print(sys.argv)
    addr = "10.0.1.1"
    iface = get_if()

    print("sending on interface %s to %s" % (iface, str(addr)))
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt / Response()

    if sys.argv[1] == 'GET':
        print('GET')
        if len(sys.argv) < 4:
            print('pass 2 more arguments:"<key>" "<version>"')
            exit(1)
        if int(sys.argv[2]) > 1025 or int(sys.argv[2]) < 0:
            print('key out of range')
            exit(1)
        pkt = pkt / IP(dst=addr)
        pkt = pkt / KVS(operation=1, first=int(sys.argv[2]), second=0, version=int(sys.argv[3]))
        pkt = pkt / TCP(dport=1234, sport=random.randint(49152,65535))
        pkt.show2()
        print('packet size',len(pkt))
        sendp(pkt, iface=iface, verbose=False)

    elif sys.argv[1] == 'PUT':
        print('PUT')
        if len(sys.argv) < 4:
            print('pass 2 more arguments:"<key>" "<value>"')
            exit(1)
        if int(sys.argv[2]) > 1025 or int(sys.argv[2]) < 0:
            print('key out of range')
            exit(1)
        
        pkt = pkt / IP(dst=addr)
        pkt = pkt / KVS(operation=2, first=int(sys.argv[2]), second=int(sys.argv[3]))
        pkt = pkt / TCP(dport=1234, sport=random.randint(49152,65535))
        pkt.show2()
        print('packet size',len(pkt))
        sendp(pkt, iface=iface, verbose=False)

    elif sys.argv[1] == 'RANGE':
        print('RANGE')
        if len(sys.argv) < 5:
            print('pass 3 more arguments:"<key1>" "<key2>" "<versionNum>"')
            exit(1)
        if int(sys.argv[2]) > 1025 or int(sys.argv[2]) < 0:
            print('key out of range')
            exit(1)

        op=3
        first=int(sys.argv[2])
        second=int(sys.argv[3])
        version=int(sys.argv[4])
        num_keys = second - first + 1

        for i in range(first, second + 1, 10):
            pkt0 = pkt.copy()
            end = i + (9 if (second - i) // 10 else (second - i))
            print(i, end)
            pkt0 = pkt0 / IP(dst=addr)
            pkt0 = pkt0/ KVS(operation=op, first=i, second=end, version=version)
            pkt0 = pkt0 / TCP(dport=1234, sport=random.randint(49152,65535))
            sendp(pkt0, iface=iface, verbose=False)
            print(pkt0)

    elif sys.argv[1] == 'SELECT':
        op=4
        if len(sys.argv) < 5:
            print('pass 3 more arguments:"<operand>" "<value>" "<versionNum>"')
            exit(1)
        if int(sys.argv[3]) > 1025 or int(sys.argv[3]) < 0:
            print('key out of range')
            exit(1)

        operand = sys.argv[2]
        first, second = 0, 0
        value = int(sys.argv[3])
        version = int(sys.argv[4])

        if operand == '<':
            first, second = 0, value - 1
        elif operand == '>':
            first, second = value + 1, 1024
        elif operand == '<=':
            first, second = 0, value
        elif operand == '>=':
            first, second = value, 1024
        elif operand == '==':
            first, second = value, value
        else:
            print('invalid operand')
            exit(1)
            
        for i in range(first, second + 1, 10):
            pkt0 = pkt.copy()
            end = i + (9 if (second - i) // 10 else (second - i))
            print(i, end)
            pkt0 = pkt0 / IP(dst=addr)
            pkt0 = pkt0/ KVS(operation=op, first=i, second=end, version=version)
            pkt0 = pkt0 / TCP(dport=1234, sport=random.randint(49152,65535))
            sendp(pkt0, iface=iface, verbose=False)
            print(pkt0)


    # pkt.show2()
    # print('packet size',len(pkt))
    # sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
