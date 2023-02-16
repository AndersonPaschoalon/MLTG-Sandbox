#include <stdio.h>
#include <string>
#include <iostream>
#include <set>
#include <atomic>
#include <unordered_map>

#include "NetworkPacket.h"
#include "NetTypes.h"

/// @brief Network set node
struct NetworkLayer
{
    /// @brief set key
    NetworkProtocol proto;

    // points to the right network set of the specified protocol
    std::set<Netv4DstSrc*>* setNetv4DstSrc = NULL;
    std::set<Netv6DstSrc*>* setNetv6DstSrc = NULL;
    std::set<Ipv4DstSrc*>* setIpv4DstSrc = NULL;
    std::set<Ipv6DstSrc*>* setIpv6DstSrc = NULL;

};

/// @brief Generic leaf for non-ip network packets
struct Netv4DstSrc
{
    // Key
    unsigned long int dstSrcSumm;
    // flow data
    unsigned long long int flowId;
};

/// @brief Generic leaf for non-ip network packets
struct Netv6DstSrc
{
    // key
    unsigned long int dstSrcHash;
    // flow data
    unsigned long long int flowId;
};

/// @brief IPv4 node
struct Ipv4DstSrc
{
    /// @brief set key
    unsigned long int dstSrcSumm;

    /// @brief point to the set of transport layer
    std::set<TransportLayer*>* setTransport;
};

/// @brief IPv6 node
struct Ipv6DstSrc
{
    /// @brief set key
    unsigned long int dstSrcHash;

    /// @brief point to the set of transport layer
    std::set<TransportLayer*>* setTransport;
};

/// @brief Transport layer node
struct TransportLayer
{
    /// @brief key
    TransportProtocol proto;

    /// @brief set for the transport layer flows
    std::set<PortDstSrc*> setPortDstSrc;
};

struct PortDstSrc
{
    /// @brief transport layer key
    unsigned long int dstSrcSumm;

    /// @brief set data
    unsigned long long int flowId;
};





class FlowIdCalc
{
    public:

        FlowIdCalc();

        ~FlowIdCalc();

        std::string toString();

        flow_id setFlowId(NetworkPacket& packet);



    private:
        std::atomic<flow_id> lastFlowId;
        std::set<NetworkLayer*> netFlowsStack;


        static const unsigned int summPorts(port_number dst, port_number src);

        static const unsigned long summIpv4(ipv4_address dst, ipv4_address src);

        static const size_t hashStrings(std::string a, std::string b);

        void initNetFlowsStack();

        void destroyNetFlowsStack();

        flow_id getNextFlowId();

};
