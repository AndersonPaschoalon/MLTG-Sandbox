#include "DriverLibpcap.h"

DriverLibpcap::DriverLibpcap()
{
    this->active = false;
}

DriverLibpcap::~DriverLibpcap()
{
}

DriverLibpcap::DriverLibpcap(const DriverLibpcap &obj)
{
    this->active = obj.active; 
}

DriverLibpcap &DriverLibpcap::operator=(DriverLibpcap other)
{
    if(this != &other)
    {
        this->active = other.active;
    }
    return *this;
}

std::string DriverLibpcap::toString()
{
    return std::string();
}

int DriverLibpcap::listen(const char* captureType, const char *deviceName, double captureTimeoutSec, long maxPackets)
{
    this->setListenVars(captureType, deviceName, captureTimeoutSec, maxPackets);
    int mode = DriverLibpcap::calcMode(captureType);
    this->active = true;
    initialize_libpcap_wrapper();
    std::thread t(start_capture, mode, deviceName, captureTimeoutSec, maxPackets);
    t.detach();
    return 0;
}

int DriverLibpcap::nextPacket(NetworkPacket &packet)
{
    if(this->active == false)
    {
        return ERROR_LISTEN_NOT_CALLED;
    }

    int ret = ERROR_LISTEN_NOT_CALLED;
    bool queueRet = false;
    while (true)
    {
        NetworkPacket* ptrPkt = nullptr;
        queueRet = gPacketsQueue->try_pop(ptrPkt);
        // 1. the queue is empty, but there are packets to be pushed, stopCapture == 0
        // 2. the queue is empty, but there are no packets to be pushed, stopCapture == 1
        if(queueRet == false)
        {
            if (gEndOfFile == 1)
            {
                ret  = STOP_CAPTURE_EOF;
                // Set the flag, so doContinue() will return with false, and the loop will break
                this->isLastPacket = true;
                break;
            }
            else if (gStopCapture == 1 )
            {
                ret  = STOP_CAPTURE_INTERRUPTED;
                // Set the flag, so doContinue() will return with false, and the loop will break
                this->isLastPacket = true;
                break;
            }
            else
            {
                // sleep for a while, to wait new packets to be captured
                std::this_thread::sleep_for(std::chrono::seconds(1));
                LOGGER(INFO, "Waiting for the next packet...");
            }
        }
        else
        {
            ret = NEXT_PACKET_OK;
            packet = *ptrPkt;
            delete ptrPkt;
            
            // update parent class state
            this->updatePacketCounter();
            break;
        }        
    }

    // update current timestamp to check the timeout
    this->lastTs = {
        .tv_sec = gCurrentTimeStamp.tv_sec,
        .tv_usec = gCurrentTimeStamp.tv_usec,
    };

    return ret;
}

int DriverLibpcap::stop()
{
    finalize_libpcap_wrapper();
    return 0;
}

const int DriverLibpcap::calcMode(const char *captureTypeStr)
{
    std::string modeStr = StringUtils::toLower(StringUtils::trimCopy(captureTypeStr).c_str());
    if (modeStr == "live")
    {
        return 0;
    }
    else if (modeStr == "pcap")
    {
        return 1;
    }
    else if (modeStr == "pcapng")
    {
        return 2;
    }
    LOGGER(WARN, "Invalid captureTypeStr:%s, using default live", modeStr.c_str());
    LOGGER(INFO, "Available values are: live, pcap");
    return 0;
}
