#include "FlowIdCalc.h"

FlowIdCalc::FlowIdCalc()
{
    this->lastFlowId = 0;
    this->netFlowsStack = new std::set<NetworkLayer>();
}

FlowIdCalc::~FlowIdCalc()
{
    std::set<NetworkLayer>::iterator it;
    for(it = this->netFlowsStack->begin(); it != this->netFlowsStack->end(); it++)
    {
        if(it->setNetv4DstSrc != NULL)
        {
            it->setNetv4DstSrc->clear();
            delete it->setNetv4DstSrc;
        }
        if(it->setNetv6DstSrc != NULL)
        {
            it->setNetv6DstSrc->clear();
            delete it->setNetv6DstSrc;
        }
        if(it->setIpv4DstSrc != NULL)
        {
            // free set IPV4
            std::set<Ipv4DstSrc>* s4 = it->setIpv4DstSrc;

            std::set<Ipv4DstSrc>::iterator it4;
            for (it4 = s4->begin(); it4 != s4->end(); ++it4)
            {
                // free Set Transport
                std::set<TransportLayer>* sT = it4->setTransport;

                std::set<TransportLayer>::iterator itT;
                for (itT = sT->begin(); itT != sT->end(); ++itT)
                {
                    // free set Ports
                    std::set<PortDstSrc>* sP = itT->setPortDstSrc;

                    sP->clear();

                    delete sP;
                }

                delete sT;
            }


           delete s4;
        }
        if(it->setIpv6DstSrc != NULL)
        {
            // free set IPV4
            std::set<Ipv6DstSrc>* s6 = it->setIpv6DstSrc;

            std::set<Ipv6DstSrc>::iterator it6;
            for (it6 = s6->begin(); it6 != s6->end(); ++it6)
            {
                // free Set Transport
                std::set<TransportLayer>* sT = it6->setTransport;

                std::set<TransportLayer>::iterator itT;
                for (itT = sT->begin(); itT != sT->end(); ++itT)
                {
                    // free set Ports
                    std::set<PortDstSrc>* sP = itT->setPortDstSrc;

                    sP->clear();

                    delete sP;
                }

                delete sT;
            }

           delete s6;
        }
    }

    this->netFlowsStack->clear();
    delete this->netFlowsStack;
    this->netFlowsStack = nullptr;
}

//FlowIdCalc::FlowIdCalc(const FlowIdCalc &obj)
//{
//}

//FlowIdCalc &FlowIdCalc::operator=(FlowIdCalc other)
//{
//    // TODO: insert return statement here
//}

std::string FlowIdCalc::toString()
{
    ipv4_address srcIp = 0x0;
    ipv4_address dstIp = 0x0;
    port_number srcPort = 0x0;
    port_number dstPort = 0x0;
    flow_hash netAddrHash = 0x0;
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
                        ", netSrc:" + hex_to_dotted_decimal(srcIp) + 
                        ", netDst:" + hex_to_dotted_decimal(dstIp) + "\n";
            }
        }

        // setNetv6DstSrc
        if (itrL1->setNetv6DstSrc != NULL)
        {
            std::set<Netv6DstSrc>::iterator itrL2;
            for (itrL2 = itrL1->setNetv6DstSrc->begin();   itrL2 !=itrL1->setNetv6DstSrc->end(); itrL2++)
            {
                dump += "flow:" + std::to_string(itrL2->flowId) + 
                        ", net:" + to_string(itrL1->proto) + 
                        ", netHash:" + std::to_string(itrL2->dstSrcHash) + "\n";
            }            
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
                                ", netSrc:" + hex_to_dotted_decimal(srcIp) + 
                                ", netDst:" + hex_to_dotted_decimal(dstIp) +
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
            NetworkProtocol netProto = itrL1->proto;
            std::set<Ipv6DstSrc>::iterator itrL2;
            for (itrL2 = itrL1->setIpv6DstSrc->begin();   itrL2 !=itrL1->setIpv6DstSrc->end(); itrL2++)
            {
                netAddrHash = itrL2->dstSrcHash;
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
                                ", netAddrHash:" + std::to_string(netAddrHash) + 
                                ", trans:" + to_string(transProto) +
                                ", portSrc:" + std::to_string(srcPort) +
                                ", portDst:" + std::to_string(dstPort) + "\n";
                    }
                }
            }   


        }

    }

    return dump;
}

