#ifndef _ETHER_IF__H_
#define _ETHER_IF__H_ 1

#include <string>
#include <vector>
#include <unistd.h>
#include <iostream>
#include <cstdlib>
#include <signal.h>

#include "NetTypes.h"
#include "NetworkPacket.h"

// packet capture ok, continue
#define DEVICE_SUCCESS                 0
#define NEXT_PACKET_OK                 0
// packet capture finished, no more packets will be readed.
#define STOP_CAPTURE_INTERRUPTED       1
#define STOP_CAPTURE_TIMEOUT           2
#define STOP_CAPTURE_EOF               3
// error reading packets
#define ERROR_LISTEN_NOT_CALLED       -1
#define ERROR_FILE_NOT_EXIST          -2
#define ERROR_CANT_OPEN_DEVICE        -3
#define ERROR_ACESS_DENIED            -4
#define ERROR_CANT_GRAB_PACKET        -5



class ICaptureDriver
{
    public:

        // listen device
        virtual int listen(const char* deviceName, double captureTimeoutSec = 0) = 0;
        virtual int listen(const char* deviceName) = 0;

        // read packets
        virtual int nextPacket(NetworkPacket& packet) = 0;
        // o que pode parar: ultimo pacote (arquivo), timeout ou thread de interrupção.
        virtual bool doContinue();

        // retrieve information
        void getDeviceInfo(std::string& deviceName, std::string& lastErrorDescription, double& captureTimeoutSec);

        // finish device
        virtual int stop() = 0;

    protected:

        // should not be directly updated by derived classes
        static bool interruptionFlag;
        double captureTimeoutSec = 0;

        // in case of sniffing a file, must be set as true at the end
        bool isLastPacket = false;
        // first packet timestamp
        PacketTimeStamp firstTs;
        // must be updated after each new packet captured
        PacketTimeStamp lastTs;
        // device name used by the library
        std::string deviceName = "";
        // must be filled in case of error on device
        std::string lastErrorDetails = "";

        // must be called on listen() to allow interruptions
        void registerSignal();

        // is called by registerSignal()
        static void signalCallbackHander(int signum);

};

#endif // _ETHER_IF__H_