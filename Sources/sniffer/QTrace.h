#ifndef _Q_TRACE__H_
#define _Q_TRACE__H_ 1

#include <string>


class QTrace
{
    private:

        QTrace();

        ~QTrace();

        std::string toString();

        void set(const std::string& traceName,
                 const std::string& traceSource,
                 const std::string& comment,
                 long int tsSec, 
                 long int tsUsec);


    public:


};

#endif  // _Q_TRACE__H_
