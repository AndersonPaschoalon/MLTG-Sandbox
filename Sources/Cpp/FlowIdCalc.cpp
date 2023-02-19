#include "FlowIdCalc.h"

FlowIdCalc::FlowIdCalc()
{
    this->lastFlowId = 0;
    this->netFlowsStack = new std::set<NetworkLayer>();

}

FlowIdCalc::~FlowIdCalc()
{

}

std::string FlowIdCalc::toString()
{
    return std::string("FlowIdCalc");
}

flow_id FlowIdCalc::setFlowId(NetworkPacket &packet)
{
    // check if the nework packet is already on the set

    NetworkLayer packetProto = {.proto=packet.getNetworkProtocol()};
    auto it = this->netFlowsStack->find(packetProto);
    if (it != this->netFlowsStack->end()) // there is packets of this protocol, and it is stored on it pointer
    {

    }
    else // no packet of this network protocol was found yet
    {
        NetworkLayer newLayer {.proto = packet.getNetworkProtocol()};

        switch (packet.getNetworkProtocol())
        {
            case NetworkProtocol::ARP:
            case NetworkProtocol::ICMP:
            case NetworkProtocol::RIPv1:
            case NetworkProtocol::RIPv2:
            case NetworkProtocol::NONE:
                // Create new Network element flow element and node
                std::set<Netv4DstSrc>* newNetSet = new std::set<Netv4DstSrc>();
                unsigned long int newDstSrcSumm = FlowIdCalc::summIpv4(packet.getIPv4Dst(), packet.getIPv4Src());
                flow_id newFlowId = this->getNextFlowId();
                Netv4DstSrc newFlowLeaf = {
                    .dstSrcSumm = newDstSrcSumm, 
                    .flowId = newFlowId};
                newNetSet->insert(newFlowLeaf);
                NetworkLayer newProtocolNode = {
                    .proto = packet.getNetworkProtocol(),
                    .setNetv4DstSrc = newNetSet,
                };
                // insert it
                this->netFlowsStack->insert(newProtocolNode);
                break;
            case NetworkProtocol::ICMPv6:
                // Create new Network element flow element and node
                std::set<Netv6DstSrc>* newNetSet = new std::set<Netv6DstSrc>();
                unsigned long int newDstSrcHash = FlowIdCalc::hashStrings(packet.getIPv6Dst(), packet.getIPv6Src());
                flow_id newFlowId = this->getNextFlowId();
                Netv6DstSrc newFlowLeaf = {
                    .dstSrcHash = newDstSrcHash, 
                    .flowId = newFlowId};
                newNetSet->insert(newFlowLeaf);
                NetworkLayer newProtocolNode = {
                    .proto = packet.getNetworkProtocol(),
                    .setNetv4DstSrc = newNetSet
                };
                // insert it
                this->netFlowsStack->insert(newProtocolNode);
                break;
            case NetworkProtocol::IPv4 :
                // Create new Network element flow element and node
                flow_id newFlowId = this->getNextFlowId();
                unsigned long int newDstSrcSumm = FlowIdCalc::summPorts(packet.getPortDst(), packet.getPortSrc());
                PortDstSrc flowLeaf = {
                    .dstSrcSumm = newDstSrcSumm,
                    .flowId = newFlowId,
                };
                std::set<PortDstSrc>* nodePort = new std::set<PortDstSrc>();
                nodePort->insert(flowLeaf);

                TransportLayer transportNode = {
                    .proto = packet.getTransportProtocol(),
                    .setPortDstSrc = nodePort,
                };
                std::set<TransportLayer>* newSetTransport = new std::set<TransportLayer>();
                newSetTransport->insert(transportNode);    
                unsigned long int newIpDstSrcSumm = FlowIdCalc::summIpv4(packet.getIPv4Dst(), packet.getIPv4Src());
                Ipv4DstSrc newNetSummNode = {
                    .dstSrcSumm = newIpDstSrcSumm, 
                    .setTransport = newSetTransport,
                };
                std::set<Ipv4DstSrc>* newSetNetAddr = new std::set<Ipv4DstSrc>();
                newSetNetAddr->insert(newNetSummNode);

                NetworkLayer newProtocolNode = {
                    .proto = packet.getNetworkProtocol(),
                    .setIpv4DstSrc = newSetNetAddr
                };
                // insert it
                this->netFlowsStack->insert(newProtocolNode);
                break;
            case NetworkProtocol::IPv6 :

                break;
            default:
                printf("**ERROR** INVALID NETWORK PACKET");
                break;
        }


    }


    return flow_id();
}

const unsigned int FlowIdCalc::summPorts(port_number dst, port_number src)
{
    return PORT_OFFSET_VALUE*dst + src;
}

const unsigned long int FlowIdCalc::summIpv4(ipv4_address dst, ipv4_address src)
{
    return IPV4_OFFSET_VALUE*dst + src;
}

const size_t FlowIdCalc::hashStrings(std::string a, std::string b)
{
    std::hash<std::string> hasher;
    std::string strToHash = a + b;
    size_t hash = hasher(strToHash);
    return hash;
}


void FlowIdCalc::destroyNetFlowsStack()
{
}

flow_id FlowIdCalc::getNextFlowId()
{
    this->lastFlowId++;
    return this->lastFlowId.load();
}
