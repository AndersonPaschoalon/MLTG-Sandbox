#ifndef _Q_TRACE__H_
#define _Q_TRACE__H_ 1

#include <string>
#include "Utils.h"
#include "NetTypes.h"
#include "NetworkPacket.h"
#include "QFlow.h"
#include "QFlowPacket.h"


class QTrace
{
    public:

        //
        // Class methods
        //

        QTrace();

        QTrace(const char* traceName, const char*  traceSource, const char* comment);

        ~QTrace();

        QTrace(const QTrace& obj);

        QTrace& operator=(QTrace other);        

        std::string toString();


        //
        // Trace metadata
        //

        const std::string getTraceName();
        const std::string getTraceSource();
        const std::string getComment();
        bool isEmpty();


        //
        // Trace Management
        //

        void push(NetworkPacket p);
        void consume(QFlow** flowHead, QFlow** flowTail, QFlowPacket** flowPacketHead,  QFlowPacket** flowPacketTail);
        const static void free(QFlow* flowHead, QFlow* flowTail, QFlowPacket* flowPacketHead,  QFlowPacket* flowPacketTail);
        const static void echo (QTrace& obj, QFlow* flowHead, QFlow* flowTail, QFlowPacket* flowPacketHead,  QFlowPacket* flowPacketTail);

    private:

        // trace information
        std::string traceName;
        std::string traceSource;
        std::string comment;

        QFlow* fHead;
        QFlow* fTail;
        QFlowPacket* pHead;
        QFlowPacket* pTail;
        flow_id lastFlow;

        void set(const char*  traceName,
                 const char*  traceSource,
                 const char*  comment);

};

#endif  // _Q_TRACE__H_
