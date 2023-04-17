#ifndef __APP_FACTORY__H__
#define __APP_FACTORY__H__ 1


#include "Logger.h"
#include "ISniffer.h"
#include "Sniffer_v01.h"


//
// Sniffer implementation
// 
#define SNIFFER_IMPL_SNIFFERV01            "Sniffer_v01"


class AppFactory
{
    public:

        static ISniffer* makeSniffer(const char* snifferImplementation);

    private:
};



#endif // __APP_FACTORY__H__