#ifndef _Q_FLOW__H_ 
#define _Q_FLOW__H_ 1

#include <string.h>
#include <string>
#include "NetTypes.h"
#include "QFlowPacket.h"

/**
 * Class responsible to temporaly store the data of a single flow to be commited in a local database.
 * QFlow stands for Queryable-Flow
 ***/
class QFlow
{
    public:
    
        // CLASS METHODS
        QFlow();

        ~QFlow();

        QFlow(const QFlow& obj) = delete;

        QFlow& operator=(QFlow other) = delete;

        std::string toString();


        // PAYLOAD
        void setFlowId(flow_id flowId);
        void setNumberOfPackets(size_t nPakcets);
        void setProtocols(NetworkProtocol n, TransportProtocol t, ApplicationProtocol a);
        void setNet4Addr(ipv4_address dst, ipv4_address src);
        void setNet6Addr(const char* dst, const char* src);
        void setPorts(port_number dst, port_number src);

        /// @brief 
        /// @param stack 
        /// @param portDstSrc 
        /// @param net4DstSrcSumm 
        /// @param net6DstSrc 
        void getQData(flow_id& fId, 
                      size_t& nPackets, 
                      protocol_stack &stk, 
                      flow_hash &port, 
                      flow_hash &net4, 
                      std::string &net6);
        flow_id getFlowId();

        // OPERATION
        QFlow* next();
        void setNext(QFlow* nxtPtr);

    private:

        QFlow* nextPtr;

        // Network.Transport.Application XX.XX.XX.
        flow_id flowId;
        protocol_stack stack;
        flow_hash portDstSrc;
        flow_hash net4DstSrcSumm;
        std::string net6DstSrc;
        size_t numberOfPackets;
        



};



#endif // _Q_FLOW__H_ 
