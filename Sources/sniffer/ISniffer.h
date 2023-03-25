#ifndef _I_SNIFFER__H_
#define _I_SNIFFER__H_ 1

#include <string>
#include <vector>
#include "Logger.h"
#include "Utils.h"
#include "NetTypes.h"
#include "NetworkPacket.h"
#include "SnifferFactory.h"
#include "ICaptureDriver.h"
#include "IFlowIdCalc.h"
#include "ILocalDbService.h"


//
// Naive implementation -> no parallel management of the database.
//
// params: traceType, traceSource, CaptureLib, timeout, databaseManager, flowCalcAlg
// init database(databaseManager), captureDriver(traceType, CaptureLib)
//      flowCalc(flowCalcAlg), trace(traceType, traceSource)
// captureDriver.listen(traceSource, timeout)
// while captureDriver.continue():
//     NetworkPacket p;
//     ret = captureDriver.nextPacket(p);
//     flowCalc.setFlowId(p)
//     trace.push(p);
// QFlow* fHead, fTail;
// QFlowPacket* pHead, pTail;
// trace.consume(fHead, fTail, pHead, pTail);
// database.receiveData(trace);
// database.receiveData(fHead, fTail);
// database.receiveData(pHead, pTail);
// database.close();
// trace.free(fHead, fTail, pHead, pTail);
//

class ISniffer
{
    public:

        virtual std::string toString();

        virtual void configure(const char* traceName, 
                               const char* captureLybrary, 
                               const char* captureDevice,
                               const char* databaseManager,
                               const char* flowCalcAlgorithm,
                               const char* comments,
                               const double timeoutSec = 30,
                               const long maxPacketNumber = -1);

        virtual int run() = 0;

    protected:

        std::string traceName;
        std::string captureLibrary;
        std::string captureDevice;
        std::string databaseManager;
        std::string flowCalcAlgorithm;
        std::string comments;
        double timeoutSec;
        long maxPacketNumber;
        TraceType traceType;

};

#endif // _I_SNIFFER__H_