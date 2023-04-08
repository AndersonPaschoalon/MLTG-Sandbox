#ifndef _ETHER_LIBPCAP__H_
#define _ETHER_LIBPCAP__H_ 1

#include "ICaptureDriver.h"

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
        virtual int listen(const char* deviceName, double captureTimeoutSec, long maxPackets);

        // read packets
        virtual int nextPacket(NetworkPacket& packet);

        // finish device
        virtual int stop();


    private:

};


#endif // _ETHER_LIBPCAP__H_
