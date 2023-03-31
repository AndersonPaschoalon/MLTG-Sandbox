#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <iostream>
#include <fstream>
#include <string>
#include <string.h>

#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
// #include <netinet/dccp.h>
// #include <netinet/sctp.h>

#include <netinet/ip_icmp.h> 
#include <netinet/if_ether.h> /* includes net/ethernet.h */
#include <pcap.h> /* if this gives you an error try pcap/pcap.h */
#include <sys/socket.h>

#define PROMISCUOUS_MODE            1
#define ETHERTYPE_WAKE_ON_LAN       0x0842
#define LOG_VERBOSE                 1

// global variables
struct timeval firstTimeStamp = {.tv_sec = 0, .tv_usec = 0};
unsigned int packetCounter = 0;

// read offline packets
void test_pcap_file();
void read_pcap_file(const char* filename);


// LINK LAYER PARSES
void process_ethernet_frame(u_char* user, const struct pcap_pkthdr* framw_header, const u_char* frame);
double calculateTimestampInSec(const struct timeval t0, const struct timeval currentTimestamp);

// TRANSPORT LAYER PARSES

void process_icmp_segment(const struct icmphdr* icmp_hdr, const u_char* icmp_segment);
void process_tcp_segment(const struct tcphdr* tcp_hdr, const u_char* tcp_segment);
void process_udp_segment(const struct udphdr* udp_hdr, const u_char* udp_segment);
void process_sctp_segment(struct sctp_header* sctp_hdr, const u_char* sctp_segment);


// NETWORK LAYER PARSES
void process_ipv4_packet(struct iphdr* ip_hdr, const u_char* frame);
void process_ipv6_packet(struct iphdr* ip_hdr, const u_char* frame);
void process_rarp_packet(struct rarp_header*, u_char* rarp_packet);
void process_arp_packet(const struct ether_arp* arp_header, u_char* arp_packet);
void process_loopback_packet(const u_char* frame);
void process_wol_packet(const struct ether_header *ether_hdr, const u_char *frame) ;


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
    /* more fields can be added here */
};

const char LOOPBACK_NULL_ENCAPSULATION[] = {0x00, 0x00, 0x00, 0x02};

int main(int argc, char* argv[])
{
    bool test01 = true;
    if (test01) test_pcap_file();

    return 0;
}

void test_pcap_file()
{

    read_pcap_file("../../Pcap/arp_pcap.pcapng.cap.pcap");
    read_pcap_file("../../Pcap/mysql_complete.pcap");
    // read_pcap_file("../../Pcap/http_PPI.pcap");
    read_pcap_file("../../Pcap/telnet-cooked.pcap");
    read_pcap_file("../../Pcap/SkypeIRC.cap.pcap");
    read_pcap_file("../../Pcap/snmp_usm.pcap");
    read_pcap_file("../../Pcap/bigFlows.pcap");

    
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
    printf("** %s completed\n", filename);
}


