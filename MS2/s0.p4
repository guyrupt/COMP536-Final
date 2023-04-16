/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<8> TYPE_TCP = 6;
const bit<8> TYPE_KVS = 145;
const bit<8> RECIRC_FL = 0;

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
    bit<8> pingpong;
}

header response_t {
    bit<32> value;
    bit<1> notNull;
    bit<1> nextHeader;
    bit<6> reserved;
}

struct metadata {
    bit<14> nport;
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
    
    register <bit<9>>(2) healthy_db; // port number of healthy db. 0 for db1(<=512), 1 for db2(>512)
    register <bit<32>>(1) request_cnt; // count total requests
    register <bit<32>>(2) pingpong_1; // 0 for ping count , 1 for pong count
    register <bit<32>>(2) pingpong_2; // 0 for ping count , 1 for pong count


    apply {
        if(hdr.kvs.isValid()) {
            bit<9> db1 = 0;
            bit<9> db2 = 0;
            healthy_db.read(db1, 0);
            healthy_db.read(db2, 1);

            if(standard_metadata.ingress_port == 1){ // packets to forward to dbs 
                bit<32> req_cnt = 0;
                request_cnt.read(req_cnt, 0);
                bit<16> a = (bit<16>)req_cnt;
                bit<16> b = 10;
                bit<16> mod_result;

                hash(mod_result, HashAlgorithm.identity, (bit<16>)0, {a}, b);
                if (mod_result == 0){ // send ping packet
                    hdr.kvs.pingpong = 1; // mark as ping packet

                    // update ping counters
                    bit<32> ping_cnt = 0;
                    pingpong_1.read(ping_cnt, 0);
                    pingpong_1.write(0, ping_cnt+1);
                    pingpong_2.read(ping_cnt, 0);
                    pingpong_2.write(0, ping_cnt+1);

                    request_cnt.write(0, 0); // update request counter

                }
                
                if (db1 == 0 && db2 == 0) { // first time, setting default dbs
                    healthy_db.write(0, 2);
                    healthy_db.write(1, 3);
                }
                
                a = (bit<16>)req_cnt;
                b = 15;

                hash(mod_result, HashAlgorithm.identity, (bit<16>)0, {a}, b);
                if (mod_result == 0){ // check health of dbs
                    bit<32> ping_cnt = 0;
                    bit<32> pong_cnt = 0;
                    pingpong_1.read(ping_cnt, 0);
                    pingpong_1.read(pong_cnt, 1);
                    if (ping_cnt >= pong_cnt + 10){ // db1 is unhealthy
                        healthy_db.write(0, 4); // replace unhealthy db with backup
                        pingpong_1.write(0, 0); // reset pingpong counters
                        pingpong_1.write(1, 0);
                    }

                    pingpong_2.read(ping_cnt, 0);
                    pingpong_2.read(pong_cnt, 1);
                    if (ping_cnt >= pong_cnt + 10){ // db2 is unhealthy
                        healthy_db.write(1, 4); // replace unhealthy db with backup
                        pingpong_2.write(0, 0); // reset pingpong counters
                        pingpong_2.write(1, 0);
                    }

                    request_cnt.write(0, 0); // update request counter

                }

                // select healthy db to forward to
                healthy_db.read(db1, 0);
                healthy_db.read(db2, 1);
                
                if (hdr.kvs.first <= 512) {
                    standard_metadata.egress_spec = db1;
                    if (db1 == 4)
                        mark_to_drop(standard_metadata);
                } 
                else{
                    standard_metadata.egress_spec = db2;
                    if (db2 == 4)
                        mark_to_drop(standard_metadata);
                }
                
                if (hdr.kvs.pingpong == 1) {

                    // ping packets need to be sent to both switches
                    if (hdr.kvs.first <= 512)
                        clone(CloneType.I2E, 3); // clone ping packet to db2
                    else
                        clone(CloneType.I2E, 2); // clone ping packet to db1
                } else {
                    clone(CloneType.I2E, 1); // clone to backup db
                }
                request_cnt.write(0, req_cnt+1); // update request counter
            }
            else { 
                // set Mac address of received packet
                hdr.ethernet.srcAddr = 0x080000000100;
                hdr.ethernet.dstAddr = 0x080000000111;

                if (hdr.kvs.pingpong == 1) {
                    // pong packets from dbs
                    bit<32> pong_cnt = 0;
                    if (standard_metadata.ingress_port == 2) {
                        pingpong_1.read(pong_cnt, 1);
                        pingpong_1.write(1, pong_cnt+1);

                    } else if (standard_metadata.ingress_port == 3) {
                        pingpong_2.read(pong_cnt, 1);
                        pingpong_2.write(1, pong_cnt+1);
                    }
                } 
                if (hdr.kvs.pingpong == 2)  // it's a pong packet from different db
                    mark_to_drop(standard_metadata);
                else
                    standard_metadata.egress_spec = 1;
                
                // mark packet to drop
                if (standard_metadata.ingress_port == 4 && 
                    ((db1 != 4 && (hdr.kvs.first <= 512)) || 
                    (db2 != 4 && (hdr.kvs.first > 512))))
                    mark_to_drop(standard_metadata);
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
