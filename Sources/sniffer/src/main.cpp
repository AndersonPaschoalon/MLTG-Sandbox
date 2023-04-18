#include <unistd.h> // for getopt function
#include <getopt.h>
#include <iostream>
#include <string>
#include <cstdlib>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <vector>
#include "AppFactory.h"
#include "AssetsFactory.h"
#include "UnityTests.h"
#include "FlowIdCalc.h"
#include "ISniffer.h"
#include "Sniffer_v01.h"


// #define RUN_UNITY_TESTS 1


const char VERSION[] = ""
"SIMITAR sniffer.exe                                                           \n"
"Version: 0.0.0.1                                                              \n"
"Author: Anderson Paschoalon.                                                  \n"
"                                                                              \n"
" Copyright (c) 2023 Anderson Paschoalon                                       \n"
"                                                                              \n"
" Permission is hereby granted, free of charge, to any person obtaining a copy \n"
" of this software and associated documentation files (the 'Software'), to deal\n"
" in the Software without restriction, including without limitation the rights \n"
" to use, copy, modify, merge, publish, distribute, sublicense, and/or sell    \n"
" copies of the Software, and to permit persons to whom the Software is        \n"
" furnished to do so, subject to the following conditions:                     \n"
"                                                                              \n"
" The above copyright notice and this permission notice shall be included in   \n"
" all copies or substantial portions of the Software.                          \n"
"                                                                              \n"
" THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR   \n"
" IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,     \n"
" FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  \n"
" AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER       \n"
" LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
" OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN    \n"
" THE SOFTWARE.                                                                \n"
"";


const char HELP_USAGE[] = ""
"Usage: sniffer.exe [OPTIONS]                                                 \n"
"                                                                             \n"
"Sniffer to capture trace data into Sqlite databases.                         \n"
"                                                                             \n"
"Execute a live capture on eth0 for 30 seconds.                               \n"
"	sniffer.exe --type live --src eth0 --lib libpcap                          \n"
"		--name LiveCapture_eth0_30s --timeout 30                              \n"
"                                                                             \n"
"Execute a pcap capture in a pcap file called sample_http.pcap.               \n"
"	sniffer.exe --type pcap --src sample_http.pcap --lib libpcap              \n"
"		--name http.pcap                                                      \n"
"                                                                             \n"
"Display the table of captured traces currently stored.                       \n"
"	sniffer.exe --show                                                        \n"
"                                                                             \n"
"Display this help tutorial:                                                  \n"
"	sniffer.exe --help	                                                      \n"
"                                                                             \n"
"Display the application version:                                             \n"
"	sniffer.exe --version                                                     \n"
"                                                                             \n"
"Options:                                                                     \n"
"                                                                             \n"
" Options for traffic capture are:                                            \n"
"  -n, --name        NAME  Specify the name of the capture (required).        \n"
"                           Eg.: ethernetCapture01                            \n"
"  -y, --type        TYPE  Specify the type of capture.                       \n"
"                           Available values are: live, pcap, nspcap.         \n"
"  -d, --device      DEV   Specify the source of the program. For captures    \n"
"                           (pcaps, nspcap) you should point to the file, for \n"
"                           live you should use the ethernet interface.       \n"
"                           Eg.: file.pcap, eth0, ...                         \n"
"  -i, --driver      DRIV  Specify the library to use.                        \n"
"                           Available values are: libpcap, dummy, csv.        \n"
"  -l, --link        NAME  Specify the Link Layer protocol of the trace.      \n"
"                           Supported values are:                             \n"
"                           ethernet, ieee802.11                              \n"
"  -t, --timeout     TIME  Specify the timeout for live captures the program  \n"
"                           in seconds.                                       \n"
"                           Default is -1 (no timeout).                       \n"
"  -m, --maxpackets  MAX   Specify the maximum number of packets to be        \n"
"                           captured for live captures.                       \n"
"                           Default is -1 (capture all).                      \n"
"                                                                             \n"
" For other actions the options are:                                          \n"
"                                                                             \n"
"  -r, --remove      NAME  Remove the trace NAME entry on TraceDatabase, and  \n"
"                           and delete the Packet/Flows table.                \n"
"  -w, --show              Display the TraceDatabase information and exit.    \n"
"  -v, --version           Display the version of the program and exit.       \n"
"  -h, --help              Display this help message and exit.                \n"
"";


/// @brief 
void showVersion();


/// @brief 
void showHelp();


/// @brief 
void displayTracesInformation();


/// @brief 
/// @param captureName 
int deleteCapture(const char* captureName);

/// @brief 
/// @param traceName 
/// @param linkProtocol 
/// @param captureType 
/// @param captureDriver 
/// @param captureDevice 
/// @param comments 
/// @param timeoutSeconds 
/// @param maxPacketNumber 
/// @return 
int executeCapture(const char* traceName,        // capture name
                   LinkProtocol linkProtocol,    // link protocol
                   const char* captureType,      // live, pcap, ...
                   const char *captureDriver,    // capture engine
                   const char *captureDevice,    // capture interface or file
                   const char* comments,         // description and details about this trace
                   const double timeoutSeconds,  // timeout in seconds for live captures. Negative numbers means there is no timeout
                   long maxPacketNumber);        // max number of packets for live captures. Negative numbers means there is no limit 


/// @brief 
void runUnityTests();


