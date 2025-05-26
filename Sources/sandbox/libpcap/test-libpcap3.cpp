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
#include <netinet/if_ether.h> /* includes net/ethernet.h */
#include <pcap.h> /* if this gives you an error try pcap/pcap.h */
#include <sys/socket.h>

#define PROMISCUOUS_MODE            1
#define ETHERTYPE_WAKE_ON_LAN       0x0842
#define ETHERTYPE_ATA               0x88A2

#define LOG_VERBOSE                 1

// global variables
struct timeval firstTimeStamp = {.tv_sec = 0, .tv_usec = 0};
unsigned int packetCounter = 0;
volatile sig_atomic_t stop_capture = 0;

void test_pcap_capture();
void start_capture(const char* interfaceName);
void read_pcap_file(const char* filename);
void pcap_live_capture(const char* etherInterface);
void signalHandler(int signum);

///////////////////////////////////////////////////////////////////////////////
// LINK LAYER PARSES
///////////////////////////////////////////////////////////////////////////////

void process_ethernet_frame(u_char* user, const struct pcap_pkthdr* framw_header, const u_char* frame);
double calculateTimestampInSec(const struct timeval t0, const struct timeval currentTimestamp);

///////////////////////////////////////////////////////////////////////////////
// TRANSPORT LAYER PARSES
///////////////////////////////////////////////////////////////////////////////

// Internet Control Message Protocol.
void process_icmp_segment(const struct icmphdr* icmp_hdr, const u_char* icmp_segment);
// Transmission Control Protocol. 
void process_tcp_segment(const struct tcphdr* tcp_hdr, const u_char* tcp_segment);
// User Datagram Protocol. 
void process_udp_segment(const struct udphdr* udp_hdr, const u_char* udp_segment);
// Stream Control Transmission Protocol. 
void process_sctp_segment(const struct sctp_header* sctp_hdr, const u_char* sctp_segment);
// ICMPv6
void process_icmpv6_segment(const struct icmp6_hdr* icmpv6_hd, const u_char* icmpv6_segment);
// Datagram Congestion Control Protocol. 
void process_dccp_segment(const struct dccp_hdr* dccp_hdr, const u_char* dccp_segment);
void process_igmp_segment(const struct igmp* igmp_hdr, const u_char* igmp_segment);

///////////////////////////////////////////////////////////////////////////////
// NETWORK LAYER PARSES
///////////////////////////////////////////////////////////////////////////////

void process_ipv4_packet(struct iphdr* ip_hdr, const u_char* packet);
void process_ipv6_packet(struct ip6_hdr* ip6_hdr, const u_char* packet);
void process_rarp_packet(const struct rarp_header* rarp_hdr, const u_char* rarp_packet);
void process_arp_packet(const struct ether_arp* arp_header, const u_char* arp_packet);
void process_loopback_packet(const struct loopback_header* loop_header, const u_char* loop_packet);
void process_wol_packet(const struct wol_header* wol_header, const u_char* wol_packet);
void process_ata_packet(const struct ata_header* ata_hd, const u_char* ata_packet);

///////////////////////////////////////////////////////////////////////////////
// Application LAYER PARSES
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

int main(int argc, char* argv[])
{
    bool test01 = true;
    if (test01) test_pcap_capture();

    return 0;
}

void test_pcap_capture()
{
    printf("oi\n");
    ///start_capture("eth0");
    start_capture("../../Pcap/SkypeIRC.cap.pcap");
    start_capture("../../Pcap/v6-http.cap.pcap");
    start_capture("../../Pcap/arp_pcap.pcapng.cap.pcap");
    start_capture("../../Pcap/mysql_complete.pcap");
    start_capture("../../Pcap/telnet-cooked.pcap");
    start_capture("../../Pcap/snmp_usm.pcap");
    start_capture("../../Pcap/wol.pcap");
    // start_capture("../../Pcap/bigFlows.pcap");
    // read_pcap_file("../../Pcap/http_PPI.pcap"); // wifi
}

