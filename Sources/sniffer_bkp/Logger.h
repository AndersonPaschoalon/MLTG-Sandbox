#ifndef _LOGGER__H_
#define _LOGGER__H_ 1

#include <cstdio>
//#include <string>

enum LogLevel {
    DEBUG,
    INFO,
    WARN,
    ERROR
};

//enum LogType{
//    CONSOLE,
//    FILE,
//    CONSOLE_FILE,
//};

extern LogLevel gLogLevel;

//extern LogType gLogType;


//#define INIT_LOGGER(configLogType, configLogLevel)\
//    gLogType = configLogType; \
//    gLogLevel = configLogLevel;\


#define LOGGER(level, format, ...) \
    do { \
        if (level >= gLogLevel) { \
            printf(format "\n", ##__VA_ARGS__); \
        } \
    } while(0)


#endif // _LOGGER__H_