void process_ethernet_frame(u_char* user, const struct pcap_pkthdr* frame_header, const u_char* frame)
{
#ifndef LOG_VERBOSE
    //printf(".");
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
#ifdef LOG_VERBOSE
        printf("WOL\n");
#endif
        process_wol_packet(ether_hdr, frame);
    }
    else if(ntohs(ether_hdr->ether_type) == ETHERTYPE_LOOPBACK) 
    {
        process_loopback_packet(frame);
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
        printf("UNKNOWN PACKET %X\n", ntohs(ether_hdr->ether_type));
#else
    printf("[ETHERNET FRAME] No.:%u Timestamp [%f] EtherType:%X, FrameLen:%d ", packetCounter, calculateTimestampInSec(firstTimeStamp, frame_header->ts), ether_hdr->ether_type, frame_len);

        printf("UNKNOWN PACKET %X\n", ntohs(ether_hdr->ether_type));
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
    if(ip_hdr->protocol == IPPROTO_IP || ip_hdr->protocol == IPPROTO_TCP)
    {
        // Calculate TCP header pointer based on IP header length
        // int tcp_hdr_length = (ip_hdr->ihl * 4) + sizeof(struct tcphdr);
        const struct tcphdr* tcp_hdr = (const struct tcphdr*)(packet + (ip_hdr->ihl * 4));
        const u_char* tcp_segment = (const u_char*) (packet + sizeof(tcp_hdr));
        // Process TCP segment
        process_tcp_segment(tcp_hdr, tcp_segment);
    } 
    else if (ip_hdr->protocol == IPPROTO_UDP) 
    {
        // const struct udphdr* udp_hdr  = (const struct udphdr*)(packet + sizeof(struct ether_header) + sizeof(struct ip));
        const struct udphdr* udp_hdr = (const struct udphdr*)(packet  + (ip_hdr->ihl * 4));
        const u_char* udp_segment = (const u_char*) (packet + sizeof(udp_hdr));
        process_udp_segment(udp_hdr, udp_segment);
    }
    else if (ip_hdr->protocol == IPPROTO_ICMP) 
    {
        // const struct icmphdr* icmp_hdr = (const struct icmphdr*)(packet + sizeof(struct iphdr));
        const struct icmphdr* icmp_hdr = (const struct icmphdr*)(packet + (ip_hdr->ihl * 4) );
        const u_char* icmp_segment = (const u_char*) (packet + sizeof(icmp_hdr));
        process_icmp_segment(icmp_hdr, icmp_segment);
    }
    else{
        // struct sctp_header* sctp_hdr = (struct sctp_header*)(packet + sizeof(struct ip));
        struct sctp_header* sctp_hdr = (struct sctp_header*)(packet + (ip_hdr->ihl * 4));
        const u_char* sctp_segment = (const u_char*) (packet + sizeof(sctp_hdr));
        process_sctp_segment(sctp_hdr, sctp_segment);
    }
}

void process_ipv6_packet(struct iphdr* ip_hdr, const u_char* frame)
{
    print("todo");
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

/*
void process_tcp_segment(const u_char* packet) {
    // Cast packet to IP header
    const struct iphdr* ip_hdr = (const struct iphdr*)(packet);

    // Calculate TCP header pointer based on IP header length
    int tcp_hdr_length = (ip_hdr->ihl * 4) + sizeof(struct tcphdr);
    const struct tcphdr* tcp_hdr = (const struct tcphdr*)(packet + (ip_hdr->ihl * 4));

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
}
*/

/**
void process_udp_segment(const u_char* packet) 
{
    // Cast packet to IP header
    const struct iphdr* ip_hdr = (const struct iphdr*)(packet);
    
    const struct udphdr* udp_hdr;
    // udp_hdr = (const struct udphdr*)(packet + sizeof(struct ether_header) + sizeof(struct ip));
    udp_hdr = (const struct udphdr*)(packet  + (ip_hdr->ihl * 4));

    printf("[UDP SEGMENT]");
    printf("source_port:%u, ", ntohs(udp_hdr->uh_sport));
    printf("dest_port:%u, ", ntohs(udp_hdr->uh_dport));
    printf("length:%u\n", ntohs(udp_hdr->uh_ulen));
}
*/
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
    // Print the ICMP header information
    printf("[ICMP SEGMENT] type:%d, code:%d, checksum:%d\n",
            icmp_hdr->type, icmp_hdr->code, ntohs(icmp_hdr->checksum));    
#endif            
} 

/*
void process_icmp_segment(const u_char* packet) 
{
    const struct iphdr* ip_hdr = (const struct iphdr*)(packet);
    
    // const struct icmphdr* icmp_hdr = (const struct icmphdr*)(packet + sizeof(struct iphdr));
    const struct icmphdr* icmp_hdr = (const struct icmphdr*)(packet + (ip_hdr->ihl * 4) );
    
    // Print the ICMP header information
    printf("[ICMP SEGMENT] type:%d, code:%d, checksum:%d\n",
            icmp_hdr->type, icmp_hdr->code, ntohs(icmp_hdr->checksum));

}
**/

