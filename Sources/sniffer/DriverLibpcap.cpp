#include "DriverLibpcap.h"

DriverLibpcap::DriverLibpcap()
{
}

DriverLibpcap::~DriverLibpcap()
{
}

DriverLibpcap::DriverLibpcap(const DriverLibpcap &obj)
{
}

DriverLibpcap &DriverLibpcap::operator=(DriverLibpcap other)
{
    // TODO: insert return statement here
    return *this;
}

std::string DriverLibpcap::toString()
{
    return std::string();
}

int DriverLibpcap::listen(const char *deviceName, double captureTimeoutSec, long maxPackets)
{
    return 0;
}

int DriverLibpcap::nextPacket(NetworkPacket &packet)
{
    return 0;
}

int DriverLibpcap::stop()
{
    return 0;
}
