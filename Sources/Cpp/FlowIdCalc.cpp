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
    flow_id actualFlowId = 0;
    flow_hash newDstSrcSumm = 0;
    flow_hash newDstSrcHash = 0;
    flow_hash netKey = 0;
    NetworkProtocol currentProtocol = packet.getNetworkProtocol();
    NetworkLayer packetProto = {.proto=currentProtocol};
    auto netNode = this->netFlowsStack->find(packetProto);
    if (netNode != this->netFlowsStack->end()) // there is packets of this protocol, and it is stored on the current pointer
    {

        switch (currentProtocol)
        {
            case NetworkProtocol::ARP:
            case NetworkProtocol::ICMP:
            case NetworkProtocol::RIPv1:
            case NetworkProtocol::RIPv2:
            case NetworkProtocol::NONE:
            {
                netKey = FlowIdCalc::summIpv4(packet.getIPv4Dst(), packet.getIPv4Src()); 
                Netv4DstSrc keyToSearch = {.dstSrcSumm=netKey,};
                if (auto search = netNode->setNetv4DstSrc->find(keyToSearch); search != netNode->setNetv4DstSrc->end())
                {
                    // there is already a node with the key netKey, therefore this flow already exist!
                    // found at (*search)
                    actualFlowId = search->flowId;
                }
                else
                {
                    // not found => therefore a new node with a new flow id must be included
                    actualFlowId = FlowIdCalc::getNextFlowId();
                    keyToSearch.flowId = actualFlowId;
                    LOGGER(DEBUG, "New {%s} flow {%lu}", to_string(currentProtocol).c_str(), actualFlowId);
                    netNode->setNetv4DstSrc->insert(keyToSearch);
                }
                break;
            }
            case NetworkProtocol::ICMPv6:
            {
                netKey = FlowIdCalc::hashStrings(packet.getIPv6Dst(), packet.getIPv6Src()); 
                Netv6DstSrc keyToSearch6 = {.dstSrcHash=netKey,};
                if (auto search = netNode->setNetv6DstSrc->find(keyToSearch6); search != netNode->setNetv6DstSrc->end())
                {
                    // there is already a node with the key netKey, therefore this flow already exist!
                    // found at (*search)
                    actualFlowId = search->flowId;
                }
                else
                {
                    // not found => therefore a new node with a new flow id must be included
                    actualFlowId = FlowIdCalc::getNextFlowId();
                    keyToSearch6.flowId = actualFlowId;
                    LOGGER(DEBUG, "New {%s} flow {%lu}", to_string(currentProtocol).c_str(), actualFlowId);
                    netNode->setNetv6DstSrc->insert(keyToSearch6);
                }
                break;
            }
            case NetworkProtocol::IPv4 :
            /*
                unsigned long int ipv4Key = FlowIdCalc::summIpv4(packet.getIPv4Dst(), packet.getIPv4Src()); 
                Ipv4DstSrc keyToSearch4 = {.dstSrcSumm=ipv4Key,};

                if (auto searchNetAddr = netNode->setIpv4DstSrc->find(keyToSearch4); searchNetAddr != netNode->setIpv4DstSrc->end())
                {
                    // there is already a node with the key netKey
                    // but we must check at the transport layer to find if there is a flow or not
                    // found at (*search)
                    TransportLayer transKey = {packet.getTransportProtocol()};
                    // search transport protocol on searchNetAddr
                    if (auto searchTransportProto = searchNetAddr->setTransport->find(transKey); searchTransportProto != searchNetAddr->setTransport->end())
                    {
                        // transport found!

                    }
                    else
                    {
                        // transport not found
                        // therefore the flow does not exist, and we must add it!
                        
                    }
                    



                }
                else
                {
                    // not found => therefore a new node with a new flow id must be included
                    actualFlowId = FlowIdCalc::getNextFlowId();
                    keyToSearch.flowId = actualFlowId;
                    netNode->setNetv4DstSrc->insert(keyToSearch);
                }
                break;
            **/
            case NetworkProtocol::IPv6 :
                break;
            default:
                LOGGER(ERROR, "**ERROR** INVALID NETWORK PACKET");
                break;
        }

    }
    else // no packet of this network protocol was found yet
    {
        LOGGER(DEBUG, "* No packet of this network protocol {%s} was found yet.\n", to_string(currentProtocol).c_str());
        switch (currentProtocol)
        {
            case NetworkProtocol::ARP:
            case NetworkProtocol::ICMP:
            case NetworkProtocol::RIPv1:
            case NetworkProtocol::RIPv2:
            case NetworkProtocol::NONE:
            {
                // Create new Network element flow element and node
                std::set<Netv4DstSrc>* newNetSet = new std::set<Netv4DstSrc>();
                newDstSrcSumm = FlowIdCalc::summIpv4(packet.getIPv4Dst(), packet.getIPv4Src());
                actualFlowId = this->getNextFlowId();
                Netv4DstSrc newFlowLeaf = {
                    .dstSrcSumm = newDstSrcSumm, 
                    .flowId = actualFlowId};
                newNetSet->insert(newFlowLeaf);
                NetworkLayer newProtocolNode = {
                    .proto = packet.getNetworkProtocol(),
                    .setNetv4DstSrc = newNetSet,
                };
                // insert it
                this->netFlowsStack->insert(newProtocolNode);
                break;
            }
            case NetworkProtocol::ICMPv6:
            {
                // Create new Network element flow element and node
                std::set<Netv6DstSrc>* newNetSet = new std::set<Netv6DstSrc>();
                newDstSrcHash = FlowIdCalc::hashStrings(packet.getIPv6Dst(), packet.getIPv6Src());
                actualFlowId = this->getNextFlowId();
                Netv6DstSrc newFlowLeafn6 = {
                    .dstSrcHash = newDstSrcHash, 
                    .flowId = actualFlowId};
                newNetSet->insert(newFlowLeafn6);
                NetworkLayer newProtocolNode = {
                    .proto = packet.getNetworkProtocol(),
                    .setNetv6DstSrc = newNetSet
                };
                // insert it
                this->netFlowsStack->insert(newProtocolNode);
                break;
            }
            case NetworkProtocol::IPv4 :
            {
                // Create new Network element flow element and node
                actualFlowId = this->getNextFlowId();
                newDstSrcSumm = FlowIdCalc::summPorts(packet.getPortDst(), packet.getPortSrc());
                PortDstSrc flowLeaf4 = {
                    .dstSrcSumm = newDstSrcSumm,
                    .flowId = actualFlowId,
                };
                std::set<PortDstSrc>* nodePort = new std::set<PortDstSrc>();
                nodePort->insert(flowLeaf4);

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
            }
            case NetworkProtocol::IPv6 :
            {
                // Create new Network element flow element and node
                actualFlowId = this->getNextFlowId();
                newDstSrcSumm = FlowIdCalc::summPorts(packet.getPortDst(), packet.getPortSrc());
                PortDstSrc flowLeaf6 = {
                    .dstSrcSumm = newDstSrcSumm,
                    .flowId = actualFlowId,
                };
                std::set<PortDstSrc>* nodePort = new std::set<PortDstSrc>();
                nodePort->insert(flowLeaf6);

                TransportLayer transportNode = {
                    .proto = packet.getTransportProtocol(),
                    .setPortDstSrc = nodePort,
                };
                std::set<TransportLayer>* newSetTransport = new std::set<TransportLayer>();
                newSetTransport->insert(transportNode);    
                newDstSrcHash = FlowIdCalc::hashStrings(packet.getIPv6Dst(), packet.getIPv6Src());
                Ipv6DstSrc newNetSummNode = {
                    .dstSrcHash = newDstSrcHash,
                    .setTransport = newSetTransport,
                };
                std::set<Ipv6DstSrc>* newSetNetAddr = new std::set<Ipv6DstSrc>();
                newSetNetAddr->insert(newNetSummNode);

                NetworkLayer newProtocolNode = {
                    .proto = packet.getNetworkProtocol(),
                    .setIpv6DstSrc = newSetNetAddr
                };
                // insert it
                this->netFlowsStack->insert(newProtocolNode);
                break;
            }                
            default:
            {
                LOGGER(ERROR, "**ERROR** INVALID NETWORK PACKET {%s}\n", to_string(currentProtocol).c_str());
                break;
            }
        }
    }

    // now, set and return the flow id
    packet.setFlowId(actualFlowId);
    return actualFlowId;
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