flow_id FlowIdCalc::setFlowId(NetworkPacket &packet)
{
    // TODO Criar um set somente para pacotes tcp/ip, para tornar o algoritimo mais eficiente.
    // check if the nework packet is already on the set
    flow_id actualFlowId = 0;
    flow_hash newDstSrcSumm = 0;
    flow_hash newDstSrcHash = 0;
    flow_hash netKey = 0;
    NetworkProtocol currentProtocol = packet.getNetworkProtocol();
    NetworkLayer packetProtoKey = {.proto=currentProtocol};
    if (auto netNode = this->netFlowsStack->find(packetProtoKey); netNode != this->netFlowsStack->end()) 
    {
        // there is packets of this protocol, and it is stored on the current pointer
        switch (currentProtocol)
        {
            // Non-IP packets
            case NetworkProtocol::ARP:
            case NetworkProtocol::RARP:
            case NetworkProtocol::LOOPBACK:           
            case NetworkProtocol::ATA:
            case NetworkProtocol::WOL:
            case NetworkProtocol::NONE:
            {
                // if the net protocol doent have ip, it will be set as IPV4_NONE
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
            /*
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
            **/
           // IPV4 packets
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
                    setTransport->insert(newTransportLayer);
                    keyToSearch4.setTransport = setTransport;
                    keyToSearch4.dstSrcSumm = netKey;
                    // insert the node on ip set
                    netNode->setIpv4DstSrc->insert(keyToSearch4);
                }
                break;
            }
            // IPV6 packets
            case NetworkProtocol::IPv6 :
            {
                netKey = FlowIdCalc::hashStrings(packet.getIPv6Dst(), packet.getIPv6Src()); 
                Ipv6DstSrc keyToSearch6 = {.dstSrcHash=netKey,};

                if (auto searchNetAddr = netNode->setIpv6DstSrc->find(keyToSearch6); searchNetAddr != netNode->setIpv6DstSrc->end())
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
                    setTransport->insert(newTransportLayer);
                    keyToSearch6.setTransport = setTransport;
                    keyToSearch6.dstSrcHash= netKey;
                    // insert the node on ip set
                    netNode->setIpv6DstSrc->insert(keyToSearch6);
                }
                break;
            }
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
            case NetworkProtocol::RARP:
            case NetworkProtocol::LOOPBACK:           
            case NetworkProtocol::ATA:
            case NetworkProtocol::WOL:
            case NetworkProtocol::NONE:
            {
                // Create new Network element flow element and node
                actualFlowId = this->getNextFlowId();
                std::set<Netv4DstSrc>* newNetSet = new std::set<Netv4DstSrc>();
                newDstSrcSumm = FlowIdCalc::summIpv4(packet.getIPv4Dst(), packet.getIPv4Src());
                Netv4DstSrc newFlowLeaf = {
                    .dstSrcSumm = newDstSrcSumm, 
                    .flowId = actualFlowId};
                newNetSet->insert(newFlowLeaf);
                packetProtoKey.setNetv4DstSrc = newNetSet;
                // insert it
                this->netFlowsStack->insert(packetProtoKey);
                break;
            }
            /*
            case NetworkProtocol::ICMPv6:
            {
                // Create new Network element flow element and node
                actualFlowId = this->getNextFlowId();
                std::set<Netv6DstSrc>* newNetSet = new std::set<Netv6DstSrc>();
                newDstSrcHash = FlowIdCalc::hashStrings(packet.getIPv6Dst(), packet.getIPv6Src());
                Netv6DstSrc newFlowLeafn6 = {
                    .dstSrcHash = newDstSrcHash, 
                    .flowId = actualFlowId};
                newNetSet->insert(newFlowLeafn6);
                packetProtoKey.setNetv6DstSrc = newNetSet;
                // insert it
                this->netFlowsStack->insert(packetProtoKey);
                break;
            }
            **/
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
                flow_hash newIpDstSrcSumm = FlowIdCalc::summIpv4(packet.getIPv4Dst(), packet.getIPv4Src());
                Ipv4DstSrc newNetSummNode = {
                    .dstSrcSumm = newIpDstSrcSumm, 
                    .setTransport = newSetTransport,
                };
                std::set<Ipv4DstSrc>* newSetNetAddr = new std::set<Ipv4DstSrc>();
                newSetNetAddr->insert(newNetSummNode);

                packetProtoKey.setIpv4DstSrc  = newSetNetAddr;
                // insert it
                this->netFlowsStack->insert(packetProtoKey);
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

                packetProtoKey.setIpv6DstSrc  = newSetNetAddr;
                // insert it
                this->netFlowsStack->insert(packetProtoKey);
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
    // return PORT_OFFSET_VALUE*dst + src;
    return zip_ports(dst, src);
}

const void FlowIdCalc::recoverPorts(flow_hash summ, port_number &dst, port_number &src)
{
    recover_ports(summ, dst, src);
}

const flow_hash FlowIdCalc::summIpv4(ipv4_address dst, ipv4_address src)
{
    return zip_ipv4(dst, src);
}

const void FlowIdCalc::recoverIpv4(flow_hash summ, ipv4_address &dst, ipv4_address &src)
{
    recover_ipv4(summ, dst, src);
}

const size_t FlowIdCalc::hashStrings(std::string a, std::string b)
{
    return hash_strings(a, b);
}

flow_id FlowIdCalc::getNextFlowId()
{
    this->lastFlowId++;
    return this->lastFlowId.load();
}
