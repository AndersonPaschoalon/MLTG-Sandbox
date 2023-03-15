#include "QTrace.h"

QTrace::QTrace(const char *traceName, const char *traceSource, const char *comment)
{
    this->set(traceName, traceSource, comment);
}

QTrace::~QTrace()
{
}

void QTrace::set(const char*  theTraceName, const char*  theTraceSource, const char*  theComment)
{
    this->traceName = std::string(theTraceName);
    this->traceSource = std::string(theTraceSource);
    this->comment = std::string(theComment);
}

std::string QTrace::toString()
{
    return std::string();
}

const std::string QTrace::getTraceName()
{
    return this->traceName;
}

const std::string QTrace::getTraceSource()
{
    return this->traceSource;
}

const std::string QTrace::getComment()
{
    return this->comment;
}

void QTrace::push(NetworkPacket &p)
{
    if (p.getFlowId() > this->lastFlow)
    {
        // add flow and packet
        QFlow* f = new QFlow();
        f->setProtocols(p.getNetworkProtocol(), p.getTransportProtocol(), p.getApplicationProtocol());
        f->setNet4Addr(p.getIPv4Dst(), p.getIPv4Src());
        f->setPorts(p.getPortDst(), p.getPortSrc());
        if(p.getIPv6Dst() != "")
        {
            f->setNet6Addr(p.getIPv6Dst().c_str(), p.getIPv6Src().c_str());
        }
        if(this->fHead == nullptr)
        {
            this->fHead = f;
        }
        if (this->fTail != nullptr)
        {
            // updata tail flow
            this->fTail->setNext(f);
        }
        f->setNext(nullptr);
        this->fTail = f;

        // update last flow
        this->lastFlow = p.getFlowId();
    }

    // add packet
    size_t packetId = p.getPacketId();
    flow_id flowId = p.getFlowId();
    PacketTimeStamp ts = p.getTimestamp();
    packet_size pktSize = p.getPacketSize();
    ttl timeToLive = p.getTtl();
    QFlowPacket* fp = new QFlowPacket(packetId, flowId, ts, pktSize, timeToLive);
    if(this->pHead == nullptr)
    {
        this->pHead = fp;
    }
    if (this->fTail != nullptr)
    {
        // update tail pkt
        this->pTail->setNext(fp);
    }
    fp->setNext(nullptr);
    this->pTail = fp;
}

void QTrace::consume(QFlow *flowHead, QFlow *flowTail, QFlowPacket *flowPacketHead, QFlowPacket *flowPacketTail)
{
    flowHead = this->fHead;
    flowTail = this->fTail;
    flowPacketHead = this->pHead;
    flowPacketTail = this->pTail;

    this->fHead = nullptr;
    this->fTail = nullptr;
    this->pHead = nullptr;
    this->pTail = nullptr;
}

void QTrace::free(QFlow *flowHead, QFlow *flowTail, QFlowPacket *flowPacketHead, QFlowPacket *flowPacketTail)
{
    QFlow *flowToDelete = nullptr;
    while (flowHead != nullptr)
    {
        flowToDelete = flowHead;
        flowHead = flowHead->next();
        if(flowToDelete == flowTail)
        {
            flowHead = nullptr;
        }
        delete flowToDelete;
    }
    flowTail = nullptr;

    QFlowPacket *flowPacketToDelete = nullptr;
    while (flowPacketHead != nullptr)
    {
        flowPacketToDelete = flowPacketHead;
        flowPacketHead = flowPacketHead->next();
        if(flowPacketToDelete == flowPacketTail)
        {
            flowPacketHead = nullptr;
        }
        delete flowPacketToDelete;
    }
    flowPacketTail = nullptr;

}