void process_sctp_segment(struct sctp_header* sctp_hdr, const u_char* sctp_segment) 
{
    uint16_t src_port = ntohs(sctp_hdr->source_port);
    uint16_t dst_port = ntohs(sctp_hdr->destination_port);
    uint32_t verification_tag = ntohl(sctp_hdr->verification_tag);
    uint32_t checksum = ntohl(sctp_hdr->checksum);
#ifdef LOG_VERBOSE
    printf("[SCTP PACKET] Source Port: %u | Destination Port: %u | Verification Tag: %u | Checksum: %u\n", src_port, dst_port, verification_tag, checksum);
#endif
}


void process_arp_packet(const struct ether_arp* arp_header, u_char* arp_packet)
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

    std::cout << "[ARP packet] " << " MACsrc:" << src_mac <<  ", MACdst: " << dst_mac << 
                                     ", IPsrc: " << src_ip << ", IPdst: " << dst_ip 
              << std::endl;
}

void process_rarp_packet(struct rarp_header* rarp_hdr, u_char* rarp_packet)
{
    // Print RARP header informatio
    printf("RARP packet:\n");
    printf("  Sender MAC: %02x:%02x:%02x:%02x:%02x:%02x\n",
           rarp_hdr->sha[0], rarp_hdr->sha[1], rarp_hdr->sha[2],
           rarp_hdr->sha[3], rarp_hdr->sha[4], rarp_hdr->sha[5]);
    printf("  Sender IP: %d.%d.%d.%d\n",
           rarp_hdr->spa[0], rarp_hdr->spa[1], rarp_hdr->spa[2], rarp_hdr->spa[3]);
    printf("  Target MAC: %02x:%02x:%02x:%02x:%02x:%02x\n",
           rarp_hdr->tha[0], rarp_hdr->tha[1], rarp_hdr->tha[2],
           rarp_hdr->tha[3], rarp_hdr->tha[4], rarp_hdr->tha[5]);
    printf("  Target IP: %d.%d.%d.%d\n",
           rarp_hdr->tpa[0], rarp_hdr->tpa[1], rarp_hdr->tpa[2], rarp_hdr->tpa[3]);
}


void process_loopback_packet(const u_char* frame) 
{
#ifdef LOG_VERBOSE
    printf("LOOPBACK PACKET\n");
#endif

    // Extract the Ethernet header
    struct ether_header* ether_hdr = (struct ether_header*) frame;

    // Extract the loopback header
    //u_int16_t type = ntohs(ether_hdr->ether_type);
    //u_char* payload = (u_char*)(packet_data + sizeof(struct ether_header));
    //u_int16_t payload_length = pkthdr->len - sizeof(struct ether_header);

    // Print relevant header information
    //printf("Ethernet Type: 0x%04x\n", type);
    //printf("Payload Length: %d bytes\n", payload_length);
    //printf("Payload:\n");
    //for (int i = 0; i < payload_length; i++) {
    //    printf("%02x ", payload[i]);
    //    if ((i+1) % 16 == 0) printf("\n");
    //}
    //printf("\n");
}


void process_wol_packet(const struct ether_header *ether_hdr, const u_char *frame) 
{
    // Cast the packet pointer to an Ethernet header structure pointer
    // struct ether_header *ether_hdr = (struct ether_header *) frame;

    // Check if it's a Wake-on-LAN frame
    if (ntohs(ether_hdr->ether_type) == ETHERTYPE_WAKE_ON_LAN) 
    {
        printf("Wake-on-LAN packet received\n");
        // Get the destination MAC address (target address)
        // uint8_t *target_mac = ether_hdr->ether_dhost;
        // printf("Target MAC address: %02X:%02X:%02X:%02X:%02X:%02X\n", 
        //        target_mac[0], target_mac[1], target_mac[2], target_mac[3], target_mac[4], target_mac[5]);
    }
}
































//

