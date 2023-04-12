#!/bin/bash

#cd bin/
#g++ -fdiagnostics-color=always -g -c ../*.cpp
#g++ -I../*.h  -o test-app *.o  -lm
rm ./bin/*.o
g++ -std=gnu++17 -Wdeprecated-declarations -fdiagnostics-color=always \
    -I./headers/  ./src/*.cpp  *.cpp \
    -o ./bin/test-app.exe  \
    -lsqlite3 -lpcap -pthread


