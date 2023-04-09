#include "SnifferFactory.h"

SnifferFactory::SnifferFactory()
{
}

std::string SnifferFactory::toString()
{
    return std::string("SnifferFactory");
}

IFlowIdCalc *SnifferFactory::makePacketFlowClassifierAlgorithm(const char *calcAlgorithm)
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

ICaptureDriver* SnifferFactory::makePacketCaptureDriver(const char *driver)
{
    std::string nameLower = StringUtils::toLower(driver);
    if ( nameLower == StringUtils::toLower(DRIVER_DUMMY))
    {
        ICaptureDriver* driver = new DriverDummy();
        return driver;
    }
    else if (nameLower == StringUtils::toLower(DRIVER_LIBPCAP))
    {
        // TODO
        ICaptureDriver* driver = nullptr;
        return driver;
    }
    else if (nameLower == StringUtils::toLower(DRIVER_PFRING))
    {
        // TODO
        ICaptureDriver* driver = nullptr;
        return driver;
    }   
    else if (nameLower == StringUtils::toLower(DRIVER_DPDK))
    {
        // TODO
        ICaptureDriver* driver = nullptr;
        return driver;
    }  
    else if (nameLower == StringUtils::toLower(DRIVER_LIBTINS))
    {
        // TODO
        ICaptureDriver* driver = nullptr;
        return driver;
    } 
    else if (nameLower == StringUtils::toLower(DRIVER_PCAPPLUSPLUS))
    {
        // TODO
        ICaptureDriver* driver = nullptr;
        return driver;
    }                
    else // default
    {
        LOGGER(WARN, "**WARN** Invalid name {%s} on fatory.", driver);
        ICaptureDriver* driver = new DriverDummy();
        return driver;        
    }

}
