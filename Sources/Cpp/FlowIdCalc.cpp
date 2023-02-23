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
    ipv4_address srcIp = 0x0;
    ipv4_address dstIp = 0x0;
    port_number srcPort = 0x0;
    port_number dstPort = 0x0;
    flow_id flowId = 0;
    std::string dump = "";
    // iter over all main set elements
    std::set<NetworkLayer>::iterator itrL1;
    for (itrL1 = this->netFlowsStack->begin();   itrL1 != this->netFlowsStack->end(); itrL1++)
    {

        dump += "# Protocol " + to_string(itrL1->proto) + "\n";
        // setNetv4DstSrc
        if (itrL1->setNetv4DstSrc != NULL)
        {
            std::set<Netv4DstSrc>::iterator itrL2;
            for (itrL2 = itrL1->setNetv4DstSrc->begin();   itrL2 !=itrL1->setNetv4DstSrc->end(); itrL2++)
            {
                srcIp = 0x0;
                dstIp = 0x0;
                FlowIdCalc::recoverIpv4(itrL2->dstSrcSumm, dstIp, srcIp);
                dump += "flow:" + std::to_string(itrL2->flowId) + 
                        ", net:" + to_string(itrL1->proto) + 
                        ", netSrc:" + hexToDottedDecimal(srcIp) + 
                        ", netDst:" + hexToDottedDecimal(dstIp) + "\n";
            }
        }

        // setNetv6DstSrc
        if (itrL1->setNetv6DstSrc != NULL)
        {
            
        }

        // setIpv4DstSrc
        if (itrL1->setIpv4DstSrc != NULL)
        {
            NetworkProtocol netProto = itrL1->proto;
            std::set<Ipv4DstSrc>::iterator itrL2;
            for (itrL2 = itrL1->setIpv4DstSrc->begin();   itrL2 !=itrL1->setIpv4DstSrc->end(); itrL2++)
            {
                srcIp = 0x0;
                dstIp = 0x0;
                FlowIdCalc::recoverIpv4(itrL2->dstSrcSumm, dstIp, srcIp);
                std::set<TransportLayer>::iterator itrL3;
                for (itrL3 = itrL2->setTransport->begin();   itrL3 !=itrL2->setTransport->end(); itrL3++)
                {
                    TransportProtocol transProto = itrL3->proto;
                    dump += "# Protocol " + to_string(netProto) + "/" +  to_string(transProto) + "\n";
                    std::set<PortDstSrc>::iterator itrL4;
                    for (itrL4 = itrL3->setPortDstSrc->begin();   itrL4 !=itrL3->setPortDstSrc->end(); itrL4++)
                    {
                        srcPort = 0;
                        dstPort = 0;
                        flowId = itrL4->flowId;
                        FlowIdCalc::recoverPorts(itrL4->dstSrcSumm, dstPort, srcPort);
                        dump += "flow:" + std::to_string(flowId) + 
                                ", net:" + to_string(netProto) + 
                                ", netSrc:" + hexToDottedDecimal(srcIp) + 
                                ", netDst:" + hexToDottedDecimal(dstIp) +
                                ", trans:" + to_string(transProto) +
                                ", portSrc:" + std::to_string(srcPort) +
                                ", portDst:" + std::to_string(dstPort) + "\n";
                    }
                }
            }            
            
        }

        // setIpv6DstSrc
        if (itrL1->setIpv6DstSrc != NULL)
        {
            
        }

    }

    return dump;
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
            {
                netKey = FlowIdCalc::summIpv4(packet.getIPv4Dst(), packet.getIPv4Src()); 
                Ipv4DstSrc keyToSearch4 = {.dstSrcSumm=netKey,};

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
                        // search port hash 
                        flow_hash portKey = FlowIdCalc::summPorts(packet.getPortDst(), packet.getPortSrc()); 
                        PortDstSrc portObj = {.dstSrcSumm=portKey};
                        if (auto searchPortPair = searchTransportProto->setPortDstSrc->find(portObj);  
                            searchPortPair != searchTransportProto->setPortDstSrc->end())
                        {
                            // Port pair found!
                            actualFlowId = searchPortPair->flowId;
                        }
                        else
                        {
                            // port pair not found, insert a new one in the transport branch!
                            actualFlowId = FlowIdCalc::getNextFlowId();
                            // fill the objects
                            portObj.flowId = actualFlowId;
                            searchTransportProto->setPortDstSrc->insert(portObj);
                        }
                    }
                    else
                    {
                        // transport not found
                        // therefore the flow does not exist, and we must add it!
                        actualFlowId = FlowIdCalc::getNextFlowId();
                        // fill the objects
                        flow_hash portHash = FlowIdCalc::summPorts(packet.getPortDst(), packet.getPortSrc());
                        PortDstSrc portObj = {
                            .dstSrcSumm = portHash,
                            .flowId = actualFlowId,
                        };
                        std::set<PortDstSrc>* setPorts = new std::set<PortDstSrc>();
                        setPorts->insert(portObj);
                        transKey.setPortDstSrc = setPorts;
                        // inset new trans protocol;
                        searchNetAddr->setTransport->insert(transKey);
                    }
                }
                else
                {
                    // not found => therefore a new node with a new flow id must be included
                    actualFlowId = FlowIdCalc::getNextFlowId();
                    // fill search object with the propper data
                    // porObj -> set ports -> transport obj -> set transport 
                    flow_hash portHash = FlowIdCalc::summPorts(packet.getPortDst(), packet.getPortSrc());
                    PortDstSrc portObj = {
                        .dstSrcSumm = portHash,
                        .flowId = actualFlowId,
                    };
                    std::set<PortDstSrc>* setPorts = new std::set<PortDstSrc>();
                    setPorts->insert(portObj);
                    TransportLayer newTransportLayer = {
                        .proto = packet.getTransportProtocol(),
                        .setPortDstSrc = setPorts,
                    };
                    std::set<TransportLayer>* setTransport = new std::set<TransportLayer>();
                    keyToSearch4.setTransport = setTransport;
                    keyToSearch4.dstSrcSumm = netKey;
                    // insert the node on ip set
                    netNode->setIpv4DstSrc->insert(keyToSearch4);
                }
            }

                break;
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

flow_id FlowIdCalc::getCurrentFlowId()
{
    return this->lastFlowId.load();
}

const flow_hash FlowIdCalc::summPorts(port_number dst, port_number src)
{
    return PORT_OFFSET_VALUE*dst + src;
}

const void FlowIdCalc::recoverPorts(flow_hash summ, port_number &dst, port_number &src)
{
    unsigned long int lsbValue = summ & PORT_LSB_MASK;
    unsigned long int msbValue = (summ & PORT_MSB_MASK) >> 16;
    src = (port_number)lsbValue;
    dst = (port_number)msbValue;
    return;
}

const unsigned long int FlowIdCalc::summIpv4(ipv4_address dst, ipv4_address src)
{
    return IPV4_OFFSET_VALUE*dst + src;
}

const void FlowIdCalc::recoverIpv4(flow_hash summ, ipv4_address &dst, ipv4_address &src)
{
    unsigned long int lsbValue = summ & IPV4_LSB_MASK;
    unsigned long int msbValue = (summ & IPV4_MSB_MASK) >> 16*2;
    src = (ipv4_address)lsbValue;
    dst = (ipv4_address)msbValue;
    return;
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