void start_capture(const char* interfaceName)
{
    if(access(interfaceName, F_OK ) != -1 ) 
    {
        // file exists, read pcap
        read_pcap_file(interfaceName);
    } 
    else 
    {
        // file does not exist, assume it is an interface
        pcap_live_capture(interfaceName);
    }
}

void read_pcap_file(const char* filename) 
{
    firstTimeStamp = {.tv_sec = 0, .tv_usec = 0};
    packetCounter = 0;
    printf("************************************************************\n");
    printf("** %s\n", filename);
    printf("************************************************************\n");
    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t* pcap_handle = pcap_open_offline(filename, errbuf);
    if (pcap_handle == nullptr) 
    {
        std::cerr << "Error opening pcap file: " << errbuf << std::endl;
        return;
    }

    pcap_loop(pcap_handle, 0, process_ethernet_frame, nullptr);
    pcap_close(pcap_handle);
    printf("\n");
    printf("** %s completed\n", filename);
}


void pcap_live_capture(const char* etherInterface)
{
    char *dev;
    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t *handle;

    printf("************************************************************\n");
    printf("** Starting live capture @ %s\n", etherInterface);
    printf("************************************************************\n");
    // Find a suitable network interface to capture packets from
    dev = pcap_lookupdev(errbuf);
    if (dev == NULL) 
    {
        fprintf(stderr, "pcap_lookupdev() failed: %s\n", errbuf);
        return;
    }

    // Open the network interface for packet capture
    handle = pcap_open_live(dev, BUFSIZ, 1, 1000, errbuf);
    if (handle == NULL) 
    {
        fprintf(stderr, "pcap_open_live() failed: %s\n", errbuf);
        return;
    }

    // Register a signal handler for SIGINT
    printf("Register a signal handler for SIGINT\n");
    signal(SIGINT, signalHandler);

    // Start capturing packets
    printf("Start capturing packets\n");
    while (stop_capture != 1) 
    {
        struct pcap_pkthdr frame_header;
        const u_char *frame = pcap_next(handle, &frame_header);
        process_ethernet_frame(NULL, &frame_header, frame);
        if (frame == NULL) 
        {
            continue;
        }
    }

    // Get statistics
    struct pcap_stat stats;
    if (pcap_stats(handle, &stats) == -1) 
    {
        fprintf(stderr, "Failed to get statistics: %s\n", pcap_geterr(handle));
        return;
    }

    // Print statistics
    printf("Packets received: %d\n", stats.ps_recv);
    printf("Packets dropped by kernel: %d\n", stats.ps_drop);
    printf("Packets dropped by interface: %d\n", stats.ps_ifdrop);


    // Clean up
    pcap_close(handle);

    return;
}

void signalHandler(int signum)
{
    stop_capture = 1;
}


