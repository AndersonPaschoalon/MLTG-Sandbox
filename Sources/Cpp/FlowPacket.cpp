#include "FlowPacket.h"

FlowPacket::FlowPacket(double timeStamp, unsigned int packetSize, ttl timeToLive)
{
    this->packetSize = packetSize;
    this->timeStamp = timeStamp;
    this->timeToLive = timeToLive;
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
