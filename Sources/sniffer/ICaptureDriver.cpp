#include "ICaptureDriver.h"

bool ICaptureDriver::interruptionFlag = false;

int ICaptureDriver::listen(const char* deviceName)
{
    return this->listen(deviceName, 0);
}

bool ICaptureDriver::doContinue()
{
    if(this->captureTimeoutSec > 0)
    {
        double elapsedTime = interArrival(this->firstTs, this->lastTs);
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

    return true;
}

void ICaptureDriver::getDeviceInfo(std::string &deviceName, std::string &lastErrorDescription, double &captureTimeoutSec)
{
}

void ICaptureDriver::signalCallbackHander(int signum)
{
    std::cout << "Caught signal " << signum << std::endl;
    ICaptureDriver::interruptionFlag = true;
}

void ICaptureDriver::registerSignal()
{
    // https://www.tutorialspoint.com/how-do-i-catch-a-ctrlplusc-event-in-cplusplus#:~:text=The%20CTRL%20%2B%20C%20is%20used,to%20the%20current%20executing%20task.
    // Register signal and signal handler
   signal(SIGINT, ICaptureDriver::signalCallbackHander);
}

void ICaptureDriver::getDeviceInfo(std::string &deviceName, std::string &lastErrorDescription, double& captureTimeoutSec)
{
    deviceName.clear();
    lastErrorDescription.clear();
    deviceName = this->deviceName;
    lastErrorDescription = this->lastErrorDetails;
    captureTimeoutSec = captureTimeoutSec;
}

