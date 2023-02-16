#include <string>
#include <vector>
#include "NetTypes.h"
#include "Flow.h"


class Trace
{
    public:

        Trace();

        ~Trace();

        std::string toString();

        void set(const std::string& traceName,
                 const std::string& traceSource,
                 const std::string& dateTime,
                 double epochStartTime);

        void addFlow(Flow* flow);


    private:

        std::string traceName;
        std::string traceSource;
        std::string dateTime;
        double epochStartTime;
        std::vector<Flow*> flows;

};
