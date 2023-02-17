#include "Flow.h"

Flow::Flow()
{
    this->packetList = new std::vector<FlowPacket*>();
    this->packetList->clear();
    this->flowId = 0;
    this->ipv4Dst = IPV4_NONE;
    this->ipv4Src = IPV4_NONE;
    this->ipv6Dst = "";
    this->ipv6Src = "";
    this->portDst = PORT_NONE;
    this->portSrc = PORT_NONE;
}

Flow::~Flow()
{
    for (FlowPacket* pkt : *this->packetList)
    {
        delete pkt;
    }
    this->packetList->clear();
    delete this->packetList;
}
