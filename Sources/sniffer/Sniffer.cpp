#include "Sniffer.h"

const void Sniffer::freeBufferChain(ETHER_BUFFER_NODE *first)
{
    ETHER_BUFFER_NODE* currentNode = first;
    ETHER_BUFFER_NODE* nextNode = NULL;
    while(currentNode != NULL)
    {
        // store next node
        nextNode = currentNode->next;

        // free current node
        delete currentNode->etherPacket;
        currentNode->etherPacket = NULL;
        currentNode = NULL;

        // update current node
        currentNode = nextNode;
    
    } 
    return;
}