void process_ethernet_frame(u_char* user, const struct pcap_pkthdr* frame_header, const u_char* frame)
{
#ifndef LOG_VERBOSE
    // printf(".");
#endif
    // Process the frame here
    const struct ether_header* ether_hdr = (const struct ether_header*)frame;
    if(firstTimeStamp.tv_sec == 0)
    {
        firstTimeStamp.tv_sec = frame_header->ts.tv_sec;
        firstTimeStamp.tv_usec = frame_header->ts.tv_usec;
    }
    int frame_len = frame_header->len;
    packetCounter++;
#ifdef LOG_VERBOSE
    printf("[ETHERNET FRAME] No.:%u Timestamp [%f] EtherType:%X, FrameLen:%d ", packetCounter, calculateTimestampInSec(firstTimeStamp, frame_header->ts), ether_hdr->ether_type, frame_len);
#endif

    // Check if it is an IP packet
    if (ntohs(ether_hdr->ether_type) == ETHERTYPE_IP) 
    {
        u_char* ip_packet = (u_char*)(frame + sizeof(struct ether_header));
        struct iphdr* ip_hdr = (struct iphdr*)(ip_packet);
        process_ipv4_packet(ip_hdr, ip_packet);
    }
    else if (ntohs(ether_hdr->ether_type) == ETHERTYPE_IPV6) 
    {
        u_char* ip6_packet = (u_char*)(frame + sizeof(struct ether_header));
        struct ip6_hdr* ip_hdr = (struct ip6_hdr*)(ip6_packet);
        process_ipv6_packet(ip_hdr, ip6_packet);
    }
    // Check if it is an ARP packet
    else if (ntohs(ether_hdr->ether_type) == ETHERTYPE_ARP) 
    {
        u_char* arp_packet = (u_char*)(frame + sizeof(struct ether_header));
        const struct ether_arp* arp_header = (const struct ether_arp*)(arp_packet);
        process_arp_packet(arp_header, arp_packet);
    }
    // Check if it is an REVERSE ARP packet
    else if (ntohs(ether_hdr->ether_type) == ETHERTYPE_REVARP) 
    {
#ifdef LOG_VERBOSE
        printf("RARP\n");
#endif
        u_char* rarp_packet = (u_char*)(frame + sizeof(struct ether_header));
        struct rarp_header* rarp_hdr = (struct rarp_header*)(rarp_packet);
        process_rarp_packet(rarp_hdr, rarp_packet);
    }
    else if (ntohs(ether_hdr->ether_type) == ETHERTYPE_WAKE_ON_LAN) 
    {
        u_char* wol_packet = (u_char*)(frame + sizeof(struct ether_header));
        const struct wol_header* wol_header = (const struct wol_header*)(wol_packet);

        process_wol_packet(wol_header, wol_packet);
    }
    else if(ntohs(ether_hdr->ether_type) == ETHERTYPE_LOOPBACK) 
    {
        u_char* loop_packet = (u_char*)(frame + sizeof(struct ether_header));
        const struct loopback_header* loop_header = (const struct loopback_header*)(loop_packet);
        process_loopback_packet(loop_header, loop_packet);
    }
    else if(ntohs(ether_hdr->ether_type) == ETHERTYPE_ATA)
    {
        u_char* ata_packet = (u_char*)(frame + sizeof(struct ether_header));
        const struct ata_header* ata_header = (const struct ata_header*)(ata_packet);
        process_ata_packet(ata_header, ata_packet);
    }
    // NULL/Loopback Encapsulation if packet_data starts with 00 00 00 02
    else if ( memcmp(frame, LOOPBACK_NULL_ENCAPSULATION, 4) == 0 )
    {
        u_char* ip_packet = (u_char*)(frame + sizeof(LOOPBACK_NULL_ENCAPSULATION));
        struct iphdr* ip_hdr = (struct iphdr*)(ip_packet);
        process_ipv4_packet(ip_hdr, ip_packet);
    }
    else
    {

#ifdef LOG_VERBOSE
        printf("UNKNOWN FRAME %X\n", ntohs(ether_hdr->ether_type));
#else
        printf("[ETHERNET FRAME] No.:%u Timestamp [%f] EtherType:%X, FrameLen:%d ", packetCounter, calculateTimestampInSec(firstTimeStamp, frame_header->ts), ether_hdr->ether_type, frame_len);
        printf("UNKNOWN FRAME %X\n", ntohs(ether_hdr->ether_type));
#endif
    }
}

double calculateTimestampInSec(const struct timeval t0, const struct timeval currentTimestamp) 
{
    double timestampInSeconds = (currentTimestamp.tv_sec - t0.tv_sec) + ((currentTimestamp.tv_usec - t0.tv_usec) / 1000000.0);
    return timestampInSeconds;
}

