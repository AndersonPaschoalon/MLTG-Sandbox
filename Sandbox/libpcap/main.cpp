#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <iostream>
#include <fstream>
#include <string>

#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/in.h>
#include <netinet/if_ether.h> /* includes net/ethernet.h */
#include <pcap.h> /* if this gives you an error try pcap/pcap.h */
#include <sys/socket.h>

#define PROMISCUOUS_MODE 1

// Utils
int logOnfile(const char* fileName, const char* msg);

// ChatGPT implementation
void packetHandler(u_char* userData, const struct pcap_pkthdr* pkthdr, const u_char* packetData);
int chatGPT_implementation();

// libpcap tutorial
void libpcap_tutorial_section01();
void libpcap_tutorial_section02();


int main(int argc, char* argv[])
{
    logOnfile("./log/main.log", "Initializing application...");
    bool test01 = true;
    bool test02 = false;
    bool test03 = false;

    if (test01) chatGPT_implementation();
    if (test02) libpcap_tutorial_section01();
    if (test03) libpcap_tutorial_section02();

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
    if (ntohs(ethernetHeader->ether_type) != ETHERTYPE_IP) 
    {
        return;
    }

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

