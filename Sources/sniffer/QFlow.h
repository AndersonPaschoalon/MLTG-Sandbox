#ifndef _Q_FLOW__H_ 
#define _Q_FLOW__H_ 1

#include <string>
#include "NetTypes.h"
#include "QFlowPacket.h"

class QFlow
{
    public:

    // CLASS METHODS

    // PAYLOAD
    void setProtocols(NetworkProtocol n, TransportProtocol t, ApplicationProtocol a);


    // OPERATION
        QFlowPacket* getFlowPacketHead();
        void setFlowPacketHead(QFlowPacket* head);

    private:

        QFlowPacket* flowPacketHead;

        // Network.Transport.Application XX.XX.XX. 
        protocol_stack stack;
        flow_hash portDstSrc;
        flow_hash net4DstSrcSumm;
        std::string net6DstSrc;


};



#endif // _Q_FLOW__H_ 
