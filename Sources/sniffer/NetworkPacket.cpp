#include "NetworkPacket.h"

NetworkPacket::NetworkPacket()
{
    this->packetSize = 0;
    this->timeStamp = 0;
    this->flowId = FLOW_ID_NONE;
    this->aplicationProtocol = ApplicationProtocol::NONE;
    this->transportProtocol = TransportProtocol::NONE;
    this->portDst = PORT_NONE;
    this->portSrc = PORT_NONE;
    this->networkProtocol = NetworkProtocol::NONE;
    this->ipv4Dst = IPV4_NONE;
    this->ipv4Src = IPV4_NONE;
    this->ipv6Dst = IPV6_NONE;
    this->ipv6Src = IPV6_NONE;
    this->timeToLive = 0;
    this->comment = "";
}

NetworkPacket::NetworkPacket(std::string comment): NetworkPacket()
{
    this->comment = comment;
}

NetworkPacket::~NetworkPacket()
{
}

NetworkPacket::NetworkPacket(const NetworkPacket &obj)
{
    this->packetSize = obj.packetSize;
    this->timeStamp = obj.timeStamp;
    this->flowId = obj.flowId;
    this->aplicationProtocol = obj.aplicationProtocol;
    this->transportProtocol = obj.transportProtocol;
    this->portDst = obj.portDst;
    this->portSrc = obj.portSrc;
    this->networkProtocol = obj.networkProtocol;
    this->ipv4Dst = obj.ipv4Dst;
    this->ipv4Src = obj.ipv4Src;
    this->ipv6Dst = obj.ipv6Dst;
    this->ipv6Src = obj.ipv6Src;
    this->timeToLive = obj.timeToLive;
    this->comment = obj.comment;
}

NetworkPacket &NetworkPacket::operator=(NetworkPacket other)
{
    if (this != &other)
    {
        this->packetSize = other.packetSize;
        this->timeStamp = other.timeStamp;
        this->flowId = other.flowId;
        this->aplicationProtocol = other.aplicationProtocol;
        this->transportProtocol = other.transportProtocol;
        this->portDst = other.portDst;
        this->portSrc = other.portSrc;
        this->networkProtocol = other.networkProtocol;
        this->ipv4Dst = other.ipv4Dst;
        this->ipv4Src = other.ipv4Src;
        this->ipv6Dst = other.ipv6Dst;
        this->ipv6Src = other.ipv6Src;
        this->timeToLive = other.timeToLive;
        this->comment = other.comment;
    }
    return *this;
}

std::string NetworkPacket::toString()
{
    return "NetworkPacket";
}

std::string NetworkPacket::about()
{
    return this->comment;
}

packet_size NetworkPacket::getPacketSize()
{
    return this->packetSize;
}

double NetworkPacket::getTimestamp()
{
    return this->timeStamp;
}

void NetworkPacket::setPysical(packet_size packetSize, time_stamp timestamp)
{
    this->packetSize = packetSize;
    this->timeStamp = timestamp;
}

flow_id NetworkPacket::getFlowId()
{
    return this->flowId;
}

void NetworkPacket::setFlowId(flow_id flowId)
{
    this->flowId = flowId;
}

NetworkProtocol NetworkPacket::getNetworkProtocol()
{
    return this->networkProtocol;
}

bool NetworkPacket::isIPv4()
{
    if(this->networkProtocol == NetworkProtocol::IPv4)
    {
        return true;
    }
    return false;
}

std::string NetworkPacket::getIPSrcStr()
{
    return "todo";
}

std::string NetworkPacket::getIPDstStr()
{
    return "todo";
}

ipv4_address NetworkPacket::getIPv4Src()
{
    return this->ipv4Src;
}

ipv4_address NetworkPacket::getIPv4Dst()
{
    return this->ipv4Dst;
}

std::string NetworkPacket::getIPv6Src()
{
    return this->ipv6Src;
}

std::string NetworkPacket::getIPv6Dst()
{
    return  this->ipv6Dst;
}

ttl NetworkPacket::getTtl()
{
    return this->timeToLive;
}

void NetworkPacket::setNetwork(NetworkProtocol proto, ipv4_address ipSrc, ipv4_address ipDst)
{
    this->networkProtocol = proto;
    this->ipv4Src = ipSrc;
    this->ipv4Dst = ipDst;
}

void NetworkPacket::setNetworkV6(NetworkProtocol proto, std::string src, std::string dst)
{
    this->networkProtocol = proto;
    this->ipv6Src = src;
    this->ipv6Dst = dst;    
}

TransportProtocol NetworkPacket::getTransportProtocol()
{
    return this->transportProtocol;
}

bool NetworkPacket::isTCPIPv4()
{
    if(this->networkProtocol == NetworkProtocol::IPv4 &&  this->transportProtocol == TransportProtocol::TCP)
    {
        return true;
    }
    return false;
}

bool NetworkPacket::isUDPIPv4()
{
    if(this->networkProtocol == NetworkProtocol::IPv4 &&  this->transportProtocol == TransportProtocol::UDP)
    {
        return true;
    }
    return false;
}

port_number NetworkPacket::getPortSrc()
{
    return this->portSrc;
}

port_number NetworkPacket::getPortDst()
{
    return this->portDst;
}

void NetworkPacket::setTransport(TransportProtocol proto, port_number src, port_number dst)
{
    this->transportProtocol = proto;
    this->portSrc = src;
    this->portDst = dst;    
}

ApplicationProtocol NetworkPacket::getApplicationProtocol()
{
    return this->aplicationProtocol;
}

void NetworkPacket::setApplication(ApplicationProtocol app)
{
    this->aplicationProtocol = app;
}