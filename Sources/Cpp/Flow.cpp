#include "Flow.h"

Flow::Flow()
{
    this->packetList = new std::vector<FlowPacket>();
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
    this->packetList->clear();
    delete this->packetList;
}

Flow::Flow(const Flow &obj)
{
    this->flowId = obj.flowId;
    this->ipv4Dst = obj.ipv4Dst;
    this->ipv4Src = obj.ipv4Src;
    this->ipv6Dst = obj.ipv6Dst;
    this->ipv6Src = obj.ipv6Src;
    this->portDst = obj.portDst;
    this->portSrc = obj.portSrc;    
}

Flow &Flow::operator=(Flow other)
{
    if(this != &other)
    {
        this->flowId = other.flowId;
        this->ipv4Dst = other.ipv4Dst;
        this->ipv4Src = other.ipv4Src;
        this->ipv6Dst = other.ipv6Dst;
        this->ipv6Src = other.ipv6Src;
        this->portDst = other.portDst;
        this->portSrc = other.portSrc;
    }        
    return *this;
}

std::string Flow::toString()
{
    return "Flow";
}

void Flow::set(flow_id flowId, time_stamp timeStamp, NetworkProtocol n, ipv4_address src, ipv4_address dst)
{
    this->flowId = flowId;
    this->startTime = timeStamp;
    this->networkProtocol = n;
    this->ipv4Src = src;
    this->ipv4Dst = dst;
}

void Flow::set(flow_id flowId, time_stamp timeStamp, NetworkProtocol n, const std::string &ipv6Src, const std::string &ipv6Dst)
{
    this->flowId = flowId;
    this->startTime = timeStamp;
    this->networkProtocol = n;
    this->ipv6Src = ipv6Src;
    this->ipv6Dst = ipv4Dst;
}

void Flow::set(flow_id flowId, time_stamp timeStamp, NetworkProtocol n, ipv4_address ipsrc, ipv4_address ipdst, TransportProtocol t, port_number portSrc, port_number portDst, ApplicationProtocol app)
{
    this->flowId = flowId;
    this->startTime = timeStamp;
    this->networkProtocol = n;
    this->ipv4Src = ipsrc;
    this->ipv4Dst = ipdst;
    this->transportProtocol = t;
    this->portDst = portDst;
    this->portSrc = portSrc;
    this->applicationProtocol = app;
}

void Flow::set(flow_id flowId, time_stamp timeStamp, NetworkProtocol n, const std::string &ipv6Src, const std::string &ipv6Dst, TransportProtocol t, port_number portSrc, port_number portDst, ApplicationProtocol app)
{
    this->flowId = flowId;
    this->startTime = timeStamp;
    this->networkProtocol = n;
    this->ipv6Src = ipv6Src;
    this->ipv6Dst = ipv6Dst;
    this->transportProtocol = t;
    this->portDst = portDst;
    this->portSrc = portSrc;
    this->applicationProtocol = app;
}

void Flow::addPacket(FlowPacket pkt)
{
    this->packetList->push_back(pkt);
}
