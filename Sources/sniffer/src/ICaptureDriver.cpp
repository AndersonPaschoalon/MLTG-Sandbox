#include "ICaptureDriver.h"

bool ICaptureDriver::interruptionFlag = false;

int ICaptureDriver::listen(const char* captureType, const char* deviceName)
{
    return this->listen(captureType, deviceName, -1, -1);
}

bool ICaptureDriver::doContinue()
{
    if(this->captureTimeoutSec > 0)
    {
        double elapsedTime = inter_arrival(this->firstTs, this->lastTs);
        if (elapsedTime > this->captureTimeoutSec)
        {
            return false;
        }
    }

    if(this->isLastPacket == true)
    {
        return false;
    }

    if(this->interruptionFlag == true)
    {
        return false;
    }

    // -1 -> do not have max number of packets
    if(this->maxPackets > 0)
    {
        if (this->packetCounter > (ulong)this->maxPackets)
        {
            return false;
        }
    }


    return true;
}


void ICaptureDriver::signalCallbackHander(int signum)
{
    std::cout << "Caught signal " << signum << std::endl;
    ICaptureDriver::interruptionFlag = true;
}

void ICaptureDriver::resetVars()
{
    this->captureTimeoutSec = 0;
    this->maxPackets = -1;
    this->isLastPacket = false;
    this->firstTs.tv_sec = 0;
    this->firstTs.tv_usec = 0;
    this->lastTs.tv_sec = 0;
    this->lastTs.tv_usec = 0;
    this->deviceName = "";
    this->lastErrorDetails = "";
    this->packetCounter = 0;
}

void ICaptureDriver::setListenVars(const char* captureType, const char *deviceName, double captureTimeoutSec, long maxPackets)
{
    this->captureType = captureType;
    this->deviceName = deviceName;
    this->captureTimeoutSec = captureTimeoutSec;
    this->maxPackets = maxPackets;
}

void ICaptureDriver::updatePacketCounter()
{
    this->packetCounter++;
}

void ICaptureDriver::registerSignal()
{
    // https://www.tutorialspoint.com/how-do-i-catch-a-ctrlplusc-event-in-cplusplus#:~:text=The%20CTRL%20%2B%20C%20is%20used,to%20the%20current%20executing%20task.
    // Register signal and signal handler
   signal(SIGINT, ICaptureDriver::signalCallbackHander);
}

void ICaptureDriver::getDeviceInfo(std::string& captureType, std::string &deviceName, std::string &lastErrorDescription, double& captureTimeout)
{
    deviceName.clear();
    lastErrorDescription.clear();
    captureType.clear();
    captureType = this->captureType;
    deviceName = this->deviceName;
    lastErrorDescription = this->lastErrorDetails;
    captureTimeout = this->captureTimeoutSec;
}

long ICaptureDriver::getPacketCounter()
{
    return this->packetCounter;
}

timeval ICaptureDriver::getFirstTimestamp()
{
    return this->firstTs;
}

timeval ICaptureDriver::getLastTimestamp()
{
    return this->lastTs;
}
