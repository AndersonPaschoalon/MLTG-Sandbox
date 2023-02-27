#include "QFlowPacket.h"

QFlowPacket::QFlowPacket(size_t packetId, flow_id flowId, time_stamp timeStamp, packet_size pktSize, ttl timeToLive)
{
    this->set(packetId, flowId, timeStamp, pktSize, timeToLive, false, NULL);
}

QFlowPacket::~QFlowPacket()
{
}

QFlowPacket::QFlowPacket(const QFlowPacket &obj)
{
    this->set(obj.pktId, obj.flowId, obj.timeStamp, obj.pktSize, obj.timeToLive, obj.readyToFree, obj.nextPacket);
}

QFlowPacket &QFlowPacket::operator=(QFlowPacket other)
{
    if(this != &other)
    {
        this->set(other.pktId, other.flowId, other.timeStamp, other.pktSize, other.timeToLive, other.readyToFree, other.nextPacket);
    }        
    return *this;
}

std::string QFlowPacket::toString()
{
    std::string pktData = "{packetID:" + std::to_string(this->pktId) +
                          ", flowId:" + std::to_string(this->flowId) + 
                          ", timeStamp:" + std::to_string(this->timeStamp) + 
                          ", packetSize:" + std::to_string(this->pktSize) + 
                          ", ttl" + std::to_string(this->timeToLive)  + "}";
    return pktData;
}

size_t QFlowPacket::packetId()
{
    return this->pktId;
}

time_stamp QFlowPacket::getTimeStamp()
{
    return this->timeStamp;
}

packet_size QFlowPacket::getPacketSize()
{
    return this->pktSize;
}

ttl QFlowPacket::getTtl()
{
    return this->timeToLive;
}

void QFlowPacket::setNext(QFlowPacket *nextNode)
{
    this->nextPacket = nextNode;
}

QFlowPacket *QFlowPacket::next()
{
    return this->nextPacket;
}

void QFlowPacket::setDelete(bool toDelete)
{
    this->readyToFree = toDelete;
}

bool QFlowPacket::getDelete()
{
    return this->readyToFree;
}

void QFlowPacket::set(size_t pktId, flow_id flowId, time_stamp timeStamp, packet_size pktSize, ttl timeToLive, bool readyToFree, QFlowPacket* nextPacket)
{
    this->pktId = pktId;
    this->flowId = flowId;
    this->timeStamp = timeStamp;
    this->pktSize = pktSize;
    this->timeToLive = timeToLive;
}
