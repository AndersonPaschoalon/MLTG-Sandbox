#ifndef _FLOW_PACKET__H_ 
#define _FLOW_PACKET__H_ 1

#include <string>
#include "NetTypes.h"

class FlowPacket
{
    public:
        FlowPacket(time_stamp timeStamp, packet_size packetSize, ttl timeToLive);

        ~FlowPacket();

        FlowPacket(const FlowPacket& obj);

        FlowPacket& operator=(FlowPacket other);

        std::string toString();

        time_stamp getTimeStamp();
        
        packet_size getPacketSize();

        ttl getTtl();

    private:

        time_stamp timeStamp;
        packet_size packetSize;
        ttl timeToLive;
};

#endif // _FLOW_PACKET__H_
