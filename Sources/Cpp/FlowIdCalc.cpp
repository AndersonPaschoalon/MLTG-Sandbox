#include "FlowIdCalc.h"

FlowIdCalc::FlowIdCalc()
{
    this->lastFlowId = 0;

}

FlowIdCalc::~FlowIdCalc()
{

}

std::string FlowIdCalc::toString()
{
    return std::string("FlowIdCalc");
}

const unsigned int FlowIdCalc::summPorts(port_number dst, port_number src)
{
    return PORT_OFFSET_VALUE*dst + src;
}

const unsigned long int FlowIdCalc::summIpv4(ipv4_address dst, ipv4_address src)
{
    return IPV4_OFFSET_VALUE*dst + src;
}

const size_t FlowIdCalc::hashStrings(std::string a, std::string b)
{
    std::hash<std::string> hasher;
    std::string strToHash = a + b;
    size_t hash = hasher(strToHash);
    return hash;
}

flow_id FlowIdCalc::getNextFlowId()
{
    this->lastFlowId++;
    return this->lastFlowId.load();
}
