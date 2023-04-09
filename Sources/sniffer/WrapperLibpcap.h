#ifndef __WRAPPER_LIBPCAP_H__
#define __WRAPPER_LIBPCAP_H__ 1

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <iostream>
#include <fstream>
#include <string>
#include <string.h>
#include <csignal>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/ip6.h>
#include <netinet/icmp6.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <linux/if_packet.h>
#include <linux/dccp.h>
#include <netinet/igmp.h>
#include <arpa/inet.h>
#include <netinet/ip_icmp.h> 
#include <netinet/if_ether.h> // includes net/ethernet.h 
#include <pcap.h> // if this gives you an error try pcap/pcap.h
#include <sys/socket.h>

#include "NetworkPacket.h"
#include "Utils.h"

#define PROMISCUOUS_MODE            1
#define ETHERTYPE_WAKE_ON_LAN       0x0842
#define ETHERTYPE_ATA               0x88A2
#define LOG_VERBOSE                 1

///////////////////////////////////////////////////////////////////////////////
// GLOBAL VARIABLES
///////////////////////////////////////////////////////////////////////////////

extern volatile long int maxNumberOfPackets;
extern volatile double timeout;
extern volatile unsigned int packetCounter;
extern volatile sig_atomic_t stopCapture;
extern struct timeval firstTimeStamp;
extern volatile struct timeval currentTimeStamp;
extern volatile TSQueue<NetworkPacket*>* packetsQueue;

///////////////////////////////////////////////////////////////////////////////
// HEADERS
///////////////////////////////////////////////////////////////////////////////

struct rarp_header {
    uint16_t htype;
    uint16_t ptype;
    uint8_t hlen;
    uint8_t plen;
    uint16_t oper;
    uint8_t sha[6];
    uint8_t spa[4];
    uint8_t tha[6];
    uint8_t tpa[4];
};

struct sctp_header {
    uint16_t source_port;
    uint16_t destination_port;
    uint32_t verification_tag;
    uint32_t checksum;
};

// Loopback header
struct loopback_header {
    unsigned char packet_type;
    unsigned char flags;
    unsigned short protocol_type;
};

// ??
struct wol_header {
    uint8_t dest_mac[6];
    uint8_t src_mac[6];
    uint8_t magic_packet[6];
    uint8_t payload[0]; // variable-length payload
};

struct ata_header
{
    unsigned char version;
    unsigned char flags;
    unsigned char major[2];
    unsigned char minor;
    unsigned char command;
    unsigned char tag[4];
};


const char LOOPBACK_NULL_ENCAPSULATION[] = {0x00, 0x00, 0x00, 0x02};


///////////////////////////////////////////////////////////////////////////////
// CAPTURE FUNCTIONS
///////////////////////////////////////////////////////////////////////////////

void start_capture(const char* interfaceName, unsigned int timeout, unsigned int maxNumberOfPackets);
void read_pcap_file(const char* filename);
void pcap_live_capture(const char* etherInterface);
void signal_handler(int signum);
void clean_capture();


///////////////////////////////////////////////////////////////////////////////
// LINK LAYER PARSES
///////////////////////////////////////////////////////////////////////////////

void process_ethernet_frame(u_char* user, const struct pcap_pkthdr* framw_header, const u_char* frame);


///////////////////////////////////////////////////////////////////////////////
// TRANSPORT LAYER PARSES
///////////////////////////////////////////////////////////////////////////////

// Internet Control Message Protocol.
void process_icmp_segment(const struct icmphdr* icmp_hdr, const u_char* icmp_segment, NetworkPacket* netPkt);
// Transmission Control Protocol. 
void process_tcp_segment(const struct tcphdr* tcp_hdr, const u_char* tcp_segment, NetworkPacket* netPkt);
// User Datagram Protocol. 
void process_udp_segment(const struct udphdr* udp_hdr, const u_char* udp_segment, NetworkPacket* netPkt);
// Stream Control Transmission Protocol. 
void process_sctp_segment(const struct sctp_header* sctp_hdr, const u_char* sctp_segment, NetworkPacket* netPkt);
// ICMPv6
void process_icmpv6_segment(const struct icmp6_hdr* icmpv6_hd, const u_char* icmpv6_segment, NetworkPacket* netPkt);
// Datagram Congestion Control Protocol. 
void process_dccp_segment(const struct dccp_hdr* dccp_hdr, const u_char* dccp_segment, NetworkPacket* netPkt);
void process_igmp_segment(const struct igmp* igmp_hdr, const u_char* igmp_segment, NetworkPacket* netPkt);

///////////////////////////////////////////////////////////////////////////////
// NETWORK LAYER PARSES
///////////////////////////////////////////////////////////////////////////////

void process_ipv4_packet(struct iphdr* ip_hdr, const u_char* packet, NetworkPacket* netPkt);
void process_ipv6_packet(struct ip6_hdr* ip6_hdr, const u_char* packet, NetworkPacket* netPkt);
void process_rarp_packet(const struct rarp_header* rarp_hdr, const u_char* rarp_packet, NetworkPacket* netPkt);
void process_arp_packet(const struct ether_arp* arp_header, const u_char* arp_packet, NetworkPacket* netPkt);
void process_loopback_packet(const struct loopback_header* loop_header, const u_char* loop_packet, NetworkPacket* netPkt);
void process_wol_packet(const struct wol_header* wol_header, const u_char* wol_packet, NetworkPacket* netPkt);
void process_ata_packet(const struct ata_header* ata_hd, const u_char* ata_packet, NetworkPacket* netPkt);

///////////////////////////////////////////////////////////////////////////////
// Application LAYER PARSES
///////////////////////////////////////////////////////////////////////////////



#endif // __WRAPPER_LIBPCAP_H__ 

