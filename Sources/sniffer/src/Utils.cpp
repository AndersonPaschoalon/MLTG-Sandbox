#include "Utils.h"

///////////////////////////////////////////////////////////////////////////////
// StringUtils
///////////////////////////////////////////////////////////////////////////////

const std::string StringUtils::toLower(const char *strIn)
{
    std::string str(strIn);
    std::transform(str.begin(), str.end(), str.begin(), [](unsigned char c) { return std::tolower(c); });
    return str;
}

const void StringUtils::lTrim(std::string &s)
{
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](unsigned char ch) {
        return !std::isspace(ch);
    }));
}

const void StringUtils::rTrim(std::string &s)
{
    s.erase(std::find_if(s.rbegin(), s.rend(), [](unsigned char ch) {
        return !std::isspace(ch);
    }).base(), s.end());
}

const void StringUtils::trim(std::string &s)
{
    StringUtils::rTrim(s);
    StringUtils::lTrim(s);
}

const std::string StringUtils::ltrimCopy(std::string s)
{
    StringUtils::lTrim(s);
    return s;
}

const std::string StringUtils::rtrimCopy(std::string s)
{
    StringUtils::rTrim(s);
    return s;
}

const std::string StringUtils::trimCopy(std::string s)
{
    StringUtils::trim(s);
    return s;
}

const std::string StringUtils::to_hex_string(unsigned long n)
{
    std::ostringstream ss;
    ss << std::hex << std::uppercase << n;
    return ss.str();
}

const std::string StringUtils::to_hex_string(unsigned int n)
{
    std::ostringstream ss;
    ss << std::hex << std::uppercase << n;
    return ss.str();
}

const std::string StringUtils::to_hex_string(unsigned short n)
{
    std::ostringstream ss;
    ss << std::hex << std::uppercase << n;
    return ss.str();
}


///////////////////////////////////////////////////////////////////////////////
// OSUtils
///////////////////////////////////////////////////////////////////////////////

const bool OSUtils::fileExists(const char *fileName)
{
    FILE *file;
    if ((file = fopen(fileName, "r")))
    {
        fclose(file);
        return true;
    }
    return false;
}

const bool OSUtils::deleteFileIfExists(const char* filename)
{
    // Check if the file exists
    std::ifstream file(filename);
    bool exists = file.good();
    file.close();

    // If the file exists, delete it
    if (exists)
    {
        if (std::remove(filename) != 0)
        {
            // Error deleting the file
            return false;
        }
    }

    // Return true if the file was deleted or if it did not exist
    return true;
}

