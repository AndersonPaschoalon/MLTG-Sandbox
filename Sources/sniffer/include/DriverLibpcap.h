#ifndef _ETHER_LIBPCAP__H_
#define _ETHER_LIBPCAP__H_ 1

#include <chrono>
#include <iostream>
#include <thread>
#include "Logger.h"
#include "ICaptureDriver.h"
#include "WrapperLibpcap.h"

class DriverLibpcap: public ICaptureDriver
{
    public:

        ///////////////////////////////////////////////////////////////////////
        // Class Methods
        ///////////////////////////////////////////////////////////////////////

        DriverLibpcap();

        ~DriverLibpcap();

        DriverLibpcap(const DriverLibpcap& obj);

        DriverLibpcap& operator=(DriverLibpcap other);

        std::string toString();


        ///////////////////////////////////////////////////////////////////////
        // Driver Methods
        ///////////////////////////////////////////////////////////////////////

        // listen device
        virtual int listen(const char* captureType, const char* deviceName, double captureTimeoutSec, long maxPackets);

        // read packets
        virtual int nextPacket(NetworkPacket& packet);

        // finish device
        virtual int stop();

    private:

        bool active;

        static const int calcMode(const char* captureTypeStr);

};


#endif // _ETHER_LIBPCAP__H_
