#include "IFlowIdCalc.h"

flow_id IFlowIdCalc::getCurrentFlowId()
{
    return this->lastFlowId.load();
}