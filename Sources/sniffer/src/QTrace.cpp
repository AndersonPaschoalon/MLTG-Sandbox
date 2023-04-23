#include "QTrace.h"

QTrace::QTrace(): QTrace("", "", "", "")
{
}

QTrace::QTrace(const char *traceName, const char *traceType, const char *traceSource, const char *comment)
{
    this->fHead = nullptr;
    this->fTail = nullptr;
    this->pHead = nullptr;
    this->pTail = nullptr;
    this->lastFlow = 0;
    this->traceProperties[QTRACE_TRACE_NAME] = traceName;
    this->traceProperties[QTRACE_TRACE_SOURCE] = traceSource;
    this->traceProperties[QTRACE_TRACE_TYPE] = traceType;
    this->traceProperties[QTRACE_COMMENT] = comment;
}

QTrace::~QTrace()
{
    // delete
}

QTrace::QTrace(const QTrace &obj)
{
    this->traceProperties = obj.traceProperties;
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
        this->traceProperties = other.traceProperties;
        this->fHead = other.fHead;
        this->fTail = other.fTail;
        this->pHead = other.pHead;
        this->pTail = other.pTail;        
        this->lastFlow = other.lastFlow;
    }
    return *this;
}


std::string QTrace::toString()
{
    return std::string("{ traceName:") + this->traceProperties[QTRACE_TRACE_NAME] + 
           std::string(", traceSource:") + this->traceProperties[QTRACE_TRACE_SOURCE]  + 
		   std::string(", TraceType:") + this->traceProperties[QTRACE_TRACE_TYPE]  + 
           std::string(", comment:") + this->traceProperties[QTRACE_COMMENT]  + 
		   std::string(", nPackets:") + this->traceProperties[QTRACE_N_PACKETS]  + 
           std::string(", nFlows:") + this->traceProperties[QTRACE_N_FLOWS]  + 
		   std::string(", duration:") + this->traceProperties[QTRACE_DURATION]  +         
           std::string("}");
}

bool QTrace::isEmpty()
{
    if(this->traceProperties[QTRACE_TRACE_NAME] == "")
    {
        return true;
    }
    return false;
}

std::string QTrace::get(std::string label) const 
{
    auto it = this->traceProperties.find(label);
    if (it == this->traceProperties.end()) 
    {
        return "";
    }
    return it->second;
}

long QTrace::getLong(std::string label) const 
{
    auto it = this->traceProperties.find(label);
    if (it == this->traceProperties.end()) 
    {
        return 0;
    }
    return std::stol(it->second);
}

double QTrace::getDouble(std::string label) const
{
    auto it = this->traceProperties.find(label);
    if (it == this->traceProperties.end()) 
    {
        return 0.0;
    }
    return std::stod(it->second);
}

void QTrace::set(std::string label, std::string value) 
{
    this->traceProperties[label] = value;
}

void QTrace::set(std::string label, long value) 
{
    this->traceProperties[label] = std::to_string(value);
}

void QTrace::set(std::string label, double value)
{
    this->traceProperties[label] = std::to_string(value);
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
    }

    // add packet
    size_t packetId = p.getPacketId();
    flow_id flowId = p.getFlowId();
    timeval ts = p.getTimestamp();
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
