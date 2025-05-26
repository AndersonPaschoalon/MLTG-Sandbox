#!/bin/bash


g++ -fdiagnostics-color=always -g test-libpcap1.cpp -lpcap -o ./test-libpcap1.exe
if [ $? -eq 0 ]; then
    echo "Compilation success"
    echo "----------------------------------------------------------------------------"
    ./test-libpcap1.exe 
else
    echo "*Compilation error*"
fi