int main(int argc, char* argv[]) 
{
#ifndef RUN_UNITY_TESTS

    // init values
    std::string type = "live";
    std::string device = "";
    int timeout = -1;
    int maxpackets = -1;
    std::string driver = "libpcap";
    std::string name = "";
    std::string traceToDelete = "";
    std::string comments = "no comment";
    LinkProtocol link = LinkProtocol::ETHERNET;
    bool show = false;
    bool version = false;
    bool help = false;
	bool unitytests = false;
    int retVal = 0;

    // Define the options
    struct option long_options[] = {
        {"type", required_argument, 0, 'y'},
        {"device", required_argument, 0, 'd'},
        {"timeout", required_argument, 0, 't'},
        {"maxpackets", required_argument, 0, 'm'},
        {"driver", required_argument, 0, 'i'},
        {"name", required_argument, 0, 'n'},
        {"comments", required_argument, 0, 'c'},
        {"link", required_argument, 0, 'l'},
        {"remove", required_argument, 0, 'r'},
        {"show", no_argument, 0, 'w'},
        {"version", no_argument, 0, 'v'},
        {"help", no_argument, 0, 'h'},
		{"unitytests", no_argument, 0, 'u'},
        {0, 0, 0, 0}
    };

    // Parse the options
    int option_index = 0;
    int c;
    while ((c = getopt_long(argc, argv, "y:d:t:m:i:n:c:l:r:wvhu", long_options, &option_index)) != -1) 
    {
        switch (c) {
            case 'y':
                type = optarg;
                break;
            case 'd':
                device = optarg;
                break;
            case 't':
                timeout = std::stoi(optarg);
                break;
            case 'm':
                maxpackets = std::stoi(optarg);
                break;
            case 'i':
                driver = optarg;
                break;
            case 'n':
                name = optarg;
                break;
            case 'c':
                comments = optarg;
                break;
            case 'l':
                link = to_link_protocol(optarg);
                break;
            case 'r':
                traceToDelete = optarg;
                break;
            case 'w':
				show = true;
            case 'u':
				unitytests = true;				
                break;
            case 'v':
                version = true;
                break;
            case 'h':
                help = true;
                break;
            default:
                std::cerr << "Invalid option: " << optarg << std::endl;
                return 1;
        }
    }

    // Print the values of the variables
    /**
    std::cout << "type = " << type << std::endl;
    std::cout << "device = " << device << std::endl;
    std::cout << "timeout = " << timeout << std::endl;
    std::cout << "maxpackets = " << maxpackets << std::endl;
    std::cout << "driver = " << driver << std::endl;
    std::cout << "name = " << name << std::endl;
    std::cout << "traceToDelete = " << traceToDelete << std::endl;
    std::cout << "show = " << std::boolalpha << show << std::endl;
    std::cout << "version = " << std::boolalpha << version << std::endl;
    std::cout << "help = " << std::boolalpha << help << std::endl;
	std::cout << "unitytests = " << std::boolalpha << unitytests << std::endl;
    */

    if (help)
    {
        showHelp();
    }
    else if(version)
    {
        showVersion();
    }
    else if(unitytests)
    {
        runUnityTests();
    }
    else if(show)
    {
        displayTracesInformation();
    }
    else if(traceToDelete != "")
    {
        retVal = deleteCapture(traceToDelete.c_str());
    }
    else if (type != "" && device != "" && driver != "" && name != "")
    {
        retVal = executeCapture(name.c_str(),
                                link,
                                type.c_str(), 
                                driver.c_str(), 
                                device.c_str(), 
                                comments.c_str(), 
                                timeout, 
                                maxpackets);
    }
    else if (type == "" )
    {
        printf("Missing mandatory argument --type\n");
        retVal = 1;
    }    
    else if (device == "" )
    {
        printf("Missing mandatory argument --device\n");
        retVal = 1;
    }
    else if (driver == "" )
    {
        printf("Missing mandatory argument --driver\n");
        retVal = 1;
    }
    else if (name == "" )
    {
        printf("Missing mandatory argument --name\n");
        retVal = 1;
    }

    return retVal;
#else
    runUnityTests();
    return 0;
#endif
}

void showHelp()
{
    printf("%s", HELP_USAGE);
}

void showVersion()
{
    printf("%s", VERSION);
}

void runUnityTests()
{
    UnityTests::run();
}

void displayTracesInformation()
{ 
    printf("displayTracesInformation\n");
    // todo
}

int deleteCapture(const char* captureName)
{
    // todo
    printf("deleteCapture\n");
    return 0;
}


int executeCapture(const char* traceName,        // capture name
                   LinkProtocol linkProtocol,    // link protocol
                   const char* captureType,      // live, pcap, ...
                   const char *captureDriver,    // capture engine
                   const char *captureDevice,    // capture interface or file
                   const char* comments,         // description and details about this trace
                   const double timeoutSeconds,  // timeout in seconds for live captures. Negative numbers means there is no timeout
                   long maxPacketNumber)         // max number of packets for live captures. Negative numbers means there is no limit 
{
    const char databaseManeger[] = TRACE_DB_V1_NAIVE; 
    const char flowAlgorithm[] = FLOW_ID_CALC;

    ISniffer* sniffer = AppFactory::makeSniffer(SNIFFER_IMPL_SNIFFERV01);
    sniffer->configure(traceName, captureType, captureDriver, captureDevice, databaseManeger, flowAlgorithm, comments, timeoutSeconds, maxPacketNumber);
    int ret = sniffer->run();    

    return ret;

    /*
    std::cout << "traceName = " << traceName << std::endl;
    std::cout << "linkProtocol = " << linkProtocol << std::endl;
    std::cout << "captureType = " << captureType << std::endl;
    std::cout << "captureDriver = " << captureDriver << std::endl;
    std::cout << "captureDevice = " << captureDevice << std::endl;
    std::cout << "comments = " << comments << std::endl;
    std::cout << "timeoutSeconds = " << timeoutSeconds << std::endl;
    std::cout << "maxPacketNumber = " << maxPacketNumber << std::endl;
    return 0;
    **/
}

