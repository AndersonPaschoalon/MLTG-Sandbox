#ifndef _FLOW__H_
#define _FLOW__H_ 1

#include <string>
#include <vector>
#include "NetTypes.h"
#include "FlowPacket.h"


class Flow
{
    public:

        Flow();

        ~Flow();

        Flow(const Flow& obj);

        Flow& operator=(Flow other);

        std::string toString();

        void set(flow_id flowId,
                 time_stamp timeStamp, 
                 NetworkProtocol n, 
                 ipv4_address src, 
                 ipv4_address dst);

        void set(flow_id flowId,
                 time_stamp timeStamp, 
                 NetworkProtocol n, 
                 const std::string& ipv6Src, 
                 const std::string& ipv6Dst);

        void set(flow_id flowId,
                 time_stamp timeStamp, 
                 NetworkProtocol n, 
                 ipv4_address ipsrc, 
                 ipv4_address ipdst,
                 TransportProtocol t,
                 port_number portSrc,
                 port_number portDst,
                 ApplicationProtocol app);

        void set(flow_id flowId,
                 time_stamp timeStamp, 
                 NetworkProtocol n, 
                 const std::string& ipv6Src, 
                 const std::string& ipv6Dst,
                 TransportProtocol t,
                 port_number portSrc,
                 port_number portDst,
                 ApplicationProtocol app);

        void addPacket(FlowPacket pkt);


    private:

        time_stamp startTime;
        flow_id flowId;

        NetworkProtocol networkProtocol;
        ipv4_address ipv4Src;
        ipv4_address ipv4Dst;
        std::string ipv6Src;
        std::string ipv6Dst;

        TransportProtocol transportProtocol;
        port_number portSrc;
        port_number portDst;
        
        ApplicationProtocol applicationProtocol;

        std::vector<FlowPacket>* packetList;

};

#endif // _FLOW__H_

