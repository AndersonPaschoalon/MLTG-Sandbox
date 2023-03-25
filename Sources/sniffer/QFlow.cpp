#include "QFlow.h"

QFlow::QFlow()
{
    this->nextPtr = nullptr;
    this->flowId = 0;
    this->stack = 0;
    this->portDstSrc = 0;
    this->net4DstSrcSumm = 0;
    this->net6DstSrc = "";
}

QFlow::~QFlow()
{
}

std::string QFlow::toString()
{
    return std::string();
}

//QFlow::QFlow(const QFlow &obj)
//{
//}

//QFlow &QFlow::operator=(QFlow other)
//{
//    // TODO: insert return statement here
//}

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
    this->net6DstSrc.append(dst);
    this->net6DstSrc.append(",");
    this->net6DstSrc.append(src);
}

void QFlow::setPorts(port_number dst, port_number src)
{
    this->portDstSrc = zip_ports(dst, src);
}

void QFlow::getQData(flow_id& fId, protocol_stack &stk, flow_hash &port, flow_hash &net4, std::string &net6)
{
    fId = this->flowId;
    stk = this->stack;
    port = this->portDstSrc;
    net4 = this->net4DstSrcSumm;
    net6 = this->net6DstSrc;
}

QFlow *QFlow::next()
{
    return this->nextPtr;
}

void QFlow::setNext(QFlow *nxtPtr)
{
    this->nextPtr = nxtPtr;
}
