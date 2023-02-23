#ifndef _ETHER_DUMMY__H__  
#define _ETHER_DUMMY__H__ 1

#include <vector>
#include "NetworkPacket.h"


class EtherDummy
{
    public:

        EtherDummy();

        ~EtherDummy();

        int listen();

        NetworkPacket& pop_back();

    private:

    int currentElement;
    int nPackets;
    std::vector<NetworkPacket>* vecPackets;

};

#endif // _ETHER_DUMMY__H__