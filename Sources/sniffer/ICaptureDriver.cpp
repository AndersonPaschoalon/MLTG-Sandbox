#include "ICaptureDriver.h"

int ICaptureDriver::listen(std::string deviceName)
{
    return this->listen(deviceName, 0);
}

void ICaptureDriver::getDeviceInfo(std::string &deviceName, std::string &lastErrorDescription, time_stamp &captureTimeoutSec)
{
    deviceName.clear();
    lastErrorDescription.clear();
    deviceName = this->deviceName;
    lastErrorDescription = this->lastErrorDetails;
    captureTimeoutSec = this->captureTimeoutSec;
}

