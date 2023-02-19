#include <iostream>
#include <vector>
#include <string>
#include "FlowIdCalc.h"


void runUnityTests()
{
   // TODO
   return;
}

int main()
{
   int retVal = 0;

#ifdef UNITY_TESTS
#else
   vector<string> msg {"Hello", "C++", "World", "from", "VS Code", "and the C++ extension!"};

   printf("Oiiiii\n");

   for (const string& word : msg)
   {
      printf("%s ", word.c_str());
   }
   cout << endl;

   FlowIdCalc flowCalc = FlowIdCalc();
   printf("-- %s\n", flowCalc.toString().c_str());
#endif



   return retVal;
}