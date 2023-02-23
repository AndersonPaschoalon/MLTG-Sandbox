#include <pcap.h>
#include <netinet/ip.h>
#include <netinet/in.h>
#include <netinet/if_ether.h>
#include <arpa/inet.h>
#include <iostream>

void packetHandler(u_char* userData, const struct pcap_pkthdr* pkthdr, const u_char* packetData);

int main(int argc, char* argv[])
{

    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t* descr;
    struct bpf_program fp;
    bpf_u_int32 maskp;
    bpf_u_int32 netp;

    // Define the filter expression
    char filterExp[] = "tcp or udp or icmp or arp";

    // Open the capture device
    descr = pcap_open_live("eth0", BUFSIZ, 1, 0, errbuf);
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

void packetHandler(u_char* userData, const struct pcap_pkthdr* pkthdr, const u_char* packetData)
{
    const ether_header* ethernetHeader = reinterpret_cast<const ether_header*>(packetData);
    int headerLength = sizeof(ether_header);

    // Only process Ethernet packets with IP payload
    if (ntohs(ethernetHeader->ether_type) != ETHERTYPE_IP) {
        return;
    }

    const struct ip* ipHeader = reinterpret_cast<const struct ip*>(packetData + headerLength);
    headerLength += sizeof(struct ip);

    char ipAddress[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &(ipHeader->ip_src), ipAddress, INET_ADDRSTRLEN);

    std::cout << "Received packet with source IP address: " << ipAddress << std::endl;
}
