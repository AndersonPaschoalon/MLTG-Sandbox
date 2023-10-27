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

        /// @brief Add one more packet to the query-able trace QTrace. It will parse the NetworkPacket
        /// information into the right data structure to query into the database.
        /// @param p Network packet to be added.
        void push(NetworkPacket p);

        /// @brief Returns the pointers of the query-able datastructures. The pointers of the trace
        /// will be set to null, therefore they must be consumed after the call of this method. 
        /// @param flowHead 
        /// @param flowTail 
        /// @param flowPacketHead 
        /// @param flowPacketTail 
        void consume(QFlow** flowHead, QFlow** flowTail, QFlowPacket** flowPacketHead,  QFlowPacket** flowPacketTail);

        /// @brief Helper function to free the pointers returned by consume(). It must be called after
        /// consume() is called, before leaving the scope.
        /// @param flowHead 
        /// @param flowTail 
        /// @param flowPacketHead 
        /// @param flowPacketTail 
        /// @return 
        const static void free(QFlow* flowHead, QFlow* flowTail, QFlowPacket* flowPacketHead,  QFlowPacket* flowPacketTail);

        /// @brief Prints in the standard output the data returned by consume().
        /// @param obj 
        /// @param flowHead 
        /// @param flowTail 
        /// @param flowPacketHead 
        /// @param flowPacketTail 
        /// @return 
        const static void echo (QTrace& obj, QFlow* flowHead, QFlow* flowTail, QFlowPacket* flowPacketHead,  QFlowPacket* flowPacketTail);
        


    private:

        const void countNumberOfPackets();

        // trace information
        std::unordered_map<std::string, std::string> traceProperties;

        QFlow* fHead;
        QFlow* fTail;
        QFlowPacket* pHead;
        QFlowPacket* pTail;
        flow_id lastFlow;


};

#endif  // _Q_TRACE__H_