void process_ipv4_packet(struct iphdr* ip_hdr, const u_char* packet)
{
#ifdef LOG_VERBOSE
    printf("[IP PACKET] version:%d, ihl:%d, tot_len:%d, ttl:%d, daddr:%X, saddr:%X ", ip_hdr->version, ip_hdr->ihl, ip_hdr->tot_len, ip_hdr->ttl, ntohl(ip_hdr->daddr), ntohl(ip_hdr->saddr));
#endif
    if (ip_hdr->protocol == IPPROTO_IP || ip_hdr->protocol == IPPROTO_TCP)
    {
        const struct tcphdr* tcp_hdr = (const struct tcphdr*)(packet + (ip_hdr->ihl * 4));
        const u_char* tcp_segment = (const u_char*) (packet + sizeof(tcp_hdr));
        process_tcp_segment(tcp_hdr, tcp_segment);
    } 
    else if(ip_hdr->protocol == IPPROTO_UDP) 
    {
        const struct udphdr* udp_hdr = (const struct udphdr*)(packet  + (ip_hdr->ihl * 4));
        const u_char* udp_segment = (const u_char*) (packet + sizeof(udp_hdr));
        process_udp_segment(udp_hdr, udp_segment);
    }
    else if (ip_hdr->protocol == IPPROTO_ICMP) 
    {
        const struct icmphdr* icmp_hdr = (const struct icmphdr*)(packet + (ip_hdr->ihl * 4) );
        const u_char* icmp_segment = (const u_char*) (packet + sizeof(icmp_hdr));
        process_icmp_segment(icmp_hdr, icmp_segment);
    }
    else if (ip_hdr->protocol == IPPROTO_IGMP) 
    {
        const struct igmp* igmp_hdr = (const struct igmp*)(packet + (ip_hdr->ihl * 4) );
        const u_char* igmp_segment = (const u_char*) (packet + sizeof(igmp_hdr));
        process_igmp_segment(igmp_hdr, igmp_segment);
    }
    else if (ip_hdr->protocol == IPPROTO_SCTP) 
    {
        struct sctp_header* sctp_hdr = (struct sctp_header*)(packet + (ip_hdr->ihl * 4));
        const u_char* sctp_segment = (const u_char*) (packet + sizeof(sctp_hdr));
        process_sctp_segment(sctp_hdr, sctp_segment);
    }
    else if (ip_hdr->protocol == IPPROTO_DCCP) 
    {
        const u_char* dccp_packet = (u_char*)(ip_hdr + 1);
        struct dccp_hdr* dccp_hdr = (struct dccp_hdr*)dccp_packet;
        process_dccp_segment(dccp_hdr, dccp_packet);
    }
    else
    {
#ifdef LOG_VERBOSE
        printf("*********** UNKNOWN PACKET %X\n", ip_hdr->protocol);
#else
        printf("[IPV4 PACKET] [UNKNOWN TRANSPORT PROTOCOL %X on packet No.:%u]\n", ip_hdr->protocol, packetCounter);
#endif        
    }

}

