#include <iostream>
#include <vector>
#include <string>

#include "FlowIdCalc.h"

using namespace std;

int main()
{
   vector<string> msg {"Hello", "C++", "World", "from", "VS Code", "and the C++ extension!"};

   printf("Oiiiii\n");

   for (const string& word : msg)
   {
      printf("%s ", word.c_str());
   }
   cout << endl;

   FlowIdCalc flowCalc = FlowIdCalc();
   printf("-- %s\n", flowCalc.toString().c_str());


   return 0;
}