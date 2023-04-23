#include "UnityTests.h"


void UnityTests::run()
{
    bool t01 = false;
    bool t02 = false;
    bool t03 = false;
    bool t04 = false;
    bool t05 = false;
    bool t06 = false;
    bool t07 = false;
    bool t08 = true;
    if (t01) UnityTests::test_FlowIdCalc();
    if (t02) UnityTests::test_NaiveDatabase_Sniffer_Integration();
    if (t03) UnityTests::test_DriverLibpcap_File();
    if (t04) UnityTests::test_DriverLibpcap_Live();
    if (t05) UnityTests::test_TraceDbManagement();
    if (t06) UnityTests::test_zip_stack();
    if (t07) UnityTests::test_displayTraceDb();
    if (t08) UnityTests::test_testeDeleteFlowDatabase();

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


void UnityTests::test_zip_stack()
{
    TransportProtocol udp = TransportProtocol::UDP;
    protocol_stack v = zip_stack(NetworkProtocol::IPv4, TransportProtocol::UDP, ApplicationProtocol::TLS_SSL);
    printf("<%X>\n", v);
    ApplicationProtocol app = to_application_protocol(v);
    TransportProtocol t = to_transport_protocol(v);
    NetworkProtocol n = to_network_protocol(v);

    v = zip_stack(NetworkProtocol::WOL, TransportProtocol::TCP, ApplicationProtocol::QUIC);
    printf("<%X>\n", v);
    app = to_application_protocol(v);
    t = to_transport_protocol(v);
    n = to_network_protocol(v);

    printf("<%X>\n", v);

}

void UnityTests::test_displayTraceDb()
{
    printf("- test_displayTraceDb\n");
    const char databaseManeger[] = TRACE_DB_V1_NAIVE; 

    ILocalDbService* db = AssetsFactory::makeTraceDatabaseManager(TRACE_DB_V1_NAIVE);
    db->open();
    db->displayTraceDatabase();
    db->close();

    delete db;    
}

void UnityTests::test_testeDeleteFlowDatabase()
{
    printf("> BEFORE\n");
    UnityTests::test_displayTraceDb();

    printf("- test_testeDeleteFlowDatabase\n");
    const char databaseManeger[] = TRACE_DB_V1_NAIVE;
    int ret = 0;

    ILocalDbService* db = AssetsFactory::makeTraceDatabaseManager(databaseManeger);
    db->open();
    ret = db->deleteFlowDatabase("TestSkype");
    db->close();
    
    delete db;

    printf("\n< AFTER\n");
    UnityTests::test_displayTraceDb();
     
}
