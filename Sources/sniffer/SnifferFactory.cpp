#include "SnifferFactory.h"


IFlowIdCalc* SnifferFactory::makePacketFlowClassifierAlgorithm(const char *calcAlgorithm)
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

ILocalDbService* SnifferFactory::makeTraceDatabaseManager(const char *manager)
{
    std::string nameLower = StringUtils::toLower(manager);
    if (nameLower == StringUtils::toLower(TRACE_DB_V1_NAIVE))
    {
        // TODO
        ILocalDbService* driver = nullptr;
        return driver;
    }
    else // default
    {
        LOGGER(WARN, "**WARN** Invalid name {%s} on fatory.", manager);
        // TODO
        ILocalDbService* driver = nullptr;
        return driver;        
    }
}

ICaptureDriver* SnifferFactory::makePacketCaptureDriver(const char *driver)
{
    std::string nameLower = StringUtils::toLower(driver);
    if ( nameLower == StringUtils::toLower(DRIVER_ETHER_DUMMY))
    {
        ICaptureDriver* driver = new EtherDummy();
        return driver;
    }
    else if (nameLower == StringUtils::toLower(DRIVER_ETHER_LIBPCAP))
    {
        // TODO
        ICaptureDriver* driver = nullptr;
        return driver;
    }
    else if (nameLower == StringUtils::toLower(DRIVER_ETHER_PFRING))
    {
        // TODO
        ICaptureDriver* driver = nullptr;
        return driver;
    }   
    else if (nameLower == StringUtils::toLower(DRIVER_ETHER_DPDK))
    {
        // TODO
        ICaptureDriver* driver = nullptr;
        return driver;
    }  
    else if (nameLower == StringUtils::toLower(DRIVER_ETHER_LIBTINS))
    {
        // TODO
        ICaptureDriver* driver = nullptr;
        return driver;
    } 
    else if (nameLower == StringUtils::toLower(DRIVER_ETHER_PCAPPLUSPLUS))
    {
        // TODO
        ICaptureDriver* driver = nullptr;
        return driver;
    }                
    else // default
    {
        LOGGER(WARN, "**WARN** Invalid name {%s} on fatory.", driver);
        ICaptureDriver* driver = new EtherDummy();
        return driver;        
    }

}
