#include "Sniffer_v01.h"

Sniffer_v01::Sniffer_v01()
{
}

Sniffer_v01::~Sniffer_v01()
{
}

int Sniffer_v01::run()
{
    // initialization
    ILocalDbService* database = AssetsFactory::makeTraceDatabaseManager(this->databaseManager.c_str());
    ICaptureDriver* captureDriver = AssetsFactory::makePacketCaptureDriver(this->captureDriver.c_str());
    IFlowIdCalc* flowAlgorithm = AssetsFactory::makePacketFlowClassifierAlgorithm(this->flowCalcAlgorithm.c_str());

    QTrace trace(this->traceName.c_str(), this->captureType.c_str(), this->captureDevice.c_str(), this->comments.c_str());
    
    // open database manager
    database->open();
    bool ret = database->traceExists(this->traceName.c_str());
    if(ret == true)
    {
        LOGGER(ERROR, "Can't create trace entry, trace %s already exists!", this->traceName.c_str());
        LOGGER(INFO,  "Hint: use --remove option to delete the entry.");
        return -1;
    }

    // start packet capture
    captureDriver->listen(this->captureType.c_str(), this->captureDevice.c_str(), this->timeoutSec, this->maxPacketNumber);
    long nFlows = -1;
    long currentFlow = -1;
    while(captureDriver->doContinue())
    {
        NetworkPacket p;
        int ret = captureDriver->nextPacket(p);
        if (ret == NEXT_PACKET_OK )
        {
            currentFlow = flowAlgorithm->setFlowId(p);
            trace.push(p);
            if(currentFlow > nFlows)
            {
                nFlows = currentFlow;
            }
        }

    }
    LOGGER(INFO, "* Number of flows %ld\n", nFlows);
    LOGGER(INFO, "* Captured Packets %ld\n", captureDriver->getPacketCounter());


    // receive captured data buffer pointers
    QFlow** ppFHead = new QFlow*; 
    QFlow** ppFTail = new QFlow*;
    QFlowPacket** ppPHead = new QFlowPacket*; 
    QFlowPacket** ppPTail = new QFlowPacket*;
    *ppFHead = nullptr;
    *ppFTail = nullptr;
    *ppPHead = nullptr;
    *ppPTail = nullptr;
    trace.consume(ppFHead, ppFTail, ppPHead, ppPTail);

    // print received data
    // QTrace::echo(trace, *ppFHead, *ppFTail, *ppPHead, *ppPTail);

    // send to local database and commit 
    database->receiveData(trace);
    database->receiveData(*ppFHead, *ppFTail);
    database->receiveData(*ppPHead, *ppPTail);
    database->close();

    // Free allocated memory
    LOGGER(DEBUG, "-- QTrace::free()");
    QTrace::free(*ppFHead, *ppFTail, *ppPHead, *ppPTail);
    delete *ppFHead;
    delete *ppFTail;
    delete *ppPHead;
    delete *ppPTail;
    ppFHead = nullptr;
    ppFTail = nullptr;
    ppPHead = nullptr;
    ppPTail = nullptr;

    captureDriver->stop();

    return 0;
}