void process_ipv6_packet(struct ip6_hdr* ip_hdr, const u_char* packet)
{
#ifdef LOG_VERBOSE
    char src_str[INET6_ADDRSTRLEN];
    char dst_str[INET6_ADDRSTRLEN];
    inet_ntop(AF_INET6, &(ip_hdr->ip6_src), src_str, INET6_ADDRSTRLEN);
    inet_ntop(AF_INET6, &(ip_hdr->ip6_dst), dst_str, INET6_ADDRSTRLEN);
    printf("[IPv6 PACKET] version:%d,  flow_label:%d, payload_len:%d, next_header:%d, hop_limit:%d, saddr:%s, daddr:%s", 
           ip_hdr->ip6_vfc, ip_hdr->ip6_flow, ntohs(ip_hdr->ip6_plen), ip_hdr->ip6_nxt, ip_hdr->ip6_hlim, src_str, dst_str);
#endif
    if (ip_hdr->ip6_nxt == IPPROTO_IP || ip_hdr->ip6_nxt == IPPROTO_TCP)
    {
        const struct tcphdr* tcp_hdr = (const struct tcphdr*)(packet + sizeof(struct ip6_hdr));
        const u_char* tcp_segment = (const u_char*) (packet + sizeof(struct ip6_hdr) + sizeof(struct tcphdr));
        process_tcp_segment(tcp_hdr, tcp_segment);
    } 
    else if (ip_hdr->ip6_nxt == IPPROTO_UDP) 
    {
        const struct udphdr* udp_hdr = (const struct udphdr*)(packet  + sizeof(struct ip6_hdr));
        const u_char* udp_segment = (const u_char*) (packet + sizeof(struct ip6_hdr) + sizeof(struct udphdr));
        process_udp_segment(udp_hdr, udp_segment);
    }
    else if (ip_hdr->ip6_nxt == IPPROTO_ICMPV6) 
    {
        const struct icmp6_hdr* icmp_hd = (const struct icmp6_hdr*)(packet + sizeof(struct ip6_hdr));
        const u_char* icmp_segment = (const u_char*) (packet + sizeof(struct ip6_hdr) + sizeof(struct icmp6_hdr));
        process_icmpv6_segment(icmp_hd, icmp_segment);
    }
    else if (ip_hdr->ip6_nxt == IPPROTO_IGMP) 
    {
        const struct igmp* igmp_hdr = (const struct igmp*)(packet +  + sizeof(struct ip6_hdr) );
        const u_char* igmp_segment = (const u_char*) (packet + sizeof(igmp_hdr));
        process_igmp_segment(igmp_hdr, igmp_segment);
    }    
    else if (ip_hdr->ip6_nxt == IPPROTO_SCTP) 
    {
        struct sctp_header* sctp_hdr = (struct sctp_header*)(packet + sizeof(struct ip6_hdr));
        const u_char* sctp_segment = (const u_char*) (packet + sizeof(struct ip6_hdr) + sizeof(struct sctp_header));
        process_sctp_segment(sctp_hdr, sctp_segment);
    }
    else if (ip_hdr->ip6_nxt == IPPROTO_DCCP) 
    {
        const u_char* dccp_packet = (u_char*)(ip_hdr + 1);
        struct dccp_hdr* dccp_hdr = (struct dccp_hdr*)dccp_packet;
        process_dccp_segment(dccp_hdr, dccp_packet);
    }
    else
    {
#ifdef LOG_VERBOSE
        printf("*********** UNKNOWN PACKET %X\n", ntohs(ip_hdr->ip6_nxt));
#else
        printf("\n[IPV6 PACKET] PROTOCOL [UNKNOWN TRANSPORT PROTOCOL %X on packet No.:%u]\n", ip_hdr->ip6_nxt, packetCounter);
#endif        
    }    
}

void process_igmp_segment(const struct igmp* igmp_hdr, const u_char* igmp_segment) 
{
    uint8_t igmp_type = igmp_hdr->igmp_type;
    uint8_t igmp_code = igmp_hdr->igmp_code;
    uint16_t igmp_cksum = ntohs(igmp_hdr->igmp_cksum);
    uint32_t igmp_group = ntohl(igmp_hdr->igmp_group.s_addr);
#ifdef LOG_VERBOSE
    printf("IGMP: type:%u, code:%u, checksum:%u, group:%s\n", igmp_type, igmp_code, igmp_cksum, inet_ntoa(*(struct in_addr*)&igmp_group));
#endif
}

void process_tcp_segment(const struct tcphdr* tcp_hdr, const u_char* tcp_segment)
{
#ifdef LOG_VERBOSE
    // Print TCP header information
    printf("[TCP SEGMENT] ");
    printf("src_port:%d, ", ntohs(tcp_hdr->source));
    printf("dst_port:%d, ", ntohs(tcp_hdr->dest));
    printf("seq_num:%u, ", ntohl(tcp_hdr->seq));
    printf("ack_num:%u, ", ntohl(tcp_hdr->ack_seq));
    printf("data_offset:%d, ", tcp_hdr->doff);
    printf("urg_flag:%d, ", tcp_hdr->urg);
    printf("ack_flag:%d, ", tcp_hdr->ack);
    printf("psh_flag:%d, ", tcp_hdr->psh);
    printf("rst_flag:%d, ", tcp_hdr->rst);
    printf("syn_flag:%d, ", tcp_hdr->syn);
    printf("fin_flag:%d\n", tcp_hdr->fin);    
#endif
}


