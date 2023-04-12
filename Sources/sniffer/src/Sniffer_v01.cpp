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
    ILocalDbService* database = SnifferFactory::makeTraceDatabaseManager(this->databaseManager.c_str());
    ICaptureDriver* captureDriver = SnifferFactory::makePacketCaptureDriver(this->captureLibrary.c_str());
    IFlowIdCalc* flowAlgorithm = SnifferFactory::makePacketFlowClassifierAlgorithm(this->flowCalcAlgorithm.c_str());

    QTrace trace(this->traceName.c_str(), this->captureDevice.c_str(), this->comments.c_str());
    
    // open database manager
    database->open();

    // start packet capture
    captureDriver->listen(this->captureDevice.c_str(), this->timeoutSec, this->maxPacketNumber);
    int countLoop = 0;
    while(captureDriver->doContinue())
    {
        countLoop++;
        NetworkPacket p;
        // printf("--------------------- %d\n", countLoop);
        int ret = captureDriver->nextPacket(p);
        if (ret == NEXT_PACKET_OK )
        {
            flowAlgorithm->setFlowId(p);
            trace.push(p);
        }

    }
    printf("* Captured Packets %ld\n", captureDriver->getPacketCounter());

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
    printf("-- QTrace::free()\n");
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
