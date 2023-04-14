#ifndef _SNIFFER_FACTORY__H_ 
#define _SNIFFER_FACTORY__H_ 1


#include "IFlowIdCalc.h"
#include "ILocalDbService.h"
#include "ICaptureDriver.h"
#include "Logger.h"
#include "cpptools.h"
#include "FlowIdCalc.h"
#include "DriverDummy.h"
#include "DriverLibpcap.h"
#include "LocalDbServiceV1_Naive.h"

//
// Trace Database Managers 
//

#define TRACE_DB_V1_NAIVE             "LocalDbServiceV1_Naive" 
#define TRACE_DB_V1_ASYNC             "LocalDbServiceV1_Async"


//
// Flow ID Calc Algorithms 
//

#define FLOW_ID_CALC                  "FlowIdCalc"


//
// Driver interfaces drivers
//

#define DRIVER_DUMMY            "DriverDummy"
#define DRIVER_LIBPCAP          "DriverLibpcap"
#define DRIVER_PFRING           "DriverPfRing"
#define DRIVER_DPDK             "DriverDPDK"
#define DRIVER_LIBTINS          "DriverLibtins"
#define DRIVER_PCAPPLUSPLUS     "DriverLibtins"


class SnifferFactory
{
    public:

        SnifferFactory();

        std::string toString();

        static IFlowIdCalc* makePacketFlowClassifierAlgorithm(const char* calcAlgorithm);

        static ILocalDbService* makeTraceDatabaseManager(const char* name);

        static ICaptureDriver* makePacketCaptureDriver(const char* manager);

    private:


};

#endif //_SNIFFER_FACTORY__H_ 