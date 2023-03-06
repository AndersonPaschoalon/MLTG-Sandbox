#include "Utils.h"

const std::string StringUtils::toLower(const char *strIn)
{
    std::string str(strIn);
    std::transform(str.begin(), str.end(), str.begin(), [](unsigned char c) { return std::tolower(c); });
    return str;
}