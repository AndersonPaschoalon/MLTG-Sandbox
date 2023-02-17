#include "Trace.h"

Trace::Trace()
{
    this->flows = std::vector<Flow*>();
    this->flows.clear();
}

Trace::~Trace()
{
    for (Flow* f : this->flows)
    {
        delete f;
    }
    this->flows.clear();
}

void Trace::addFlow(Flow *flow)
{
    this->flows.push_back(flow);
}

void Trace::bufferParser(ETHER_BUFFER_NODE *buffer, FlowIdCalc *flowCalc)
{
    ETHER_BUFFER_NODE* currentNode = NULL;
    NetworkPacket* currentPacket = NULL;

    currentNode = buffer;
    while(currentNode != NULL)
    {
        currentPacket = currentNode->etherPacket;

        // current trace already has flows 0, 1, ..., n - 1. Next is n.
        size_t nextFlowId = flows.size();
        flow_id currentPacketFlow = flowCalc->setFlowId(*currentPacket);

        // add a new flow
        if (currentPacketFlow == nextFlowId)
        {
            Flow* newFlow = new Flow();
            NetworkProtocol proto;
            switch (proto)
            {
                case NetworkProtocol::IPv4:
                {
                    newFlow->set(currentPacketFlow,                         // flow_id flowId,
                                 currentPacket->getTimestamp(),             // time_stamp timeStamp, 
                                 currentPacket->getNetworkProtocol(),       // NetworkProtocol n, 
                                 currentPacket->getIPv4Src(),               // ipv4_address ipsrc, 
                                 currentPacket->getIPv4Dst(),               // ipv4_address ipdst,
                                 currentPacket->getTransportProtocol(),     // TransportProtocol t,
                                 currentPacket->getPortSrc(),               // port_number portSrc,
                                 currentPacket->getPortDst(),               // port_number portDst,
                                 currentPacket->getApplicationProtocol()    // ApplicationProtocol app
                                );
                    break;
                }
                case NetworkProtocol::IPv6:
                {
                    newFlow->set(currentPacketFlow,                         // flow_id flowId,
                                 currentPacket->getTimestamp(),             // time_stamp timeStamp, 
                                 currentPacket->getNetworkProtocol(),       // NetworkProtocol n, 
                                 currentPacket->getIPv6Src(),               // ipv6_address ipsrc, 
                                 currentPacket->getIPv6Dst(),               // ipv6_address ipdst,
                                 currentPacket->getTransportProtocol(),     // TransportProtocol t,
                                 currentPacket->getPortSrc(),               // port_number portSrc,
                                 currentPacket->getPortDst(),               // port_number portDst,
                                 currentPacket->getApplicationProtocol()    // ApplicationProtocol app
                                );                       
                }
                case NetworkProtocol::ARP:
                case NetworkProtocol::ICMP:
                case NetworkProtocol::RIPv2:
                case NetworkProtocol::RIPv1:
                {
                    newFlow->set(currentPacketFlow,                         // flow_id flowId,
                                 currentPacket->getTimestamp(),             // time_stamp timeStamp, 
                                 currentPacket->getNetworkProtocol(),       // NetworkProtocol n, 
                                 currentPacket->getIPv4Src(),               // ipv4_address ipsrc, 
                                 currentPacket->getIPv4Dst()               // ipv4_address ipdst,
                                );
                    break;                    
                }
                case NetworkProtocol::ICMPv6:
                {
                    newFlow->set(currentPacketFlow,                         // flow_id flowId,
                                 currentPacket->getTimestamp(),             // time_stamp timeStamp, 
                                 currentPacket->getNetworkProtocol(),       // NetworkProtocol n, 
                                 currentPacket->getIPv6Src(),               // ipv6_address ipsrc, 
                                 currentPacket->getIPv6Dst()                // ipv6_address ipdst,
                                );
                    break;
                }
                default:
                {
                    // Não deve ocorrer!!
                    newFlow->set(currentPacketFlow,                         // flow_id flowId,
                                 currentPacket->getTimestamp(),             // time_stamp timeStamp, 
                                 currentPacket->getNetworkProtocol(),       // NetworkProtocol n, 
                                 currentPacket->getIPv4Src(),               // ipv4_address ipsrc, 
                                 currentPacket->getIPv4Dst()                // ipv4_address ipdst,
                                );
                    break;
                }
                this->addFlow(newFlow);
                // clean wild pointer 
                newFlow = NULL;
            }
        }
        // this should always happen, since we add a new flow
        if (currentPacketFlow < flows.size())
        {
            FlowPacket* pkt = new FlowPacket(currentPacket->getTimestamp(),   // double timeStamp, 
                                             currentPacket->getPacketSize(), // unsigned int packetSize, 
                                             currentPacket->getTtl() //ttl timeToLive
                                             );
            this->flows[currentPacketFlow]->addPacket(pkt);
            // clean wild pointer
            pkt = NULL;
        }
        else
        {
            printf("**TODO - ERROR**\n");
        }
        currentNode = buffer->next;
    }


}