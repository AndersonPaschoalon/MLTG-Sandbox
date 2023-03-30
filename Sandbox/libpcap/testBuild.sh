#!/bin/bash

# g++ -fdiagnostics-color=always -I./*.h  -g *.cpp -o ./bin/test-app.exe
# g++ -fdiagnostics-color=always -g *.cpp -lpcap -o ./test-libpcap1.exe
g++ -fdiagnostics-color=always -g test-libpcap2.cpp -lpcap -o ./test-libpcap2.exe
echo "----------------------------------------------------------------------------"
./test-libpcap2.exe | tee test-libpcap2.log

