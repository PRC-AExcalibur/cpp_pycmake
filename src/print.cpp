
#include "../include/pycmake.h"
#include "internal.h"

void PrintTest()
{
    std::cout<<"helloworld"<<std::endl;
}

void PrintTest(double x)
{
    PrintTest();
    std::cout<<x<<" ^2 = "<<x2(x)<<std::endl;
    std::cout<<x<<" ^3 = "<<x3(x)<<std::endl;
}