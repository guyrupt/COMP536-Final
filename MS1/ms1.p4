/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<8> TYPE_TCP = 6;
const bit<8> TYPE_KVS = 145;
const bit<8> RECIRC_FL = 0;
const bit<32> SELECT_LT = 0x401;
const bit<32> SELECT_GT = 0x402;
const bit<32> SELECT_LE = 0x403;
const bit<32> SELECT_GE = 0x404;
const bit<32> SELECT_EQ = 0x405;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<16> port_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header tcp_t {
    port_t srcPort;
    port_t dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<3>  res;
    bit<3>  ecn;
    bit<6>  ctrl;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

header kvs_t {
    bit<8> op;
    bit<16> first;
    bit<32> second;
    bit<32> version;
    bit<8> protocol;
}

header response_t {
    bit<32> value;
    bit<1> notNull;
    bit<1> nextHeader;
    bit<6> reserved;
}

struct metadata {
    @field_list(RECIRC_FL)
    bit<16> circulate_index;
}

struct headers {
    ethernet_t  ethernet;
    ipv4_t      ipv4;
    tcp_t       tcp;
    kvs_t       kvs;
    response_t[1025]  response;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {
    state start {
        transition parse_ethernet;
    }
    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x1234: parse_response;
            default: accept;
        }
    }
    state parse_response {
        packet.extract(hdr.response.next);
        transition select(hdr.response.last.nextHeader){
            0: parse_response;
            1: parse_ipv4;
            default: accept;
        }
    }
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            TYPE_TCP: parse_tcp;
            TYPE_KVS: parse_kvs;
            default: accept;
        }
    }
    state parse_kvs {
        packet.extract(hdr.kvs);
        transition select(hdr.kvs.protocol) {
            TYPE_TCP: parse_tcp;
            default: accept;
        }
    }
    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }   
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    
    // register <bit<32>>(1025) database;
    register <bit<32>>(6150) database;
    register <bit<32>>(1025) latestVer;
    register <bit<1>>(1025) notNull;

    action set_nhop(ip4Addr_t dstAddr, egressSpec_t port) {
        hdr.ipv4.dstAddr = dstAddr;
        standard_metadata.egress_spec = port;
    }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action get() {
        bit<32> ver = hdr.kvs.version;

        database.read(hdr.response[0].value, (bit<32>)hdr.kvs.first + 1025 * ver);
        notNull.read(hdr.response[0].notNull, (bit<32>)(hdr.kvs.first));

        bit<32> latest = 0;
        latestVer.read(latest, (bit<32>)(hdr.kvs.first));
        if (hdr.kvs.version > latest - 1) {
            hdr.response[0].notNull = 0;
        }

    }

    action put() {
        bit<32> ver = 0;
        latestVer.read(ver, (bit<32>)hdr.kvs.first);
        database.write((bit<32>)hdr.kvs.first + 1025 * ver, hdr.kvs.second);
        notNull.write((bit<32>)hdr.kvs.first, 1);
        ver = ver + 1;
        latestVer.write((bit<32>)hdr.kvs.first, ver);
    }
    
    action get_range() {
        bit<32> ver = hdr.kvs.version;

        hdr.response.push_front(1);
        hdr.response[0].setValid();

        bit<16> key = hdr.kvs.first + meta.circulate_index;
        database.read(hdr.response[0].value, (bit<32>)key + 1025 * ver);
        notNull.read(hdr.response[0].notNull, (bit<32>)(key));

        bit<32> latest = 0;
        latestVer.read(latest, (bit<32>)(key));
        if (hdr.kvs.version > latest - 1) {
            hdr.response[0].notNull = 0;
        }

        meta.circulate_index = meta.circulate_index + 1;
    }

    action select_lt() {
        hdr.kvs.second = (bit<32>) hdr.kvs.first - 1;
        hdr.kvs.first = 0;
    }

    action select_gt() {
        hdr.kvs.first = hdr.kvs.first + 1;
        hdr.kvs.second = 1024;
    }

    action select_le() {
        hdr.kvs.second = (bit<32>) hdr.kvs.first;
        hdr.kvs.first = 0;
    }

    action select_ge() {
        hdr.kvs.second = 1024;
    }

    action select_eq() {
        hdr.kvs.second = (bit<32>) hdr.kvs.first;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            set_nhop;
            drop;
        }
        size = 1024;
        default_action = drop();
    }

    table kvs {
        key = {
            hdr.kvs.op: exact;
        }
        actions = {
            get;
            put;
            get_range;
        }
        size = 1024;
    }

    table select_ops {
        key = {
            hdr.kvs.second: exact;
        }
        actions = {
            select_lt;
            select_gt;
            select_le;
            select_ge;
            select_eq;
            NoAction;
        }
        default_action = NoAction;
        const entries = {
            SELECT_LT: select_lt();
            SELECT_GT: select_gt();
            SELECT_LE: select_le();
            SELECT_GE: select_ge();
            SELECT_EQ: select_eq();
        }
    }

    apply {
        // if (hdr.ethernet.etherType == TYPE_IPV4) {
        //     ipv4_lpm.apply();
        //     if (hdr.tcp.dstPort == 0x1234) {
        //         kvs.apply();
        //         hdr.kvs.first = 0;
        //         hdr.kvs.second = 0;
        //     } 
        // }
        if(hdr.response[0].isValid()){
            ipv4_lpm.apply();
            kvs.apply();
            
            if (hdr.kvs.op == 4) {
                select_ops.apply();
                get_range();
            }

        }
        
        
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  
        if (hdr.response[0].isValid() && (hdr.kvs.op == 3 || hdr.kvs.op == 4)) {
            if ((bit<32>)(hdr.kvs.first + meta.circulate_index) <= hdr.kvs.second) {
                recirculate_preserving_field_list(RECIRC_FL);
            } 
        }
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
        update_checksum(
            hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet,
                   in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.response);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.kvs);
        packet.emit(hdr.tcp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
