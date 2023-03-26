#include "EtherLibpcap.h"

EtherLibpcap::EtherLibpcap()
{
}

EtherLibpcap::~EtherLibpcap()
{
}

EtherLibpcap &EtherLibpcap::operator=(EtherLibpcap other)
{
    // TODO: insert return statement here
}

std::string EtherLibpcap::toString()
{
    return std::string();
}

int EtherLibpcap::listen(const char *deviceName, double captureTimeoutSec, long maxPackets)
{
    return 0;
}

int EtherLibpcap::nextPacket(NetworkPacket &packet)
{
    return 0;
}

int EtherLibpcap::stop()
{
    return 0;
}