void process_udp_segment(const struct udphdr* udp_hdr, const u_char* udp_segment)
{
#ifdef LOG_VERBOSE
    printf("[UDP SEGMENT]");
    printf("source_port:%u, ", ntohs(udp_hdr->uh_sport));
    printf("dest_port:%u, ", ntohs(udp_hdr->uh_dport));
    printf("length:%u\n", ntohs(udp_hdr->uh_ulen));
#endif
}


void process_icmp_segment(const struct icmphdr* icmp_hdr, const u_char* icmp_segment)
{
#ifdef LOG_VERBOSE
    printf("[ICMP SEGMENT] type:%d, code:%d, checksum:%d\n",
            icmp_hdr->type, icmp_hdr->code, ntohs(icmp_hdr->checksum));    
#endif            
} 


void process_sctp_segment(const struct sctp_header* sctp_hdr, const u_char* sctp_segment) 
{
    uint16_t src_port = ntohs(sctp_hdr->source_port);
    uint16_t dst_port = ntohs(sctp_hdr->destination_port);
    uint32_t verification_tag = ntohl(sctp_hdr->verification_tag);
    uint32_t checksum = ntohl(sctp_hdr->checksum);
#ifdef LOG_VERBOSE
    printf("[SCTP PACKET] Source Port: %u, Destination Port: %u, Verification Tag: %u, Checksum: %u\n", src_port, dst_port, verification_tag, checksum);
#endif
}

void process_icmpv6_segment(const icmp6_hdr *icmpv6_hd, const u_char *icmpv6_segment)
{
#ifdef LOG_VERBOSE
    printf("[ICMPv6 SEGMENT] type:%d, code:%d, checksum:%d\n",
            icmpv6_hd->icmp6_type, icmpv6_hd->icmp6_code, ntohs(icmpv6_hd->icmp6_cksum));
#endif
}

void process_dccp_segment(const struct dccp_hdr* dccp_hdr, const u_char* dccp_segment) 
{
    uint16_t src_port = ntohs(dccp_hdr->dccph_sport);
    uint16_t dst_port = ntohs(dccp_hdr->dccph_dport);
    uint32_t dccp_ccval = ntohl(dccp_hdr->dccph_ccval);
    uint16_t dccp_chksum = ntohs(dccp_hdr->dccph_checksum);
    uint32_t dccp_cscov = ntohl(dccp_hdr->dccph_cscov);
    uint32_t dccp_seq = ntohl(dccp_hdr->dccph_seq);
    uint32_t dccp_seq2 = ntohl(dccp_hdr->dccph_seq2);
    uint32_t dccp_doff = ntohl(dccp_hdr->dccph_doff);
    uint32_t dccp_type = ntohl(dccp_hdr->dccph_type);
#ifdef LOG_VERBOSE
    printf("[DCCP PACKET] src_port:%u, dst_port:%u, dccp_seq:%u, dccp_ccval:%u, dccp_chksum:%u, dccp_cscov:%u, dccp_seq2:%u, dccp_doff:%u, dccp_type:%u\n",
           src_port, dst_port, dccp_seq, dccp_ccval, dccp_chksum, dccp_cscov, dccp_seq2, dccp_doff, dccp_type);
#endif
}

void process_arp_packet(const struct ether_arp* arp_header, const u_char* arp_packet)
{
    //const struct ether_arp* arp_header = (const struct ether_arp*)(frame + sizeof(struct ether_header));
    char src_mac[18];
    char dst_mac[18];
    char src_ip[INET_ADDRSTRLEN];
    char dst_ip[INET_ADDRSTRLEN];

    sprintf(src_mac, "%02x:%02x:%02x:%02x:%02x:%02x", arp_header->arp_sha[0], arp_header->arp_sha[1], arp_header->arp_sha[2], arp_header->arp_sha[3], arp_header->arp_sha[4], arp_header->arp_sha[5]);
    sprintf(dst_mac, "%02x:%02x:%02x:%02x:%02x:%02x", arp_header->arp_tha[0], arp_header->arp_tha[1], arp_header->arp_tha[2], arp_header->arp_tha[3], arp_header->arp_tha[4], arp_header->arp_tha[5]);
    inet_ntop(AF_INET, arp_header->arp_spa, src_ip, INET_ADDRSTRLEN);
    inet_ntop(AF_INET, arp_header->arp_tpa, dst_ip, INET_ADDRSTRLEN);
#ifdef LOG_VERBOSE
    std::cout << "[ARP packet] " << " MACsrc:" << src_mac <<  ", MACdst: " << dst_mac << 
                                     ", IPsrc: " << src_ip << ", IPdst: " << dst_ip 
              << std::endl;
#endif              
}

