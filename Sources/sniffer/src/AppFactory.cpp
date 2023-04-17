#include "AppFactory.h"


ISniffer *AppFactory::makeSniffer(const char *snifferImplementation)
{
    ISniffer* snifferImpl = nullptr;
    
    if(strcmp(snifferImplementation, SNIFFER_IMPL_SNIFFERV01) == 0)
    {
        snifferImpl = new Sniffer_v01();
    }
    else // default
    {
        
        snifferImpl = new Sniffer_v01();
    }
    return snifferImpl;
}

