#include <stdio.h>
#include <string>
#include <iostream>
#include <set>

#include "NetworkPacket.h"
#include "NetTypes.h"

struct NetworkLayer
{
    NetworkProtocol proto;
    std::set<Netv4DstSrc> setNetv4DstSrc;
    std::set<Netv6DstSrc> setNetv6DstSrc;
    std::set<Ipv4DstSrc> setIpv4DstSrc;
    std::set<Ipv6DstSrc> setIpv6DstSrc;

};

struct Netv4DstSrc
{
    unsigned long int dstSrcSumm;
    unsigned long long int flowId;
};

struct Netv6DstSrc
{
    unsigned long int dstSrcHash;
    unsigned long long int flowId;
};


struct Ipv4DstSrc
{
    unsigned long int dstSrcSumm;
    std::set<TransportLayer> setTransport;
};

struct Ipv6DstSrc
{
    unsigned long int dstSrcHash;
};

struct TransportLayer
{
    TransportProtocol proto;
    std::set<PortDstSrc> setPortDstSrc;
};

struct PortDstSrc
{
    unsigned long int dstSrcSumm;
    unsigned long long int flowId;
};





class FlowIdCalc
{
    public:

        FlowIdCalc();

        ~FlowIdCalc();

        std::string toString();

        unsigned long long getNextFlowId();


    private:

        unsigned long long lastFlowId;

        unsigned long int summPorts(unsigned short dst, unsigned short src);
        unsigned long int summIpv4(unsigned int dst, unsigned int src);
        unsigned long int hashStrings(std::string a, std::string b);

};
