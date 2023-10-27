#include "QFlow.h"

QFlow::QFlow()
{
    this->nextPtr = nullptr;
    this->flowId = 0;
    this->stack = 0;
    this->portDstSrc = 0;
    this->net4DstSrcSumm = 0;
    this->net6DstSrc = "";
    this->numberOfPackets = 0;
}

QFlow::~QFlow()
{
}

std::string QFlow::toString()
{
    std::string ipv4DstStr = "";
    std::string ipv4SrcStr = "";
    port_number portSrc = 0;
    port_number portDst = 0;
    NetworkProtocol n = to_network_protocol(this->stack);
    TransportProtocol t = to_transport_protocol(this->stack);
    ApplicationProtocol a = to_application_protocol(this->stack);
    recover_ipv4_str(this->net4DstSrcSumm, ipv4DstStr, ipv4SrcStr);
    recover_ports(this->portDstSrc, portDst, portSrc);
    return std::string("{ flowId:") + std::to_string(this->flowId) + 
           std::string("{ numberOfPackets:") + std::to_string(this->numberOfPackets) + 
           // network
           std::string(", netProto:") + to_string(n) +
           std::string(", net4Dst:") + ipv4DstStr + 
           std::string(", net4Src:") + ipv4SrcStr  + 
           std::string(", net6Hash:") + this->net6DstSrc + 
           // transport
           std::string(", transProto:") + to_string(t) +
           std::string(", portDst:") + std::to_string(portDst) +
           std::string(", portSrc:") + std::to_string(portSrc) +
           // application
           std::string(", appProto:") + to_string(a) +
           std::string("}");
}

//QFlow::QFlow(const QFlow &obj)
//{
//}

//QFlow &QFlow::operator=(QFlow other)
//{
//    // TODO: insert return statement here
//}

void QFlow::setFlowId(flow_id flowId)
{
    this->flowId = flowId;
}

void QFlow::setNumberOfPackets(size_t nPakcets)
{
    this->numberOfPackets = nPakcets;
}

void QFlow::setProtocols(NetworkProtocol n, TransportProtocol t, ApplicationProtocol a)
{
    this->stack = zip_stack(n, t, a);
}

void QFlow::setNet4Addr(ipv4_address dst, ipv4_address src)
{
    this->net4DstSrcSumm = zip_ipv4(dst, src);
}

void QFlow::setNet6Addr(const char *dst, const char *src)
{
    this->net6DstSrc.clear();
    if(strcmp(dst, "") != 0 || strcmp(src, "") != 0)
    {
        this->net6DstSrc.append(dst);
        this->net6DstSrc.append(",");
        this->net6DstSrc.append(src);
    }
}

void QFlow::setPorts(port_number dst, port_number src)
{
    this->portDstSrc = zip_ports(dst, src);
}

void QFlow::getQData(flow_id& fId, 
                     size_t& nPackets, 
                     protocol_stack &stk, 
                     flow_hash &port, 
                     flow_hash &net4, 
                     std::string &net6)
{
    fId = this->flowId;
    nPackets = this->numberOfPackets;
    stk = this->stack;
    port = this->portDstSrc;
    net4 = this->net4DstSrcSumm;
    net6 = this->net6DstSrc;
}

flow_id QFlow::getFlowId()
{
    return this->flowId;
}

QFlow *QFlow::next()
{
    return this->nextPtr;
}

void QFlow::setNext(QFlow *nxtPtr)
{
    this->nextPtr = nxtPtr;
}
