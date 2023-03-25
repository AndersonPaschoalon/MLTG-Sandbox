#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include <vector>
#include <string>
#include "UnityTests.h"
#include "FlowIdCalc.h"
#include "ISniffer.h"
#include "Sniffer_v01.h"

#define UNITY_TESTS 1





int main()
{
   int retVal = 0;

#ifdef UNITY_TESTS
   // unity tests 
   UnityTests::run();
#else
    // params
    const char traceName[] = "POC";
    const char snifferImplementation[] = "Sniffer_v01";
    const char captureLibrary[] = "";
    const char captureDevice[] = "";
    const char databaseManeger[] = "LocalDbServiceV1_Naive";
    const char flowAlgorithm[] = "FlowIdCalc";
    const char comments[] = "This is the sniffer first proof of concepts.";
    double timeoutSec = 30.0;

    // run sniffer implementation
    ISniffer* sniffer = makeNewSniffer(snifferImplementation);
    sniffer->configure(traceName, captureLibrary, captureDevice, databaseManeger, flowAlgorithm, comments, timeoutSec);
    int ret = sniffer->run();

    return ret;
#endif
   return retVal;
   
}



// ISniffer* makeNewSniffer(const char* snifferImplementation);
// ISniffer* makeNewSniffer(const char* snifferImplementation)
// {
//     ISniffer* snifferImpl = nullptr;
//     if(strcmp(snifferImplementation, "Sniffer_v01") == 0)
//     {
//         snifferImpl = new Sniffer_v01();
//     }
//     else
//     {
//         snifferImpl = new Sniffer_v01();
//     }
//     return snifferImpl;
// }










