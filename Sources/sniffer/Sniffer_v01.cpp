#include "Sniffer_v01.h"

Sniffer_v01::Sniffer_v01()
{
}

Sniffer_v01::~Sniffer_v01()
{
}

Sniffer_v01::Sniffer_v01(const Sniffer_v01 &obj)
{
}

Sniffer_v01 &Sniffer_v01::operator=(Sniffer_v01 other)
{
    // TODO: insert return statement here
}



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
int Sniffer_v01::run()
{
    // initialization
    // ILocalDbService* database = SnifferFactory::makeTraceDatabaseManager(TRACE_DB_V1_NAIVE);
    // ICaptureDriver* captureDriver = SnifferFactory::makePacketCaptureDriver(DRIVER_ETHER_DUMMY);
    // IFlowIdCalc* flowAlgorithm = SnifferFactory::makePacketFlowClassifierAlgorithm(FLOW_ID_CALC);
    ILocalDbService* database = SnifferFactory::makeTraceDatabaseManager(this->databaseManager.c_str());
    ICaptureDriver* captureDriver = SnifferFactory::makePacketCaptureDriver(this->captureLibrary.c_str());
    IFlowIdCalc* flowAlgorithm = SnifferFactory::makePacketFlowClassifierAlgorithm(this->flowCalcAlgorithm.c_str());


    QTrace trace = QTrace(this->traceName.c_str(), this->captureDevice.c_str(), this->comments.c_str());
    
    // open database manager
    database->open();

    // start packet capture
    captureDriver->listen(this->captureDevice.c_str(), this->timeoutSec);
    while(captureDriver->doContinue())
    {
        NetworkPacket p;
        int ret = captureDriver->nextPacket(p);
        flowAlgorithm->setFlowId(p);
        trace.push(p);
    }

    // receive captured data buffer pointers
    QFlow* fHead = nullptr; 
    QFlow* fTail = nullptr;
    QFlowPacket* pHead = nullptr; 
    QFlowPacket* pTail = nullptr;
    trace.consume(fHead, fTail, pHead, pTail);

    // send to local database and commit 
    database->receiveData(trace);
    database->receiveData(fHead, fTail);
    database->receiveData(pHead, pTail);
    database->close();

    // Free allocated memory
    QTrace::free(fHead, fTail, pHead, pTail);

    return 0;
}
