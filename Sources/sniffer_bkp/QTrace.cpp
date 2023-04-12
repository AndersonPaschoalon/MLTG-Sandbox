#include "QTrace.h"

QTrace::QTrace(): QTrace("", "", "")
{
}

QTrace::QTrace(const char *traceName, const char *traceSource, const char *comment)
{
    this->fHead = nullptr;
    this->fTail = nullptr;
    this->pHead = nullptr;
    this->pTail = nullptr;
    this->lastFlow = 0;
    this->set(traceName, traceSource, comment);
}

QTrace::~QTrace()
{
    // delete
}

QTrace::QTrace(const QTrace &obj)
{
    this->traceName = obj.traceName;
    this->traceSource = obj.traceSource;
    this->comment = obj.comment;
    this->fHead = obj.fHead;
    this->fTail = obj.fTail;
    this->pHead = obj.pHead;
    this->pTail = obj.pTail;        
    this->lastFlow = obj.lastFlow;
}

QTrace &QTrace::operator=(QTrace other)
{
    if (this != &other)
    {
        this->traceName = other.traceName;
        this->traceSource = other.traceSource;
        this->comment = other.comment;
        this->fHead = other.fHead;
        this->fTail = other.fTail;
        this->pHead = other.pHead;
        this->pTail = other.pTail;        
        this->lastFlow = other.lastFlow;
    }
    return *this;
}

void QTrace::set(const char*  theTraceName, const char*  theTraceSource, const char*  theComment)
{
    this->traceName = StringUtils::trimCopy(std::string(theTraceName));
    this->traceSource = StringUtils::trimCopy(std::string(theTraceSource));
    this->comment = StringUtils::trimCopy(std::string(theComment));
}

std::string QTrace::toString()
{
    return std::string("{ traceName:") + this->traceName + 
           std::string(", traceSource:") + this->traceSource + 
		   std::string(", comment:") + this->comment + std::string("}");
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

const std::string QTrace::getTags()
{
    return std::string();
}

bool QTrace::isEmpty()
{
    if(this->traceName == "")
    {
        return true;
    }
    return false;
}

void QTrace::push(NetworkPacket p)
{
    if (p.getFlowId() > this->lastFlow)
    {
        // add flow and packet
        QFlow* f = new QFlow();
        f->setFlowId(p.getFlowId());
        f->setProtocols(p.getNetworkProtocol(), p.getTransportProtocol(), p.getApplicationProtocol());
        f->setNet4Addr(p.getIPv4Dst(), p.getIPv4Src());
        f->setPorts(p.getPortDst(), p.getPortSrc());
        f->setNet6Addr(p.getIPv6Dst().c_str(), p.getIPv6Src().c_str());
        if(this->fHead == nullptr) // first flow, update head
        {
            this->fHead = f;
        }
        if (this->fTail != nullptr)
        {
            // current tail must point to the new flow
            this->fTail->setNext(f);
        }
        // swap tail and current flow pointer
        f->setNext(nullptr);
        this->fTail = f;

        // update last flow
        this->lastFlow = p.getFlowId();

        // debug 
        // printf("Flow added %s\n", f->toString().c_str());
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
    if (this->pTail != nullptr)
    {
        // update tail pkt
        this->pTail->setNext(fp);
    }
    fp->setNext(nullptr);
    this->pTail = fp;

    // debug 
    // printf("Packet added %s\n", fp->toString().c_str());
}

void QTrace::consume(QFlow** flowHead, QFlow** flowTail, QFlowPacket** flowPacketHead,  QFlowPacket** flowPacketTail)
{
    *flowHead = this->fHead;
    *flowTail = this->fTail;
    *flowPacketHead = this->pHead;
    *flowPacketTail = this->pTail;

    this->fHead = nullptr;
    this->fTail = nullptr;
    this->pHead = nullptr;
    this->pTail = nullptr;
}

const void QTrace::free(QFlow *flowHead, QFlow *flowTail, QFlowPacket *flowPacketHead, QFlowPacket *flowPacketTail)
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

const void QTrace::echo(QTrace &obj, QFlow *flowHead, QFlow *flowTail, QFlowPacket *flowPacketHead, QFlowPacket *flowPacketTail)
{
    printf("** QTrace data dump **\n\t%s\n", obj.toString().c_str());

    unsigned long i = 0;
    printf("\n** QFlow data dump**\n");
    QFlow *flowPtr;
    flowPtr = flowHead;
    while (flowPtr != nullptr)
    {
        printf("\t[flow-%lu] %s\n", i, flowPtr->toString().c_str());
        flowPtr = flowPtr->next();
        if(flowPtr == flowTail)
        {
            break;;
        }
        i++;
    }

    i = 0;
    printf("\n** QFlowPacket data dump**\n");
    QFlowPacket *pktPtr;
    pktPtr = flowPacketHead;
    while (pktPtr != nullptr)
    {
        printf("\t[pkt-%lu] %s\n", i, pktPtr->toString().c_str());
        pktPtr = pktPtr->next();
        if(pktPtr == flowPacketTail)
        {
            break;;
        }
        i++;
    }

    return void();
}
