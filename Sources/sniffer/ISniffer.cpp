#include "ISniffer.h"

std::string ISniffer::toString()
{
    std::string traceTypeStr = "";
    if(this->traceType == TraceType::FILE)
    {
        traceTypeStr = "FILE";
    }
    else
    {
        traceTypeStr = "LIVE";
    }
    std::string str = std::string("{traceName: ") + this->traceName +
                      std::string("{captureLibrary: ") + this->captureLibrary +
                      std::string(", traceSourceName: ") + this->captureDevice + 
                      std::string(", traceType: ") + traceTypeStr + 
                      std::string(", databaseManager: ") + this->databaseManager + 
                      std::string(", flowCalcAlgorithm: ") + this->flowCalcAlgorithm + 
                      std::string(", comments: ") + this->comments + 
                      std::string(", timeoutSec: ") + std::to_string(timeoutSec) + 
                      std::string(", maxPacketNumber: ") + std::to_string(maxPacketNumber) +                       
                      std::string("}");
    return str;
}

void ISniffer::configure(const char* traceName, const char *capLybrary, const char *captureDevice, const char *databaseMan, const char *flowAlgorithm, const char* comments, const double timeoutSeconds,  long maxPacketNumber)
{
    this->traceName = std::string(traceName);
    this->captureLibrary = std::string(capLybrary);
    this->captureDevice = std::string(captureDevice);
    this->databaseManager = std::string(databaseMan);
    this->flowCalcAlgorithm = std::string(flowAlgorithm);
    this->comments = std::string(comments);
    this->timeoutSec = timeoutSeconds;
    this->maxPacketNumber = maxPacketNumber;
    if(StringUtils::fileExists(captureDevice))
    {
        this->traceType = TraceType::FILE;
    }
    else
    {
        this->traceType = TraceType::LIVE;
    }
}