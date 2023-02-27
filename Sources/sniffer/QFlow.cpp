#include "QFlow.h"

void QFlow::setProtocols(NetworkProtocol n, TransportProtocol t, ApplicationProtocol a)
{
    this->stack = zip_stack(n, t, a);
}