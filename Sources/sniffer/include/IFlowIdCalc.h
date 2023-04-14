#ifndef _I_FLOW_ID_CALC__H_
#define _I_FLOW_ID_CALC__H_ 1


#include <stdio.h>
#include <string>
#include <iostream>
#include <atomic>
#include "NetworkPacket.h"
#include "NetTypes.h"


class IFlowIdCalc
{
    public:

        virtual std::string toString() = 0;

        virtual flow_id setFlowId(NetworkPacket& packet) = 0;

        flow_id getCurrentFlowId();

    protected:

        std::atomic<flow_id> lastFlowId;

};


#endif // _I_FLOW_ID_CALC__H_