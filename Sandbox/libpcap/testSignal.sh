#!/bin/bash


g++ -fdiagnostics-color=always -g testSignal.cpp -o ./testSignal.exe
if [ $? -eq 0 ]; then
    echo "Compilation success"
    echo "----------------------------------------------------------------------------"
    #./testSignal.exe | tee testSignal.log
    ./testSignal.exe
else
    echo "*Compilation error*"
fi





