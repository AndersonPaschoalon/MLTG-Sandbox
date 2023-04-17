#ifndef _ETHER_DUMMY__H__  
#define _ETHER_DUMMY__H__ 1

#include <vector>
#include "Logger.h"
#include "NetworkPacket.h"
#include "ICaptureDriver.h"

#define DUMMY_DEVICE_FIXED    "fixed" // default
#define DUMMY_DEVICE_RANDOM   "random"

/// @brief This class creates some fixed pre-defined packets. For test purpose only.
class DriverDummy: public ICaptureDriver
{
    public:

        ///////////////////////////////////////////////////////////////////////
        // Class Methods
        ///////////////////////////////////////////////////////////////////////

        DriverDummy();

        ~DriverDummy();

        DriverDummy(const DriverDummy& obj);

        DriverDummy& operator=(DriverDummy other);

        std::string toString();

        ///////////////////////////////////////////////////////////////////////
        // Driver Methods
        ///////////////////////////////////////////////////////////////////////

        // listen device
        int listen(const char* captureType, const char* deviceName, double captureTimeoutSec, long maxPacketCounter);
        int listen(const char* captureType, const char* deviceName);

        // read packets
        int nextPacket(NetworkPacket& packet);

        int stop();

    private:

        bool active;
        size_t currentElement;
        int nPackets;
        std::vector<NetworkPacket>* vecPackets;
        std::string deviceName;

};

#endif // _ETHER_DUMMY__H__