#!/bin/bash

#cd bin/
#g++ -fdiagnostics-color=always -g -c ../*.cpp
#g++ -I../*.h  -o test-app *.o  -lm
rm ./bin/*.o
g++ -fdiagnostics-color=always -I./*.h -g *.cpp -o ./bin/test-app.exe  -l sqlite3


