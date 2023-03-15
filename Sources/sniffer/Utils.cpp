#include "Utils.h"

const std::string StringUtils::toLower(const char *strIn)
{
    std::string str(strIn);
    std::transform(str.begin(), str.end(), str.begin(), [](unsigned char c) { return std::tolower(c); });
    return str;
}

const bool StringUtils::fileExists(const char *fileName)
{
    FILE *file;
    if ((file = fopen(fileName, "r")))
    {
        fclose(file);
        return true;
    }
    return false;
}
