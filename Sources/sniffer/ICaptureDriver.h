#ifndef _ETHER_IF__H_
#define _ETHER_IF__H_ 1

#include <string>
#include <vector>
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
        virtual int listen(std::string deviceName, time_stamp captureTimeoutSec = 0) = 0;
        virtual int listen(std::string deviceName);

        // read packets
        virtual int nextPacket(NetworkPacket& packet) = 0;

        // retrieve information
        virtual void getDeviceInfo(std::string& deviceName, std::string& lastErrorDescription, time_stamp& captureTimeoutSec);

        // finish device
        virtual int stop() = 0;

    protected:

        time_stamp captureTimeoutSec = 0;
        std::string deviceName = "";
        std::string lastErrorDetails = "";

};

#endif // _ETHER_IF__H_