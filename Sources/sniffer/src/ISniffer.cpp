#include "ISniffer.h"

std::string ISniffer::toString()
{
    std::string traceTypeStr = "";
    std::string str = std::string("{traceName: ") + this->traceName +
                      std::string(", captureType: ") + this->captureType + 
                      std::string(", captureDriver: ") + this->captureDriver +
                      std::string(", traceSourceName: ") + this->captureDevice + 
                      std::string(", databaseManager: ") + this->databaseManager + 
                      std::string(", flowCalcAlgorithm: ") + this->flowCalcAlgorithm + 
                      std::string(", comments: ") + this->comments + 
                      std::string(", timeoutSec: ") + std::to_string(timeoutSec) + 
                      std::string(", maxPacketNumber: ") + std::to_string(maxPacketNumber) +                       
                      std::string("}");
    return str;
}

void ISniffer::configure(const char* traceName,        // capture name
                         const char* captureType,      // live, pcap, ...
                         const char *captureDriver,    // capture engine
                         const char *captureDevice,    // capture interface or file
                         const char *databaseMan,      // class responsible for manager the TraceDatabase
                         const char *flowAlgorithm,    // algorithm used to calc the flowID
                         const char* comments,         // description and details about this trace
                         const double timeoutSeconds,  // timeout in seconds for live captures. Negative numbers means there is no timeout
                         long maxPacketNumber)         // max number of packets for live captures. Negative numbers means there is no limit 
{
    this->traceName = std::string(traceName);
    this->captureType = std::string(captureType);
    this->captureDriver = std::string(captureDriver);
    this->captureDevice = std::string(captureDevice);
    this->databaseManager = std::string(databaseMan);
    this->flowCalcAlgorithm = std::string(flowAlgorithm);
    this->comments = std::string(comments);
    this->timeoutSec = timeoutSeconds;
    this->maxPacketNumber = maxPacketNumber;
}