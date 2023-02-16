#include <string>
#include "NetTypes.h"

class FlowPacket
{
    public:
        FlowPacket(double timeStamp, unsigned int packetSize, ttl timeToLive);

        time_stamp getTimeStamp();
        
        packet_size getPacketSize();

        ttl getTtl();

    private:

        time_stamp timeStamp;
        packet_size packetSize;
        ttl timeToLive;
};