#ifndef _Q_FLOW_PACKET__H_ 
#define _Q_FLOW_PACKET__H_ 1

#include <string>
#include "NetTypes.h"

/// @brief Queyrable Flow packet. 
class QFlowPacket
{
    public:

        // CLASS OPERATORS

        QFlowPacket(size_t packetId, flow_id flowId, time_stamp time_stamp, packet_size pktSize, ttl timeToLive);

        ~QFlowPacket();

        QFlowPacket(const QFlowPacket& obj);

        QFlowPacket& operator=(QFlowPacket other);

        std::string toString();

        // CLASS PAYLOAD

        /// @brief Packet private key. Is a counter on the flow packets.
        /// @return returns the packet ID.
        size_t packetId();

        /// @brief [FK][PK] Packet flow ID.
        /// @return returns the packet flow ID
        flow_id getFlowId();

        time_stamp getTimeStamp();
        
        packet_size getPacketSize();

        ttl getTtl();

        // OPERATIONS CONTROL

        void setNext(QFlowPacket* nextNode);

        QFlowPacket* next();

        void setDelete(bool toDelete);

        bool getDelete();

    private:

    size_t pktId;
    flow_id flowId;
    time_stamp timeStamp;
    packet_size pktSize;
    ttl timeToLive;
    bool readyToFree;
    QFlowPacket* nextPacket;

    void set(size_t pktId, flow_id flowId, time_stamp timeStamp, packet_size pktSize, ttl timeToLive, bool readyToFree, QFlowPacket* nextPacket);

};

#endif _Q_FLOW_PACKET__H_ 
