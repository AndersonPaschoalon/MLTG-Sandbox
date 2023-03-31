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
#include <netinet/ip_icmp.h> 
#include <netinet/if_ether.h> /* includes net/ethernet.h */
#include <pcap.h> /* if this gives you an error try pcap/pcap.h */
#include <sys/socket.h>

#define PROMISCUOUS_MODE            1
#define ETHERTYPE_WAKE_ON_LAN       0x0842

struct timeval firstTimeStamp = {.tv_sec = 0, .tv_usec = 0};

// Utils
int logOnfile(const char* fileName, const char* msg);

// ChatGPT implementation
void packetHandler(u_char* userData, const struct pcap_pkthdr* pkthdr, const u_char* packetData);
int chatGPT_implementation();
// read offline packets
void test_pcap_file();
void read_pcap_file(const char* filename);
void process_packet(u_char* user, const struct pcap_pkthdr* pkt_header, const u_char* packet);
// protocol parses
void process_ipv4_packet(const u_char* packet);
void process_rarp_packet(const u_char* packet, int packet_len);
void process_arp_packet(const u_char* packet, const struct pcap_pkthdr* pkt_header) ;
void process_loopback_packet(const u_char* packet_data, const struct pcap_pkthdr* pkthdr);
void process_wol_packet(const u_char *packet) ;
void process_icmp_packet(const u_char* packet, const struct pcap_pkthdr* pkthdr);
double calculateTimestampInSec(const struct timeval t0, const struct timeval currentTimestamp);

// libpcap tutorial
void libpcap_tutorial_section01();
void libpcap_tutorial_section02();

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

int main(int argc, char* argv[])
{
    logOnfile("./log/main.log", "Initializing application...");
    bool test01 = false; // promissor
    bool test02 = false;
    bool test03 = false;
    bool test04 = true;

    if (test01) chatGPT_implementation();
    if (test02) libpcap_tutorial_section01();
    if (test03) libpcap_tutorial_section02();
    if (test04) test_pcap_file();

    return 0;
}

int logOnfile(const char* fileName, const char* msg) 
{

    // Open the file for writing in append mode
    std::ofstream file(fileName, std::ios::app);
    if (!file.is_open()) {
        // Failed to open the file
        return -1;
    }

    // Write the message to the file and on stdout
    printf("%s\n", msg);
    file << msg << std::endl;

    // Close the file
    file.close();

    // Return success
    return 0;
}

void packetHandler(u_char* userData, const struct pcap_pkthdr* pkthdr, const u_char* packetData)
{
    const char LOG_FILE[] = "./log/chatGPT_implementation.log";
    const ether_header* ethernetHeader = reinterpret_cast<const ether_header*>(packetData);
    int headerLength = sizeof(ether_header);

    // Only process Ethernet packets with IP payload
    //if (ntohs(ethernetHeader->ether_type) != ETHERTYPE_IP) 
    //{
    //    return;
    //}

    const struct ip* ipHeader = reinterpret_cast<const struct ip*>(packetData + headerLength);
    headerLength += sizeof(struct ip);

    char ipAddress[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &(ipHeader->ip_src), ipAddress, INET_ADDRSTRLEN);

    std::string msg = "Received packet with source IP address: " + std::string(ipAddress);
    std::cout << msg << std::endl;
    // std::cout << "Received packet with source IP address: " << ipAddress << std::endl;
    logOnfile(LOG_FILE, msg.c_str());
}

