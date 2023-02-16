#include <string>
#include <vector>
#include "NetTypes.h"
#include "NetworkPacket.h"

typedef struct ether_buffer_node
{
    NetworkPacket* etherPacket;
    struct ether_buffer_node* next;

} ETHER_BUFFER_NODE;

class EtherIf
{
    public:
        EtherIf(TraceType traceType, const std::string& traceSourceName, CaptureLibrary lib, double timeout = 30000);

        ~EtherIf();

        bool listen();

        /// @brief Tells of the buffer is empty or not. It do not mean the parsing process finished.
        /// You mau call hasEnded() to check if the execution finished or not.
        /// If it did not finished, tt is recommended to call sleep() before calling hasPackets(). 
        /// @return 
        bool hasPackets();

        bool hasEnded();

        // este metodo deve retornar o ponteiro para o promeiro elemento do buffer, e atualizar o 
        // elemento firstNode para Null. A ideia é que endereço do buffer seja retornado, para que
        // ele possa ser consumido. quando um novo pacote chegar, o buffer estará vazio.
        ETHER_BUFFER_NODE* getBuffer();

        // Utils

        // dorme por alguns ms, para aguardar mais pacotes
        bool sleep();

        static const void freeBufferChain(ETHER_BUFFER_NODE* first);

    private:

        // pointer to the buffer first node
        ETHER_BUFFER_NODE* firstNode;

        // timeout, for live captures
        double timeout;

        // for live captures
        double timeAlive;

        // for files it is set when the parsing pcap procedure finished.
        // for live captures it is set when the timeAlive is larger than the timeout.
        double executionFinished;

};