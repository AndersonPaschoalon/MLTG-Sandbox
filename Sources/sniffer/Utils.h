#ifndef _UTILS__H_
#define _UTILS__H_ 1


#include <iostream>
#include <string>
#include <algorithm>
#include <cctype>
#include <cstdio>    // For remove()
#include <fstream>   // For ifstream

class StringUtils
{
    public:

        //
        // String operations
        //

        const static std::string toLower(const char* str);

        const static void lTrim(std::string &s);

        const static void rTrim(std::string &s);

        const static void trim(std::string &s);

        const static std::string ltrimCopy(std::string s);

        const static std::string rtrimCopy(std::string s);

        const static std::string trimCopy(std::string s);

    private:

};

class OSUtils
{
    public:

        const static bool fileExists(const char* fileName);

        const static bool deleteFileIfExists(const char* filename);

    private:

};


#endif // _UTILS__H_