void process_rarp_packet(const struct rarp_header* rarp_hdr, const u_char* rarp_packet)
{
#ifdef LOG_VERBOSE
    // Print RARP header informatio
    printf("[RARP PACKET]");
    printf("  Sender MAC: %02x:%02x:%02x:%02x:%02x:%02x,",
           rarp_hdr->sha[0], rarp_hdr->sha[1], rarp_hdr->sha[2],
           rarp_hdr->sha[3], rarp_hdr->sha[4], rarp_hdr->sha[5]);
    printf("  Sender IP: %d.%d.%d.%d,",
           rarp_hdr->spa[0], rarp_hdr->spa[1], rarp_hdr->spa[2], rarp_hdr->spa[3]);
    printf("  Target MAC: %02x:%02x:%02x:%02x:%02x:%02x,",
           rarp_hdr->tha[0], rarp_hdr->tha[1], rarp_hdr->tha[2],
           rarp_hdr->tha[3], rarp_hdr->tha[4], rarp_hdr->tha[5]);
    printf("  Target IP: %d.%d.%d.%d\n",
           rarp_hdr->tpa[0], rarp_hdr->tpa[1], rarp_hdr->tpa[2], rarp_hdr->tpa[3]);
#endif
}

void process_loopback_packet(const struct loopback_header* loop_header, const u_char* loop_packet) 
{
#ifdef LOG_VERBOSE
    printf("[LOOPBACK PACKET] ");
    printf("packet_type:%02x, flags:%02x, protocol_type:%02x\n", loop_header->packet_type, loop_header->flags, loop_header->protocol_type);
#endif
}


void process_wol_packet(const struct wol_header* wol_header, const u_char* wol_packet)
{
#ifdef LOG_VERBOSE
    printf("[WOL PACKET]");
    printf(" SRC MAC: %02x:%02x:%02x:%02x:%02x:%02x ",
           wol_header->src_mac[0], wol_header->src_mac[1], wol_header->src_mac[2],
           wol_header->src_mac[3], wol_header->src_mac[4], wol_header->src_mac[5]);
    printf(" DST MAC: %02x:%02x:%02x:%02x:%02x:%02x ",
           wol_header->dest_mac[0], wol_header->dest_mac[1], wol_header->dest_mac[2],
           wol_header->dest_mac[3], wol_header->dest_mac[4], wol_header->dest_mac[5]);
    printf(" magic_packet: %02x:%02x:%02x:%02x:%02x:%02x \n",
           wol_header->magic_packet[0], wol_header->magic_packet[1], wol_header->magic_packet[2],
           wol_header->magic_packet[3], wol_header->magic_packet[4], wol_header->magic_packet[5]);
#endif
}

void process_ata_packet(const ata_header *ata_hd, const u_char *ata_packet)
{
#ifdef LOG_VERBOSE
    printf("[ATA PACKET] version=0x%02x, flags=0x%02x, major=0x%02x%02x, minor=0x%02x, command=0x%02x, tag=0x%02x%02x%02x%02x\n", ata_hd->version, ata_hd->flags, ata_hd->major[0], ata_hd->major[1], ata_hd->minor, ata_hd->command, ata_hd->tag[0], ata_hd->tag[1], ata_hd->tag[2], ata_hd->tag[3]);
#endif
}

//