int chatGPT_implementation()
{
    printf("-- chatGPT_implementation\n");
    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t* descr;
    struct bpf_program fp;
    bpf_u_int32 maskp;
    bpf_u_int32 netp;

    // Define the filter expression
    char filterExp[] = "tcp or udp or icmp or arp";

    // Open the capture device
    descr = pcap_open_live("eth0", BUFSIZ, 1, 1000, errbuf);
    if(descr == NULL) 
    {
        printf("pcap_open_live() failed: %s\n", errbuf);
        return 1;
    }

    // Compile the filter expression
    if(pcap_compile(descr, &fp, filterExp, 0, netp) == -1) 
    {
        printf("pcap_compile() failed: %s\n", pcap_geterr(descr));
        return 1;
    }

    // Set the filter expression
    if(pcap_setfilter(descr, &fp) == -1) 
    {
        printf("pcap_setfilter() failed: %s\n", pcap_geterr(descr));
        return 1;
    }

    // Capture packets
    pcap_loop(descr, -1, packetHandler, NULL);

    return 0;
}

void process_arp_packet(const struct ether_arp* arp_header, const u_char* packet) 
{
    char src_mac[18];
    char dst_mac[18];
    char src_ip[INET_ADDRSTRLEN];
    char dst_ip[INET_ADDRSTRLEN];

    sprintf(src_mac, "%02x:%02x:%02x:%02x:%02x:%02x", arp_header->arp_sha[0], arp_header->arp_sha[1], arp_header->arp_sha[2], arp_header->arp_sha[3], arp_header->arp_sha[4], arp_header->arp_sha[5]);
    sprintf(dst_mac, "%02x:%02x:%02x:%02x:%02x:%02x", arp_header->arp_tha[0], arp_header->arp_tha[1], arp_header->arp_tha[2], arp_header->arp_tha[3], arp_header->arp_tha[4], arp_header->arp_tha[5]);
    inet_ntop(AF_INET, arp_header->arp_spa, src_ip, INET_ADDRSTRLEN);
    inet_ntop(AF_INET, arp_header->arp_tpa, dst_ip, INET_ADDRSTRLEN);

    std::cout << "ARP packet >> " << " MACsrc:" << src_mac <<  ", MACdst: " << dst_mac << 
                                     ", IPsrc: " << src_ip << ", IPdst: " << dst_ip 
              << std::endl;
}

void process_rarp_packet(const u_char* packet, int packet_len) 
{
    // Ethernet header
    struct ether_header* ether_hdr = (struct ether_header*)packet;

    // Check if it's a RARP packet
    if (ntohs(ether_hdr->ether_type) != ETHERTYPE_REVARP) {
        return;
    }

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

void process_loopback_packet(const u_char* packet_data, const struct pcap_pkthdr* pkthdr) 
{
    // printf("---------- Loopback Packet ----------\n");
    printf("LOOPBACK PACKET\n");

    // Extract the Ethernet header
    struct ether_header* ether_hdr = (struct ether_header*) packet_data;

    // Extract the loopback header
    u_int16_t type = ntohs(ether_hdr->ether_type);
    u_char* payload = (u_char*)(packet_data + sizeof(struct ether_header));
    u_int16_t payload_length = pkthdr->len - sizeof(struct ether_header);

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
        uint8_t *target_mac = ether_hdr->ether_dhost;
        printf("Target MAC address: %02X:%02X:%02X:%02X:%02X:%02X\n", 
               target_mac[0], target_mac[1], target_mac[2], target_mac[3], target_mac[4], target_mac[5]);
    }
}


void process_icmp_packet(const u_char* packet, const struct pcap_pkthdr* pkthdr) 
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



