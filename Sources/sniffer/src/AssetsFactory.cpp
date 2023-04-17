#include "AssetsFactory.h"

AssetsFactory::AssetsFactory()
{
}

std::string AssetsFactory::toString()
{
    return std::string("AssetsFactory");
}

IFlowIdCalc *AssetsFactory::makePacketFlowClassifierAlgorithm(const char *calcAlgorithm)
{
    std::string nameLower = StringUtils::toLower(calcAlgorithm);
    if ( nameLower == StringUtils::toLower(FLOW_ID_CALC))
    {
        IFlowIdCalc* flowIdCalc = new FlowIdCalc();
        return flowIdCalc;
    }
    else // default
    {
        LOGGER(WARN, "**WARN** Invalid name {%s} on fatory.", calcAlgorithm);
        IFlowIdCalc* flowIdCalc = new FlowIdCalc();
        return flowIdCalc;        
    }
}

ILocalDbService* AssetsFactory::makeTraceDatabaseManager(const char *manager)
{
    std::string nameLower = StringUtils::toLower(manager);
    if (nameLower == StringUtils::toLower(TRACE_DB_V1_NAIVE))
    {
        // TODO
        ILocalDbService* dbService = new LocalDbServiceV1_Naive();
        return dbService;
    }
    else // default
    {
        LOGGER(WARN, "**WARN** Invalid name {%s} on fatory.", manager);
        // TODO
        ILocalDbService* dbService = nullptr;
        return dbService;        
    }
}

ICaptureDriver* AssetsFactory::makePacketCaptureDriver(const char *driver)
{
    std::string nameLower = StringUtils::toLower(driver);
    if ( nameLower == StringUtils::toLower(DRIVER_DUMMY) || nameLower == StringUtils::toLower(DRIVER_DUMMY2) )
    {
        ICaptureDriver* driver = new DriverDummy();
        return driver;
    }
    if ( nameLower == StringUtils::toLower(DRIVER_CSV) || nameLower == StringUtils::toLower(DRIVER_CSV2) )
    {
        ICaptureDriver* driver = nullptr;
        return driver;
    }    
    else if (nameLower == StringUtils::toLower(DRIVER_LIBPCAP) || nameLower == StringUtils::toLower(DRIVER_LIBPCAP2))
    {
        // TODO
        ICaptureDriver* driver = new DriverLibpcap();
        return driver;
    }
    else if (nameLower == StringUtils::toLower(DRIVER_DPDK) || nameLower == StringUtils::toLower(DRIVER_DPDK2))
    {
        // TODO
        ICaptureDriver* driver = nullptr;
        return driver;
    }  
    else if (nameLower == StringUtils::toLower(DRIVER_LIBTINS) || nameLower == StringUtils::toLower(DRIVER_LIBTINS2))
    {
        // TODO
        ICaptureDriver* driver = nullptr;
        return driver;
    }    
    else // default
    {
        LOGGER(WARN, "**WARN** Invalid name {%s} on fatory.", driver);
        LOGGER(INFO, "Using default capture driver DriverDummy");
        ICaptureDriver* driver = new DriverDummy();
        return driver;        
    }

}

/*
ISniffer *SnifferFactory::makeSniffer(const char *snifferImplementation)
{
    ISniffer* snifferImpl = nullptr;
    if(strcmp(snifferImplementation, "Sniffer_v01") == 0)
    {
        snifferImpl = new Sniffer_v01();
    }
    else
    {
        snifferImpl = new Sniffer_v01();
    }
    return snifferImpl;
}
*/
