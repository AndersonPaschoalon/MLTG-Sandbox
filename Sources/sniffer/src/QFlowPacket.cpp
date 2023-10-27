#include "QFlowPacket.h"

QFlowPacket::QFlowPacket(size_t packetId, flow_id flowId, timeval& timeStamp, packet_size pktSize, ttl timeToLive)
{
    this->set(packetId, flowId, timeStamp, pktSize, timeToLive, false, nullptr);
}

QFlowPacket::~QFlowPacket()
{
    // nothing to do
}

//QFlowPacket::QFlowPacket(const QFlowPacket &obj)
//{
//    PacketTimeStamp ts;
//    ts.sec = obj.timeStamp.sec;
//    ts.usec = obj.timeStamp.usec;
//    this->set(obj.pktId, obj.flowId, ts, obj.pktSize, obj.timeToLive, obj.readyToFree, obj.nextPacket);
//}

//QFlowPacket &QFlowPacket::operator=(QFlowPacket other)
//{
//    if(this != &other)
//    {
//        this->set(other.pktId, other.flowId, other.timeStamp, other.pktSize, other.timeToLive, other.readyToFree, other.nextPacket);
//    }        
//    return *this;
//}

std::string QFlowPacket::toString()
{
    std::string pktData = "{packetID:" + std::to_string(this->pktId) +
                          ", flowId:" + std::to_string(this->flowId) + 
                          ", timeStamp:(" + std::to_string(this->timeStamp.tv_sec) + "s " +
                                           std::to_string(this->timeStamp.tv_usec) + "us)" +
                          ", packetSize:" + std::to_string(this->pktSize) + 
                          ", ttl:" + std::to_string(this->timeToLive)  + "}";
    return pktData;
}

void QFlowPacket::getQData(size_t &packetId, flow_id &fId, timeval &ts, packet_size &packetSize, ttl &time2Live)
{
    packetId  = this->pktId;
    fId = this->flowId;
    ts.tv_sec =  this->timeStamp.tv_sec;
    ts.tv_usec = this->timeStamp.tv_usec;
    packetSize = this->pktSize;
    time2Live = this->timeToLive;
}

flow_id QFlowPacket::getFlowId()
{
    return this->flowId;
}

void QFlowPacket::setNext(QFlowPacket *nextNode)
{
    this->nextPacket = nextNode;
}

QFlowPacket *QFlowPacket::next()
{
    return this->nextPacket;
}

void QFlowPacket::setCommited(bool toDelete)
{
    this->readyToFree = toDelete;
}

bool QFlowPacket::getCommited()
{
    return this->readyToFree;
}

void QFlowPacket::set(size_t pktId, flow_id flowId, timeval& timeStamp, packet_size pktSize, ttl timeToLive, bool readyToFree, QFlowPacket* nextPacket)
{
    this->pktId = pktId;
    this->flowId = flowId;
    this->timeStamp.tv_sec = timeStamp.tv_sec;
    this->timeStamp.tv_usec = timeStamp.tv_usec;
    this->pktSize = pktSize;
    this->timeToLive = timeToLive;
    this->readyToFree = readyToFree;
    this->nextPacket = nextPacket;
}
