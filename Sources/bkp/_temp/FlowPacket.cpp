#include "FlowPacket.h"

FlowPacket::FlowPacket(time_stamp timeStamp, packet_size packetSize, ttl timeToLive)
{
    this->packetSize = packetSize;
    this->timeStamp = timeStamp;
    this->timeToLive = timeToLive;
}

FlowPacket::~FlowPacket()
{
}

FlowPacket::FlowPacket(const FlowPacket &obj)
{
    this->timeStamp = obj.timeStamp;
    this->packetSize = obj.packetSize;
    this->timeToLive = obj.timeToLive;
}

FlowPacket &FlowPacket::operator=(FlowPacket other)
{
    if (this != &other)
    {
        this->timeStamp = other.timeStamp;
        this->packetSize = other.packetSize;
        this->timeToLive = other.timeToLive;
    }
    return *this;

}

time_stamp FlowPacket::getTimeStamp()
{
    return this->timeStamp;
}

packet_size FlowPacket::getPacketSize()
{
    return this->packetSize;
}

ttl FlowPacket::getTtl()
{
    return this->timeToLive;
}
