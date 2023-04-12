#ifndef _SNIFFER_V01__H_
#define _SNIFFER_V01__H_ 1

#include <string>
#include <vector>
#include "ISniffer.h"


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

class Sniffer_v01: public ISniffer
{
    public:

        Sniffer_v01();

        ~Sniffer_v01();

        Sniffer_v01(const Sniffer_v01& obj) = delete;

        Sniffer_v01& operator=(Sniffer_v01 other) = delete;

        int run();

    private:
};

#endif // _SNIFFER_V01__H_