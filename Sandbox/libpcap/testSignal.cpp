#include <stdio.h>
#include <csignal>
#include <iostream>
#include <unistd.h>



void signalHandler(int signum)
{
    printf("Interrupt signal (%d) received.\n", signum);
    exit(signum);
}

int main()
{
    printf("Signal register...\n");
    // Register signal handler for SIGINT
    signal(SIGINT, signalHandler);

    // Infinite loop to simulate a long-running program
    while(true)
    {
        printf("Running...\n");
        sleep(1);
    }

    return 0;
}