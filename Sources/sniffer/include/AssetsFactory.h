#ifndef _SNIFFER_FACTORY__H_ 
#define _SNIFFER_FACTORY__H_ 1


#include "cpptools.h"
#include "IFlowIdCalc.h"
#include "ILocalDbService.h"
#include "ICaptureDriver.h"
#include "AssetsFactory.h"
#include "Logger.h"
#include "FlowIdCalc.h"
#include "DriverDummy.h"
#include "DriverLibpcap.h"
#include "LocalDbServiceV1_Naive.h"
#include "Sniffer_v01.h"


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

// Capture a static set of emulated packets
#define DRIVER_DUMMY            "DriverDummy"
// Emulated packets from a CSV file
#define DRIVER_CSV              "DriverCsv"
// Libpcap live and pcap capture
#define DRIVER_LIBPCAP          "DriverLibpcap"
// TODO
#define DRIVER_PFRING           "DriverPfRing"
// TODO
#define DRIVER_DPDK             "DriverDPDK"
// TODO
#define DRIVER_LIBTINS          "DriverLibtins"
// TODO
#define DRIVER_PCAPPLUSPLUS     "DriverPcapPlusPlus"
// Capture a static set of emulated packets
#define DRIVER_DUMMY2            "Dummy"
// Emulated packets from a CSV file
#define DRIVER_CSV2              "Csv"
// Libpcap live and pcap capture
#define DRIVER_LIBPCAP2          "Libpcap"
// TODO
#define DRIVER_PFRING2           "PfRing"
// TODO
#define DRIVER_DPDK2             "DPDK"
// TODO
#define DRIVER_LIBTINS2          "Libtins"
// TODO
#define DRIVER_PCAPPLUSPLUS2     "PcapPlusPlus"



class AssetsFactory
{
    public:

        AssetsFactory();

        std::string toString();

        static IFlowIdCalc* makePacketFlowClassifierAlgorithm(const char* calcAlgorithm);

        static ILocalDbService* makeTraceDatabaseManager(const char* name);

        static ICaptureDriver* makePacketCaptureDriver(const char* manager);

    private:


};

#endif //_SNIFFER_FACTORY__H_ 