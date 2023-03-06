#ifndef _SNIFFER_FACTORY__H_ 
#define _SNIFFER_FACTORY__H_ 1


#include "IFlowIdCalc.h"
#include "ILocalDbService.h"
#include "ICaptureDriver.h"


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
// Ether interfaces drivers
//

#define DRIVER_ETHER_DUMMY            "EtherDummy"
#define DRIVER_ETHER_LIBPCAP          "EtherLibpcap"
#define DRIVER_ETHER_PFRING           "EtherPfRing"
#define DRIVER_ETHER_DPDK             "EtherDPDK"
#define DRIVER_ETHER_LIBTINS          "EtherLibtins"
#define DRIVER_ETHER_PCAPPLUSPLUS     "EtherLibtins"


class SnifferFactory
{
    public:

        const static IFlowIdCalc* makePacketFlowClassifierAlgorithm(const char* calcAlgorithm);

        const static ILocalDbService* makeTraceDatabaseManager(const char* name);

        const static ICaptureDriver* makePacketCaptureDriver(const char* manager);


    private:


};

#endif //_SNIFFER_FACTORY__H_ 