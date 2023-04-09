#ifndef _TRACE__H_
#define _TRACE__H_ 1


#include <string>
#include <vector>
#include "NetTypes.h"
#include "NetworkPacket.h"
#include "Flow.h"
#include "FlowPacket.h"
#include "FlowIdCalc.h"


class Trace
{
    public:

        Trace();

        ~Trace();

        std::string toString();

        void set(const std::string& traceName,
                 const std::string& traceSource,
                 const std::string& dateTime,
                 double epochStartTime);

        void bufferParser(ETHER_BUFFER_NODE* buffer, FlowIdCalc* flowCalc);        


    private:

        std::string traceName;
        std::string traceSource;
        std::string dateTime;
        double epochStartTime;
        std::vector<Flow*> flows;

        void addFlow(Flow* flow);


};

#endif // _TRACE__H_


