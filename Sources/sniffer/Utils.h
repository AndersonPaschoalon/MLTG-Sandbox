#ifndef _UTILS__H_
#define _UTILS__H_ 1


#include <iostream>
#include <string>
#include <algorithm>
#include <cctype>


class StringUtils
{
    public:

        const static std::string toLower(const char* str);

        const static bool fileExists(const char* fileName);

    private:

};

#endif // _UTILS__H_