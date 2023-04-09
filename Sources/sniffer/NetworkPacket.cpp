#include "NetworkPacket.h"

NetworkPacket::NetworkPacket()
{
    this->packetId = 0;
    this->packetSize = 0;
    this->timeStamp.sec = 0;
    this->timeStamp.usec = 0;
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
    // nothing to do
}

NetworkPacket::NetworkPacket(const NetworkPacket &obj)
{
    this->packetId = obj.packetId;
    this->packetSize = obj.packetSize;
    this->timeStamp.sec = obj.timeStamp.sec;
    this->timeStamp.usec = obj.timeStamp.usec;
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
        this->packetId = other.packetId;
        this->packetSize = other.packetSize;
        this->timeStamp.sec = other.timeStamp.sec;
        this->timeStamp.usec = other.timeStamp.usec;
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
    return std::string("{ packetSize:") + std::to_string(this->packetSize) + 
           std::string(", timeStamp:") + std::to_string(this->timeStamp.sec) + std::string("s ") +  std::to_string(this->timeStamp.usec) + std::string("us") + 
           std::string(", packetId:") + std::to_string(this->packetId) +
		   std::string(", flowId:") + std::to_string(this->flowId) +
           std::string(", networkProtocol:") + to_string(this->networkProtocol) +
		   std::string(", transportProtocol:") + to_string(this->transportProtocol) +
           std::string(", aplicationProtocol:") + to_string(this->aplicationProtocol) +
		   std::string(", portDst:") + std::to_string(this->portDst) +
		   std::string(", portSrc:") + std::to_string(this->portSrc) +
		   std::string(", ipv4Dst:") + std::to_string(this->ipv4Dst) +
		   std::string(", ipv4Src:") + std::to_string(this->ipv4Src) +
		   std::string(", ipv6Dst:") + this->ipv6Dst +
		   std::string(", ipv6Src:") + this->ipv6Src +
		   std::string(", timeToLive:") + std::to_string(this->timeToLive) +		   
           std::string(", comment:") + this->comment + std::string("}");
}

std::string NetworkPacket::about()
{
    return this->comment;
}

size_t NetworkPacket::getPacketId()
{
    return this->packetId;
}

packet_size NetworkPacket::getPacketSize()
{
    return this->packetSize;
}

PacketTimeStamp NetworkPacket::getTimestamp()
{
    return this->timeStamp;
}

void NetworkPacket::setPysical(size_t pktId, packet_size packetSize, PacketTimeStamp& timestamp)
{
    this->packetId = pktId;
    this->packetSize = packetSize;
    this->timeStamp.sec = timestamp.sec;
    this->timeStamp.usec = timestamp.usec;
}

flow_id NetworkPacket::getFlowId()
{
    return this->flowId;
}

void NetworkPacket::setFlowId(flow_id flowId)
{
    this->flowId = flowId;
}

void NetworkPacket::setLink(LinkProtocol proto)
{
    this->linkProtocol = proto;
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

void NetworkPacket::setNetwork(NetworkProtocol proto, ipv4_address ipSrc, ipv4_address ipDst, ttl timeToLive)
{
    this->networkProtocol = proto;
    this->ipv4Src = ipSrc;
    this->ipv4Dst = ipDst;
    this->timeToLive = timeToLive;
}

void NetworkPacket::setNetwork(NetworkProtocol proto)
{
    this->networkProtocol = proto;
    this->ipv4Src = IPV4_NONE;
    this->ipv4Dst = IPV4_NONE;
}

void NetworkPacket::setNetworkV6(NetworkProtocol proto, std::string src, std::string dst, ttl hopLimit)
{
    this->networkProtocol = proto;
    this->ipv6Src = src;
    this->ipv6Dst = dst;    
    this->timeToLive = hopLimit;
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

void NetworkPacket::setTransport(TransportProtocol proto)
{
    this->transportProtocol = proto;
    this->portSrc = PORT_NONE;
    this->portDst = PORT_NONE;   
}

ApplicationProtocol NetworkPacket::getApplicationProtocol()
{
    return this->aplicationProtocol;
}

void NetworkPacket::setApplication(ApplicationProtocol app)
{
    this->aplicationProtocol = app;
}
