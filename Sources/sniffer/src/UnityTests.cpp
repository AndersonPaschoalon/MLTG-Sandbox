#include "UnityTests.h"


void UnityTests::run()
{
    bool t01 = false;
    bool t02 = false;
    bool t03 = true;
    bool t04 = false;
    bool t05 = false;
    if (t01) UnityTests::test_FlowIdCalc();
    if (t02) UnityTests::test_NaiveDatabase_Sniffer_Integration();
    if (t03) UnityTests::test_DriverLibpcap_File();
    if (t04) UnityTests::test_DriverLibpcap_Live();
    if (t05) UnityTests::test_TraceDbManagement();

}

void UnityTests::test_FlowIdCalc()
{
    DriverDummy dummyIf;
    FlowIdCalc flowCalc;
    
    dummyIf.listen("live", "DummyDevice");
    int i = 0;
    for (i = 0; i < 1000000; i++)
    {
        NetworkPacket p;
        int ret = dummyIf.nextPacket(p);
        if(ret != NEXT_PACKET_OK)
        {
            LOGGER(ERROR, "**ERROR READING PACKET FROM INTERFACE**");
            break;
        }
        flow_id flowId = flowCalc.setFlowId(p);
        //LOGGER(INFO, "* New Flow ID is %zu (packet:%s)", flowId, p.about().c_str());
    }
    dummyIf.stop();
    LOGGER(INFO, "*********************************************");
    LOGGER(INFO, "flowCalc.toString():\n%s", flowCalc.toString().c_str());
}

void UnityTests::test_NaiveDatabase_Sniffer_Integration()
{
    const char traceName[] = "POC";
    const char snifferImplementation[] = "Sniffer_v01";
    const char captureDriver[] = "DriverDummy";
    const char captureType[] = "live";
    const char captureDevice[] = "";
    const char databaseManeger[] = "LocalDbServiceV1_Naive";
    const char flowAlgorithm[] = "FlowIdCalc";
    const char comments[] = "This is the sniffer first proof of concepts.";
    double timeoutSec = 30.0;
    long maxPacketNumber = 1000000;
    //long maxPacketNumber = 10;

    // run sniffer implementation
    ISniffer* sniffer = AppFactory::makeSniffer(snifferImplementation);
    sniffer->configure(traceName, captureType, captureDriver, captureDevice, databaseManeger, flowAlgorithm, comments, timeoutSec, maxPacketNumber);
    int ret = sniffer->run();
}

void UnityTests::test_DriverLibpcap_Live()
{
    DriverLibpcap driverLibpcap;
    driverLibpcap.listen("live", "eth0", 30, 100);
    while ( true)
    {
        bool ret = driverLibpcap.doContinue();
        if(ret == false)
        {
            break;
        }
        NetworkPacket p;
        driverLibpcap.nextPacket(p);
        LOGGER(INFO, "[Captured Packet] %s", p.toString().c_str());
    }
}

void UnityTests::test_DriverLibpcap_File()
{
    const char traceName[] = "01_SkypeIRC.cap.pcap";
    const char captureDevice[] = "../../../Pcap/SkypeIRC.cap.pcap";
    // const char traceName[] = "01_bigFlows.pcap";
    // const char captureDevice[] = "../../../Pcap/bigFlows.pcap";
    // const char traceName[] = "lanDiurnal.pcap";
    // const char captureDevice[] = "../../../../../Pcaps/Pcaps/lanDiurnal.pcap";
    // const char traceName[] = "lan-firewall-1h.pcap";
    // const char captureDevice[] = "../../../../../Pcaps/Pcaps/lan-firewall-1h.pcap";    
    // const char traceName[] = "equinix-1s.pcap";
    // const char captureDevice[] = "../../../../../Pcaps/Pcaps/equinix-1s.pcap";

    const char snifferImplementation[] = "Sniffer_v01";
    const char captureDriver[] = "DriverLibpcap";
    const char captureType[] = "pcap";
    const char databaseManeger[] = "LocalDbServiceV1_Naive";
    const char flowAlgorithm[] = "FlowIdCalc";
    const char comments[] = "This is the sniffer first proof of concepts.";
    double timeoutSec = -1;
    // long maxPacketNumber = 1000000;
    long maxPacketNumber = -1;

    // run sniffer implementation
    ISniffer* sniffer = AppFactory::makeSniffer(snifferImplementation);
    sniffer->configure(traceName, captureType, captureDriver, captureDevice, databaseManeger, flowAlgorithm, comments, timeoutSec, maxPacketNumber);
    int ret = sniffer->run();
}

void UnityTests::test_TraceDbManagement()
{
    const char traceName[] = "POC3";
    const char snifferImplementation[] = "Sniffer_v01";
    const char captureDriver[] = "DriverDummy";
    const char captureType[] = "pcap";
    const char captureDevice[] = "";
    const char databaseManeger[] = "LocalDbServiceV1_Naive";
    const char flowAlgorithm[] = "FlowIdCalc";
    const char comments[] = "This is the sniffer first proof of concepts.";
    double timeoutSec = 30.0;
    long maxPacketNumber = 100;
    //long maxPacketNumber = 10;

    // run sniffer implementation
    ISniffer* sniffer = AppFactory::makeSniffer(snifferImplementation);
    sniffer->configure(traceName, captureType, captureDriver,  captureDevice, databaseManeger, flowAlgorithm, comments, timeoutSec, maxPacketNumber);
    int ret = sniffer->run();
}

