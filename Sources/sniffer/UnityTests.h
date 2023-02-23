#ifndef _UNITY_TESTS__H_
#define _UNITY_TESTS__H_ 1

#include <stdio.h>
#include <iostream>

#include "UnityTests.h"
#include "EtherDummy.h"
#include "FlowIdCalc.h"
#include "NetworkPacket.h"
#include "Logger.h"


class UnityTests{

public:
    static void run();

private:

    static void test_FlowIdCalc();


};

#endif // _UNITY_TESTS__H_

