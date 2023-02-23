#!/bin/bash

rm ./bin/*.o
# g++ -fdiagnostics-color=always -I./*.h  -g *.cpp -o ./bin/test-app.exe
g++ -fdiagnostics-color=always -g *.cpp -lpcap -o ./bin/test-libpcap.exe

