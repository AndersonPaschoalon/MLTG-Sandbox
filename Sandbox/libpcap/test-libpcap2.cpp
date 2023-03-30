#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <iostream>
#include <fstream>
#include <string>

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

struct timeval firstTimeStamp = {.tv_sec = 0, .tv_usec = 0};


// read offline packets
void test_pcap_file();
void read_pcap_file(const char* filename);
void process_packet(u_char* user, const struct pcap_pkthdr* pkt_header, const u_char* packet);
double calculateTimestampInSec(const struct timeval t0, const struct timeval currentTimestamp);

// protocol parses
void process_icmp_segment(const u_char* packet);
void process_tcp_segment(const u_char* packet);
void process_udp_segment(const u_char* packet);
void process_sctp_segment(const u_char* packet);

void process_ipv4_packet(const u_char* packet);
void process_rarp_packet(const u_char* packet);
void process_arp_packet(const u_char* packet) ;
void process_loopback_packet(const u_char* packet_data);
void process_wol_packet(const u_char *packet) ;
void process_icmp_packet(const u_char* packet);


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
    
}

void read_pcap_file(const char* filename) 
{
    firstTimeStamp = {.tv_sec = 0, .tv_usec = 0};
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

    pcap_loop(pcap_handle, 0, process_packet, nullptr);
    pcap_close(pcap_handle);
}

void process_packet(u_char* user, const struct pcap_pkthdr* pkt_header, const u_char* packet)
{
    // Process the packet here
    const struct ether_header* ether_hdr = (const struct ether_header*)packet;

    if(firstTimeStamp.tv_sec == 0)
    {
        firstTimeStamp.tv_sec = pkt_header->ts.tv_sec;
        firstTimeStamp.tv_usec = pkt_header->ts.tv_usec;
    }
    int frame_len = pkt_header->len;
    // printf("Packet timestamp: %ld.%06ld\n", pkt_header->ts.tv_sec, pkt_header->ts.tv_usec);
    printf("[ETHERNET FRAME] Timestamp [%f] EtherType:%X, FrameLen:%d ", calculateTimestampInSec(firstTimeStamp, pkt_header->ts), ether_hdr->ether_type, frame_len);

    // Check if it is an IP packet
    if (ntohs(ether_hdr->ether_type) == ETHERTYPE_IP) 
    {
        struct iphdr* ip_hdr = (struct iphdr*)(packet + sizeof(struct ether_header));
        printf("[IP PACKET] version:%d, ihl:%d, tot_len:%d, ttl:%d, daddr:%X, saddr:%X ", ip_hdr->version, ip_hdr->ihl, ip_hdr->tot_len, ip_hdr->ttl, ntohl(ip_hdr->daddr), ntohl(ip_hdr->saddr));
        // Check if it is an ICMP packet
        if(ip_hdr->protocol == IPPROTO_IP || ip_hdr->protocol == IPPROTO_TCP)
        {
            process_tcp_segment(packet);
        } 
        else if (ip_hdr->protocol == IPPROTO_UDP) 
        {
            process_udp_segment(packet);
        }
        else if (ip_hdr->protocol == IPPROTO_ICMP) 
        {
            process_icmp_segment(packet);
        }
    }
    // Check if it is an ARP packet
    else if (ntohs(ether_hdr->ether_type) == ETHERTYPE_ARP) 
    {
        process_arp_packet(packet);
    }
    // Check if it is an REVERSE ARP packet
    else if (ntohs(ether_hdr->ether_type) == ETHERTYPE_REVARP) 
    {
        process_rarp_packet(packet);
    }
    else if (ntohs(ether_hdr->ether_type) == ETHERTYPE_WAKE_ON_LAN) 
    {
        process_wol_packet(packet);
    }
    else if(ntohs(ether_hdr->ether_type) == ETHERTYPE_LOOPBACK) 
    {
        process_loopback_packet(packet);
    }
    else
    {
        printf("UNKNOWN PACKET %X\n", ntohs(ether_hdr->ether_type));
    }
}

