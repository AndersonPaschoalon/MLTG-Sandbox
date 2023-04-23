#ifndef _Q_TRACE__H_
#define _Q_TRACE__H_ 1

#include <string>
#include <unordered_map>
#include "cpptools.h"
#include "NetTypes.h"
#include "NetworkPacket.h"
#include "QFlow.h"
#include "QFlowPacket.h"

// Properties
#define QTRACE_TRACE_NAME          "traceName"
#define QTRACE_TRACE_SOURCE        "traceSource"
#define QTRACE_TRACE_TYPE          "TraceType"
#define QTRACE_COMMENT             "comment"
#define QTRACE_N_PACKETS           "nPackets"
#define QTRACE_N_FLOWS             "nFlows"
#define QTRACE_DURATION            "duration"


class QTrace
{
    public:

        //
        // Class methods
        //

        QTrace();

        QTrace(const char *traceName, const char *traceType, const char *traceSource,  const char *comment);

        ~QTrace();

        QTrace(const QTrace& obj);

        QTrace& operator=(QTrace other);        

        std::string toString();


        //
        // Trace metadata
        //
        bool isEmpty();
        std::string get(std::string label) const;
        long getLong(std::string label) const;
        double getDouble(std::string label) const;
        void set(std::string label, std::string value);
        void set(std::string label, long value);
        void set(std::string label, double value);


        //
        // Trace Management
        //

        void push(NetworkPacket p);
        void consume(QFlow** flowHead, QFlow** flowTail, QFlowPacket** flowPacketHead,  QFlowPacket** flowPacketTail);

        const static void free(QFlow* flowHead, QFlow* flowTail, QFlowPacket* flowPacketHead,  QFlowPacket* flowPacketTail);
        const static void echo (QTrace& obj, QFlow* flowHead, QFlow* flowTail, QFlowPacket* flowPacketHead,  QFlowPacket* flowPacketTail);

    private:

        // trace information
        std::unordered_map<std::string, std::string> traceProperties;

        QFlow* fHead;
        QFlow* fTail;
        QFlowPacket* pHead;
        QFlowPacket* pTail;
        flow_id lastFlow;


        // void setTags(const char* csvTags);

};

#endif  // _Q_TRACE__H_