void process_packet(u_char* user, const struct pcap_pkthdr* pkt_header, const u_char* packet)
{
    // Process the packet here
    const struct ether_header* ether_hdr = (const struct ether_header*)packet;

    if(firstTimeStamp.tv_sec == 0)
    {
        firstTimeStamp.tv_sec = pkt_header->ts.tv_sec;
        firstTimeStamp.tv_usec = pkt_header->ts.tv_usec;
    }
    // printf("Packet timestamp: %ld.%06ld\n", pkt_header->ts.tv_sec, pkt_header->ts.tv_usec);
    printf("Timestamp [%f]", calculateTimestampInSec(firstTimeStamp, pkt_header->ts));

    // Check if it is an IP packet
    if (ntohs(ether_hdr->ether_type) == ETHERTYPE_IP) 
    {
        struct iphdr* ip_hdr = (struct iphdr*)(packet + sizeof(struct ether_header));
        // Check if it is an ICMP packet
        if(ip_hdr->protocol == IPPROTO_IP || ip_hdr->protocol == IPPROTO_UDP || ip_hdr->protocol == IPPROTO_TCP)
        {
            process_ipv4_packet(packet);
        }  
        else if (ip_hdr->protocol == IPPROTO_ICMP) 
        {
            process_icmp_packet(packet, pkt_header);
        }
    }
    // Check if it is an ARP packet
    else if (ntohs(ether_hdr->ether_type) == ETHERTYPE_ARP) 
    {
        process_arp_packet(packet, pkt_header);
    }
    //
    else if (ntohs(ether_hdr->ether_type) == ETHERTYPE_WAKE_ON_LAN) 
    {
        process_wol_packet(packet);
    }
    else if(ntohs(ether_hdr->ether_type) == ETHERTYPE_LOOPBACK) 
    {
        process_loopback_packet(packet, pkt_header);
    }
    else
    {
        printf("UNKNOWN PACKET %X\n", ntohs(ether_hdr->ether_type));
    }
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

double calculateTimestampInSec(const struct timeval t0, const struct timeval currentTimestamp) 
{
    double timestampInSeconds = (currentTimestamp.tv_sec - t0.tv_sec) + ((currentTimestamp.tv_usec - t0.tv_usec) / 1000000.0);
    return timestampInSeconds;
}

void test_pcap_file()
{

    read_pcap_file("../../Pcap/arp_pcap.pcapng.cap.pcap");
    // read_pcap_file("../../Pcap/mysql_complete.pcap");
    // read_pcap_file("../../Pcap/http_PPI.pcap");
    // read_pcap_file("../../Pcap/telnet-cooked.pcap");
    read_pcap_file("../../Pcap/SkypeIRC.cap.pcap");
    read_pcap_file("../../Pcap/snmp_usm.pcap");
    
}

void libpcap_tutorial_section01()
{
    printf("http://yuba.stanford.edu/~casado/pcap/section1.html\n");

    char *dev; /* name of the device to use */ 
    char *net; /* dot notation of the network address */
    char *mask;/* dot notation of the network mask    */
    int ret;   /* return code */
    char errbuf[PCAP_ERRBUF_SIZE];
    bpf_u_int32 netp; /* ip          */
    bpf_u_int32 maskp;/* subnet mask */
    struct in_addr addr;

    /* ask pcap to find a valid device for use to sniff on */
    dev = pcap_lookupdev(errbuf);

    /* error checking */
    if(dev == NULL)
    {
        printf("%s\n",errbuf);
        exit(1);
    }

    /* print out device name */
    printf("DEV: %s\n", dev);

    /* ask pcap for the network address and mask of the device */
    ret = pcap_lookupnet(dev, &netp, &maskp, errbuf);

    if(ret == -1)
    {
        printf("%s\n",errbuf);
        exit(1);
    }

    /* get the network address in a human readable form */
    addr.s_addr = netp;
    net = inet_ntoa(addr);

    if(net == NULL)/* thanks Scott :-P */
    {
        perror("inet_ntoa");
        exit(1);
    }
    printf("NET: %s\n",net);

    /* do the same as above for the device's mask */
    addr.s_addr = maskp;
    mask = inet_ntoa(addr);

    if(mask == NULL)
    {
        perror("inet_ntoa");
        exit(1);
    }

    printf("MASK: %s\n",mask);
}

void libpcap_tutorial_section02()
{
    const char LOG_FILE[] = "./log/libpcap_tutorial_section02.log";
    int i;
    char *dev; 
    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t* descr;
    const u_char *packet;
    struct pcap_pkthdr hdr;     /* pcap.h */
    struct ether_header *eptr;  /* net/ethernet.h */
    pcap_if_t *alldevsp;

    u_char *ptr; /* printing out hardware header info */

    /* grab a device to peak into... */
    int ret = pcap_findalldevs(&alldevsp, errbuf);
    dev = alldevsp->name;
    // dev = pcap_lookupdev(errbuf);

    if(dev == NULL)
    {
        printf("%s\n",errbuf);
        exit(1);
    }

    printf("DEV: %s\n",dev);
    std::string msg = "* LISTENING DEV:" + std::string(dev) + "\n";
    logOnfile(LOG_FILE, msg.c_str());

    /* 
        open the device for sniffing.

        pcap_t *pcap_open_live(char *device,int snaplen, int prmisc,int to_ms,
        char *ebuf)

        snaplen - maximum size of packets to capture in bytes
        promisc - set card in promiscuous mode?
        to_ms   - time to wait for packets in miliseconds before read
        times out
        errbuf  - if something happens, place error string here

        Note if you change "prmisc" param to anything other than zero, you will
        get all packets your device sees, whether they are intendeed for you or
        not!! Be sure you know the rules of the network you are running on
        before you set your card in promiscuous mode!!
    */
    // descr = pcap_open_live(dev, BUFSIZ, 0, -1, errbuf);
    // descr = pcap_open_live(dev, BUFSIZ, PROMISCUOUS_MODE, -1, errbuf);
    descr = pcap_open_live(dev, BUFSIZ, PROMISCUOUS_MODE, 1000, errbuf);

    if(descr == NULL)
    {
        printf("pcap_open_live(): %s\n",errbuf);
        exit(1);
    }


    /*
       grab a packet from descr (yay!)                    
       u_char *pcap_next(pcap_t *p,struct pcap_pkthdr *h) 
       so just pass in the descriptor we got from         
       our call to pcap_open_live and an allocated        
       struct pcap_pkthdr                                 
    */
    logOnfile(LOG_FILE, msg.c_str());
    packet = pcap_next(descr,&hdr);

    if(packet == NULL)
    {/* dinna work *sob* */
        printf("Didn't grab packet\n");
        exit(1);
    }

    /*  struct pcap_pkthdr {
        struct timeval ts;   time stamp 
        bpf_u_int32 caplen;  length of portion present 
        bpf_u_int32;         lebgth this packet (off wire) 
        }
     */

    printf("Grabbed packet of length %d\n",hdr.len);
    printf("Recieved at ..... %s\n",ctime((const time_t*)&hdr.ts.tv_sec)); 
    printf("Ethernet address length is %d\n",ETHER_HDR_LEN);

    /* lets start with the ether header... */
    eptr = (struct ether_header *) packet;

    /* Do a couple of checks to see what packet type we have..*/
    if (ntohs (eptr->ether_type) == ETHERTYPE_IP)
    {
        printf("Ethernet type hex:%x dec:%d is an IP packet\n",
                ntohs(eptr->ether_type),
                ntohs(eptr->ether_type));
    }else  if (ntohs (eptr->ether_type) == ETHERTYPE_ARP)
    {
        printf("Ethernet type hex:%x dec:%d is an ARP packet\n",
                ntohs(eptr->ether_type),
                ntohs(eptr->ether_type));
    }else {
        printf("Ethernet type %x not IP", ntohs(eptr->ether_type));
        exit(1);
    }

    /* copied from Steven's UNP */
    ptr = eptr->ether_dhost;
    i = ETHER_ADDR_LEN;
    printf(" Destination Address:  ");
    do{
        printf("%s%x",(i == ETHER_ADDR_LEN) ? " " : ":",*ptr++);
    }while(--i>0);
    printf("\n");

    ptr = eptr->ether_shost;
    i = ETHER_ADDR_LEN;
    printf(" Source Address:  ");
    do{
        printf("%s%x",(i == ETHER_ADDR_LEN) ? " " : ":",*ptr++);
    }while(--i>0);

    pcap_freealldevs(alldevsp);
    printf("\n");    
}





























//

