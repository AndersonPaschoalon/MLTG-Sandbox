#!/bin/bash

g++ -std=gnu++17 -Wdeprecated-declarations -fdiagnostics-color=always  -g \
    -I./include -I./libs/cpptools/include  \
	src/*.cpp  \
    -o ./bin/test-app.exe  \
    -lsqlite3 -lpcap -pthread \
	libs/cpptools/bin/libcpptools.a 