double calculateTimestampInSec(const struct timeval t0, const struct timeval currentTimestamp) 
{
    double timestampInSeconds = (currentTimestamp.tv_sec - t0.tv_sec) + ((currentTimestamp.tv_usec - t0.tv_usec) / 1000000.0);
    return timestampInSeconds;
}

void process_tcp_segment(const u_char* packet) {
    // Cast packet to IP header
    const struct iphdr* ip_hdr = (const struct iphdr*)(packet + sizeof(struct ether_header));

    // Calculate TCP header pointer based on IP header length
    int tcp_hdr_length = (ip_hdr->ihl * 4) + sizeof(struct tcphdr);
    const struct tcphdr* tcp_hdr = (const struct tcphdr*)(packet + sizeof(struct ether_header) + (ip_hdr->ihl * 4));

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

void process_udp_segment(const u_char* packet) {
    const struct udphdr* udp_hdr;
    udp_hdr = (const struct udphdr*)(packet + sizeof(struct ether_header) + sizeof(struct ip));

    printf("[UDP SEGMENT]");
    printf("source_port:%u, ", ntohs(udp_hdr->uh_sport));
    printf("dest_port:%u, ", ntohs(udp_hdr->uh_dport));
    printf("length:%u\n", ntohs(udp_hdr->uh_ulen));
}


void process_icmp_segment(const u_char* packet) {
    const struct ether_header* ether_hdr = (const struct ether_header*)packet;
    const struct iphdr* ip_hdr = (const struct iphdr*)(packet + sizeof(struct ether_header));
    
    // Check if it's an IP packet and if the protocol is ICMP
    if (ntohs(ether_hdr->ether_type) == ETHERTYPE_IP && ip_hdr->protocol == IPPROTO_ICMP) {
        const struct icmphdr* icmp_hdr = (const struct icmphdr*)(packet + sizeof(struct ether_header) + sizeof(struct iphdr));
        
        // Print the ICMP header information
        printf("[ICMP SEGMENT] type:%d, code:%d, checksum:%d\n",
               icmp_hdr->type, icmp_hdr->code, ntohs(icmp_hdr->checksum));
    }
}

void process_sctp_segment(const u_char* packet) {
    struct sctp_header* sctp_hdr = (struct sctp_header*)(packet + sizeof(struct ip) + sizeof(struct ether_header));
    uint16_t src_port = ntohs(sctp_hdr->source_port);
    uint16_t dst_port = ntohs(sctp_hdr->destination_port);
    uint32_t verification_tag = ntohl(sctp_hdr->verification_tag);
    uint32_t checksum = ntohl(sctp_hdr->checksum);

    printf("[SCTP PACKET] Source Port: %u | Destination Port: %u | Verification Tag: %u | Checksum: %u\n", src_port, dst_port, verification_tag, checksum);
}


void process_arp_packet(const u_char* packet) 
{
    const struct ether_arp* arp_header = (const struct ether_arp*)(packet + sizeof(struct ether_header));
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

void process_rarp_packet(const u_char* packet) 
{
    // Ethernet header
    struct ether_header* ether_hdr = (struct ether_header*)packet;

    // Check if it's a RARP packet
    //if (ntohs(ether_hdr->ether_type) != ETHERTYPE_REVARP) {
    //    return;
    //}

    // RARP header
    struct rarp_header* rarp_hdr = (struct rarp_header*)(packet + sizeof(struct ether_header));

    // Print RARP header information
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

void process_ipv4_packet(const u_char* packet) 
{
    // Parse the IP header
    struct iphdr* ip_hdr = (struct iphdr*)(packet + sizeof(struct ether_header));
    int ip_hdr_length = ip_hdr->ihl * 4;

    // Determine if the packet is TCP or UDP
    u_char* transport_packet = (u_char*)(packet + sizeof(struct ether_header) + ip_hdr_length);
    int transport_packet_length = ntohs(ip_hdr->tot_len) - ip_hdr_length;

    switch (ip_hdr->protocol) 
    {
        case IPPROTO_TCP: {
            // Parse the TCP header
            struct tcphdr* tcp_hdr = (struct tcphdr*)transport_packet;
            int tcp_hdr_length = tcp_hdr->doff * 4;

            // Print relevant information from the TCP header
            printf("TCP Packet:\n");
            printf("\tSource Port: %d\n", ntohs(tcp_hdr->source));
            printf("\tDestination Port: %d\n", ntohs(tcp_hdr->dest));

            // Determine the application protocol, if possible
            if (ntohs(tcp_hdr->dest) == 80 || ntohs(tcp_hdr->source) == 80) 
            {
                printf("\tApplication Protocol: HTTP\n");
            } else {
                printf("\tApplication Protocol: Unknown\n");
            }

            break;
        }
        case IPPROTO_UDP: 
        {
            // Parse the UDP header
            struct udphdr* udp_hdr = (struct udphdr*)transport_packet;
            int udp_hdr_length = sizeof(struct udphdr);

            // Print relevant information from the UDP header
            printf("UDP Packet:\n");
            printf("\tSource Port: %d\n", ntohs(udp_hdr->source));
            printf("\tDestination Port: %d\n", ntohs(udp_hdr->dest));

            // Determine the application protocol, if possible
            if (ntohs(udp_hdr->dest) == 53 || ntohs(udp_hdr->source) == 53) 
            {
                printf("\tApplication Protocol: DNS\n");
            } else {
                printf("\tApplication Protocol: Unknown\n");
            }

            break;
        }
        default:
            printf("Unknown transport protocol: %d\n", ip_hdr->protocol);
            break;
    }
}

void process_loopback_packet(const u_char* packet_data) 
{
    // printf("---------- Loopback Packet ----------\n");
    printf("LOOPBACK PACKET\n");

    // Extract the Ethernet header
    struct ether_header* ether_hdr = (struct ether_header*) packet_data;

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

void process_wol_packet(const u_char *packet) 
{
    // Cast the packet pointer to an Ethernet header structure pointer
    struct ether_header *ether_hdr = (struct ether_header *) packet;

    // Check if it's a Wake-on-LAN packet
    if (ntohs(ether_hdr->ether_type) == ETHERTYPE_WAKE_ON_LAN) 
    {
        printf("Wake-on-LAN packet received\n");

        // Get the destination MAC address (target address)
        // uint8_t *target_mac = ether_hdr->ether_dhost;
        // printf("Target MAC address: %02X:%02X:%02X:%02X:%02X:%02X\n", 
        //        target_mac[0], target_mac[1], target_mac[2], target_mac[3], target_mac[4], target_mac[5]);
    }
}

void process_icmp_packet(const u_char* packet) 
{
    // Get the Ethernet header
    struct ether_header* ether_hdr = (struct ether_header*)packet;

    // Get the IP header
    struct iphdr* ip_hdr = (struct iphdr*)(packet + sizeof(struct ether_header));

    // Get the ICMP header
    struct icmphdr* icmp_hdr = (struct icmphdr*)(packet + sizeof(struct ether_header) + sizeof(struct iphdr));

    // Print the source and destination MAC addresses
    printf("Source MAC: ");
    for (int i = 0; i < 6; i++) {
        printf("%02X", ether_hdr->ether_shost[i]);
        if (i < 5) printf(":");
    }
    printf("\n");

    printf("Destination MAC: ");
    for (int i = 0; i < 6; i++) {
        printf("%02X", ether_hdr->ether_dhost[i]);
        if (i < 5) printf(":");
    }
    printf("\n");

    // Print the source and destination IP addresses
    printf("Source IP: %s\n", inet_ntoa(*(struct in_addr*)&ip_hdr->saddr));
    printf("Destination IP: %s\n", inet_ntoa(*(struct in_addr*)&ip_hdr->daddr));

    // Print the ICMP type and code
    printf("ICMP type: %d\n", icmp_hdr->type);
    printf("ICMP code: %d\n", icmp_hdr->code);

}































//

