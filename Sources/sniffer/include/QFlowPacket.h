#ifndef _Q_FLOW_PACKET__H_ 
#define _Q_FLOW_PACKET__H_ 1

#include <string>
#include "NetTypes.h"

/// @brief Queyrable Flow packet. 
class QFlowPacket
{
    public:

        // CLASS OPERATORS

        QFlowPacket(size_t packetId, flow_id flowId, timeval& ts, packet_size pktSize, ttl timeToLive);

        ~QFlowPacket();

        QFlowPacket(const QFlowPacket& obj) = delete;

        QFlowPacket& operator=(QFlowPacket other) = delete;

        std::string toString();

        // CLASS PAYLOAD
        void getQData(size_t& packetId, flow_id& flowId, timeval& ts, packet_size& packetSize, ttl& timeToLive);
        flow_id getFlowId();

        // OPERATIONS CONTROL

        void setNext(QFlowPacket* nextNode);

        QFlowPacket* next();

        // TODO MUDAR PARA setCommited()
        void setCommited(bool toDelete);

        // getCommited
        bool getCommited();

    private:

        size_t pktId;
        flow_id flowId;
        timeval timeStamp;
        packet_size pktSize;
        ttl timeToLive;
        bool readyToFree;
        QFlowPacket* nextPacket;

        void set(size_t pktId, flow_id flowId, timeval& timeStamp, packet_size pktSize, ttl timeToLive, bool readyToFree, QFlowPacket* nextPacket);

};

#endif // _Q_FLOW_PACKET__H_ 
