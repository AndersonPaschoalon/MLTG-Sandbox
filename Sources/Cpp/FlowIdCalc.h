#include <stdio.h>
#include <string>
#include <iostream>
#include <set>
#include <atomic>
#include <unordered_map>

#include "NetworkPacket.h"
#include "NetTypes.h"

/// @brief Network set node
typedef struct _NetworkLayer
{
    /// @brief set key
    NetworkProtocol proto;

    // points to the right network set of the specified protocol
    std::set<Netv4DstSrc>* setNetv4DstSrc = NULL;
    std::set<Netv6DstSrc>* setNetv6DstSrc = NULL;
    std::set<Ipv4DstSrc>* setIpv4DstSrc = NULL;
    std::set<Ipv6DstSrc>* setIpv6DstSrc = NULL;

    bool operator<(const struct _NetworkLayer& other) const 
    {
        return proto < other.proto;
    }
}NetworkLayer;

/// @brief Generic leaf for non-ip network packets
typedef struct _Netv4DstSrc
{
    // Key
    unsigned long int dstSrcSumm;
    // flow data
    flow_id flowId;

    bool operator<(const struct _Netv4DstSrc& other) const 
    {
        return dstSrcSumm < other.dstSrcSumm;
    }

}Netv4DstSrc;

/// @brief Generic leaf for non-ip network packets
typedef struct _Netv6DstSrc
{
    // key
    unsigned long int dstSrcHash;
    // flow data
    flow_id flowId;

    bool operator<(const struct _Netv6DstSrc& other) const 
    {
        return dstSrcHash < other.dstSrcHash;
    }

}Netv6DstSrc;

/// @brief IPv4 node
typedef struct _Ipv4DstSrc
{
    /// @brief set key
    unsigned long int dstSrcSumm;

    /// @brief point to the set of transport layer
    std::set<TransportLayer>* setTransport;


    bool operator<(const _Ipv4DstSrc& other) const 
    {
        return dstSrcSumm < other.dstSrcSumm;
    }

}Ipv4DstSrc;

/// @brief IPv6 node
typedef struct _Ipv6DstSrc
{
    /// @brief set key
    unsigned long int dstSrcHash;

    /// @brief point to the set of transport layer
    std::set<TransportLayer>* setTransport;

    bool operator<(const struct _Ipv6DstSrc& other) const 
    {
        return dstSrcHash < other.dstSrcHash;
    }

}Ipv6DstSrc;

/// @brief Transport layer node
typedef struct _TransportLayer
{
    /// @brief key
    TransportProtocol proto;

    /// @brief set for the transport layer flows
    std::set<PortDstSrc>* setPortDstSrc;

    bool operator<(const struct _TransportLayer& other) const 
    {
        return proto < other.proto;
    }    
}TransportLayer;

typedef struct _PortDstSrc
{
    /// @brief transport layer key
    unsigned long int dstSrcSumm;

    /// @brief set data
    flow_id flowId;

    bool operator<(const struct _PortDstSrc& other) const 
    {
        return dstSrcSumm < other.dstSrcSumm;
    }    

}PortDstSrc;


class FlowIdCalc
{
    public:

        FlowIdCalc();

        ~FlowIdCalc();

        std::string toString();

        flow_id setFlowId(NetworkPacket& packet);



    private:
        std::atomic<flow_id> lastFlowId;

        /// @brief A set that represent the Flow Stack of a given trace.
        std::set<NetworkLayer>* netFlowsStack;

        static const unsigned int summPorts(port_number dst, port_number src);

        static const unsigned long summIpv4(ipv4_address dst, ipv4_address src);

        static const size_t hashStrings(std::string a, std::string b);

        void initNetFlowsStack();

        void destroyNetFlowsStack();

        flow_id getNextFlowId();

};
