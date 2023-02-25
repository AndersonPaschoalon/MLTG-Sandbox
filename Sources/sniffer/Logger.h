#ifndef _LOGGER__H_
#define _LOGGER__H_ 1

#include <cstdio>

enum LogLevel {
    DEBUG,
    INFO,
    WARN,
    ERROR
};

extern LogLevel gLogLevel;

#define LOGGER(level, format, ...) \
    do { \
        if (level >= gLogLevel) { \
            printf(format "\n", ##__VA_ARGS__); \
        } \
    } while(0)


#endif // _LOGGER__H_