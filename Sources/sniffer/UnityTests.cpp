#include "UnityTests.h"


void UnityTests::run()
{
    // UnityTests::test_FlowIdCalc();
    UnityTests::test_NaiveDatabase();
}

void UnityTests::test_FlowIdCalc()
{
    EtherDummy dummyIf = EtherDummy();
    FlowIdCalc flowCalc;
    dummyIf.listen("DummyDevice");
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

void UnityTests::test_NaiveDatabase()
{

    LocalDbServiceV1_Naive database = LocalDbServiceV1_Naive();
    database.open();
}
