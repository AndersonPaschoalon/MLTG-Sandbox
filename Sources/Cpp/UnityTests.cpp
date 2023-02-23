#include "UnityTests.h"


void UnityTests::run()
{
    UnityTests::test_FlowIdCalc();
}

void UnityTests::test_FlowIdCalc()
{
    EtherDummy dummyIf = EtherDummy();
    FlowIdCalc flowCalc;
    dummyIf.listen();
    int i = 0;
    for (i = 0; i < 400; i++)
    {
        NetworkPacket p = dummyIf.pop_back();
        flow_id flowId = flowCalc.setFlowId(p);
        LOGGER(INFO, "* New Flow ID is %zu (packet:%s)", flowId, p.about().c_str());
    } 
    LOGGER(INFO, "*********************************************");
    LOGGER(INFO, "flowCalc.toString():\n%s", flowCalc.toString().c_str());
}