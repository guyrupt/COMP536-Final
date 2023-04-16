#!/usr/bin/env python3
import os
import sys

from scapy.all import (
    TCP,
    FieldLenField,
    FieldListField,
    IntField,
    IPOption,
    ShortField,
    get_if_list,
    sniff,
)
from scapy.layers.inet import _IPOption_HDR

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
    iface = None
    for i in get_if_list():
        if "eth0" in i:
            iface = i
            break
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface


class IPOption_MRI(IPOption):
    name = "MRI"
    option = 31
    fields_desc = [
        _IPOption_HDR,
        FieldLenField(
            "length", None, fmt="B", length_of="swids", adjust=lambda pkt, l: l + 4
        ),
        ShortField("count", 0),
        FieldListField(
            "swids", [], IntField("", 0), length_from=lambda pkt: pkt.count * 4
        ),
    ]


def get_packet_layers(packet):
    counter = 0
    while True:
        layer = packet.getlayer(counter)
        if layer is None:
            break

        yield layer
        counter += 1


def handle_pkt(pkt):
    # if KVS in pkt:
    #     print("got a packet")
    #     pkt.show2()
    if KVS in pkt and pkt[TCP].dport == 1234 and pkt[Ether].dst == "08:00:00:00:01:11":
        # print("got a packet")
        # pkt.show2()
        #    hexdump(pkt)
        if pkt[KVS].operation == 1:
            if pkt[Response].notNull == 1:
                print(f"value: {pkt[Response].value}")
            else:
                print("value is null")

        elif pkt[KVS].operation == 2:
            print("inserted")

        elif pkt[KVS].operation == 3 or pkt[KVS].operation == 4:
            print("range query")
            for hdr in reversed(list(get_packet_layers(pkt))):
                if hdr.name == "Response" and hdr.nextHeader == 0:
                    if hdr.notNull == 1:
                        print(f"value: {hdr.value}")
                    else:
                        print("value is null")

        sys.stdout.flush()
        # print(pkt[Response].payload)


def main():
    ifaces = [i for i in os.listdir("/sys/class/net/") if "eth" in i]
    iface = ifaces[0]
    print("sniffing on %s" % iface)
    sys.stdout.flush()
    sniff(iface=iface, prn=lambda x: handle_pkt(x))


if __name__ == "__main__":
    main()
