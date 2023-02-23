#include "EtherDummy.h"

EtherDummy::EtherDummy()
{
    printf("EtherDummy\n");
    this->vecPackets = new std::vector<NetworkPacket>();
    this->currentElement = -1;
}

EtherDummy::~EtherDummy()
{
    delete this->vecPackets;
}

int EtherDummy::listen()
{
    int nElements = 0;
    double timeStamp = 0.0;
    int size0 = 64;
    int size1 = 128;
    int size2 = 512;
    int size3 = 1024;
    ipv4_address addr1 = 0xFFFF1212; // 255.255.18.18
    ipv4_address addr2 = 0xFFFF0015; // 255.255.0.21
    port_number port1 = 0x00FF; // 255
    port_number port2 = 0xFF00; // 65280

    // Flow 1
    NetworkPacket p1 = NetworkPacket("Flow 1, ip, addr1, addr2, tcp, port1, port2");
    p1.setPysical(timeStamp, size0);
    p1.setNetwork(NetworkProtocol::IPv4, addr1, addr2);
    p1.setTransport(TransportProtocol::TCP, port1, port2);
    p1.setApplication(ApplicationProtocol::HTTP);

    // Flow 2
    timeStamp += 0.5;
    NetworkPacket p2 = NetworkPacket("Flow 2, ip, addr2, addr1, tcp, port1, port2");
    p2.setPysical(timeStamp, size1);
    p2.setNetwork(NetworkProtocol::IPv4, addr2, addr1);
    p2.setTransport(TransportProtocol::TCP, port1, port2);
    p2.setApplication(ApplicationProtocol::HTTP);

    // Flow 3
    timeStamp += 0.5;
    NetworkPacket p3 = NetworkPacket("Flow 3, ip, addr2, addr1, tcp, port2, port1");
    p3.setPysical(timeStamp, size2);
    p3.setNetwork(NetworkProtocol::IPv4, addr2, addr1);
    p3.setTransport(TransportProtocol::TCP, port2, port1);
    p3.setApplication(ApplicationProtocol::HTTP);

    // Flow 3
    timeStamp += 0.5;
    NetworkPacket p4 = NetworkPacket("Flow 3, ip, addr2, addr1, tcp, port2, port1");
    p4.setPysical(timeStamp, size1);
    p4.setNetwork(NetworkProtocol::IPv4, addr2, addr1);
    p4.setTransport(TransportProtocol::TCP, port2, port1);
    p4.setApplication(ApplicationProtocol::HTTP);

    // Flow 4
    timeStamp += 0.5;
    NetworkPacket p5 = NetworkPacket("Flow 4, ip, addr2, addr1, udp, port2, port1");
    p5.setPysical(timeStamp, size0);
    p5.setNetwork(NetworkProtocol::IPv4, addr2, addr1);
    p5.setTransport(TransportProtocol::UDP, port2, port1);
    p5.setApplication(ApplicationProtocol::HTTP);

    // Flow 4
    timeStamp += 0.5;
    NetworkPacket p6 = NetworkPacket("Flow 4, ip, addr2, addr1, udp, port2, port1");
    p6.setPysical(timeStamp, size1);
    p6.setNetwork(NetworkProtocol::IPv4, addr2, addr1);
    p6.setTransport(TransportProtocol::UDP, port2, port1);
    p6.setApplication(ApplicationProtocol::HTTP);

    // Flow 5
    timeStamp += 0.5;
    NetworkPacket p7 = NetworkPacket("Flow 5, icmp, addr2, addr1");
    p7.setPysical(timeStamp, size2);
    p7.setNetwork(NetworkProtocol::ICMP, addr2, addr1);

    // Flow 6
    timeStamp += 0.5;
    NetworkPacket p8 = NetworkPacket("Flow 6, icmp, addr1, addr2");
    p8.setPysical(timeStamp, size3);
    p8.setNetwork(NetworkProtocol::ICMP, addr1, addr2);

    //  Flow 6
    timeStamp += 0.5;
    NetworkPacket p9 = NetworkPacket("Flow 6, icmp, addr1, addr2");
    p9.setPysical(timeStamp, size3);
    p9.setNetwork(NetworkProtocol::ICMP, addr1, addr2);

    // Flow 7
    timeStamp += 0.5;
    NetworkPacket p10 = NetworkPacket("Flow 7, arp, addr1, addr2");
    p10.setPysical(timeStamp, size3);
    p10.setNetwork(NetworkProtocol::ARP, addr1, addr2);

    // Flow 8
    timeStamp += 0.5;
    NetworkPacket p11 = NetworkPacket("Flow 8, arp, addr2, addr1");
    p11.setPysical(timeStamp, size0);
    p11.setNetwork(NetworkProtocol::ARP, addr2, addr1);

    this->vecPackets->push_back(p1);
    this->vecPackets->push_back(p2);
    this->vecPackets->push_back(p3);
    this->vecPackets->push_back(p4);
    this->vecPackets->push_back(p5);
    this->vecPackets->push_back(p6);
    this->vecPackets->push_back(p7);
    this->vecPackets->push_back(p8);
    this->vecPackets->push_back(p9);
    this->vecPackets->push_back(p10);
    this->vecPackets->push_back(p11);

    return  0;
}

NetworkPacket &EtherDummy::pop_back()
{
    this->currentElement++;
    if (this->currentElement >= this->vecPackets->size())
    {
        this->currentElement = 0;
    }
	printf("pkt%d\n", this->currentElement);
    return this->vecPackets->at(this->currentElement);
}
