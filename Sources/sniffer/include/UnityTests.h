#ifndef _UNITY_TESTS__H_
#define _UNITY_TESTS__H_ 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <iostream>
#include "AppFactory.h"
#include "UnityTests.h"
#include "FlowIdCalc.h"
#include "NetworkPacket.h"
#include "Logger.h"
#include "ILocalDbService.h"
#include "LocalDbServiceV1_Naive.h"
#include "ISniffer.h"
#include "DriverDummy.h"
#include "DriverLibpcap.h"
#include "Sniffer_v01.h"


class UnityTests
{

public:
    static void run();

private:

    static void test_FlowIdCalc();
    static void test_NaiveDatabase_Sniffer_Integration();
    static void test_DriverLibpcap_Live();
    static void test_DriverLibpcap_File();
    static void test_TraceDbManagement();
    static void test_zip_stack();
    static void test_displayTraceDb();
    static void test_testeDeleteFlowDatabase();

};


#endif // _UNITY_TESTS__H_

