#include "LocalDbServiceV1_Naive.h"

LocalDbServiceV1_Naive::LocalDbServiceV1_Naive()
{
    this->hasCommit = false;
    this->alreadyClosed = false;
}

LocalDbServiceV1_Naive::~LocalDbServiceV1_Naive()
{
    if(this->alreadyClosed != true)
    {
        this->close();
    }
    // already free
    this->db = nullptr;

    // this class does not manage this memory
    this->qTracePtr = nullptr;
}


std::string LocalDbServiceV1_Naive::toString()
{
    return std::string("LocalDbServiceV1_Naive");
}

int LocalDbServiceV1_Naive::open()
{
        int rc = sqlite3_open(FILE_TRACE_DATABASE, &db);
        if (rc) 
        {
            LOGGER(ERROR, "Error opening SQLite database: %s",  sqlite3_errmsg(db));
            return rc;
        }

        const char* sql = "CREATE TABLE IF NOT EXISTS Trace ("
                          "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                          "traceName TEXT NOT NULL,"
                          "traceSource TEXT NOT NULL,"
                          "comment TEXT,"
                          "tsSec INTEGER NOT NULL,"
                          "tsUsec INTEGER NOT NULL"
                          ");";
        rc = sqlite3_exec(db, sql, nullptr, nullptr, nullptr);
        if (rc) 
        {
            LOGGER(ERROR, "Error creating Trace table: %s",  sqlite3_errmsg(db));
            return rc;
        }

        this->hasCommit = false;
        this->alreadyClosed = false;
        return SQLITE_OK;
    }

void LocalDbServiceV1_Naive::receiveData(QTrace &newTrace)
{
    this->qTracePtr = &newTrace;
}

void LocalDbServiceV1_Naive::receiveData(QFlow *head, QFlow *tail)
{
    if(head == nullptr)
    {
        return;
    }

    QFlow* currentNode = head; 
    while(true)
    {
        this->qFlowPtrVec.push_back(currentNode);
        currentNode = currentNode->next();
        if(currentNode == nullptr || currentNode == tail)
        {
            break;
        }
    }
}

void LocalDbServiceV1_Naive::receiveData(QFlowPacket *head, QFlowPacket *tail)
{
    if(head == nullptr)
    {
        return;
    }

    QFlowPacket* currentNode = head; 
    while(true)
    {
        this->qPktPtrVec.push_back(currentNode);
        currentNode = currentNode->next();
        if(currentNode == nullptr || currentNode == tail)
        {
            break;
        }
    }
}

int LocalDbServiceV1_Naive::close()
{
    int ret = 0;
    if (this->alreadyClosed != true)
    {
        int ret = this->commitToFlowDatabase();
        this->hasCommit = true;
        this->alreadyClosed = true;
    }
    return ret;
}

bool LocalDbServiceV1_Naive::hasNewCommit()
{
    bool ret = this->hasCommit;
    this->hasCommit = false;
    return ret;
}

int LocalDbServiceV1_Naive::commitToFlowDatabase()
{
    if(this->qTracePtr == nullptr || this->qTracePtr->getTraceName() == "")
    {
        return false;
    }

    // Open the <traceName>_Flow.db database
    std::string flowDbName = this->qTracePtr->getTraceName() + "_Flow.db";
    int rc = sqlite3_open(flowDbName.c_str(), &this->db);
    if (rc != SQLITE_OK) 
    {
        std::cerr << "Error opening database " << flowDbName << ": " << sqlite3_errmsg(this->db) << std::endl;
        sqlite3_close(this->db);
        return rc;
    }

    // Create the Flows and Packets tables if they don't exist
    rc = sqlite3_exec(this->db, "CREATE TABLE IF NOT EXISTS Flows ("
                                 "flowID INTEGER PRIMARY KEY AUTOINCREMENT,"
                                 "stack INTEGER,"
                                 "portDstSrc INTEGER,"
                                 "net4DstSrcSumm INTEGER,"
                                 "net6DstSrc TEXT,"
                                 "traceName TEXT);",
                      nullptr, nullptr, nullptr);
    if (rc != SQLITE_OK) 
    {
        std::cerr << "Error creating Flows table: " << sqlite3_errmsg(this->db) << std::endl;
        sqlite3_close(this->db);
        return rc;
    }
    rc = sqlite3_exec(this->db, "CREATE TABLE IF NOT EXISTS Packets ("
                                "packetID INTEGER PRIMARY KEY AUTOINCREMENT,"
                                "flowID INTEGER,"
                                "tsSec INTEGER,"
                                "tsUsec INTEGER,"
                                "pktSize INTEGER,"
                                "timeToLive INTEGER,"
                                "FOREIGN KEY (flowID) REFERENCES Flows(flowID));",
                      nullptr, 
                      nullptr, 
                      nullptr);
    if (rc != SQLITE_OK) 
    {
        std::cerr << "Error creating Packets table: " << sqlite3_errmsg(this->db) << std::endl;
        sqlite3_close(this->db);
        return rc;
    }

    // Start a transaction
    sqlite3_exec(db, "BEGIN TRANSACTION", NULL, NULL, NULL);

    // Insert Flows
    flow_id flowId = -1;
    protocol_stack stack; 
    flow_hash portDstSrc;
    flow_hash net4DstSrcSumm;
    std::string net6DstSrc;
    for (QFlow* x: this->qFlowPtrVec)
    {
        x->getQData(flowId, stack, portDstSrc, net4DstSrcSumm, net6DstSrc);
        // Construct the SQL INSERT statement for the current row
        std::string sql =   "INSERT INTO Flows"
                                "(flowID, stack, portDstSrc, net4DstSrcSumm, net6DstSrc, traceName)" 
                            "VALUES" 
                                "(" + std::to_string(flowId) + ", " 
                                    + std::to_string(stack) + ", "
                                    + std::to_string(portDstSrc) + ", " 
                                    + std::to_string(net4DstSrcSumm) + ", "
                                    + net6DstSrc + ")";

        // Execute the INSERT statement
        sqlite3_exec(db, sql.c_str(), NULL, NULL, NULL);
    }
    // Insert Packets
    size_t pktId = -1;
    flowId = -1;
    PacketTimeStamp ts;
    packet_size pktSize;
    ttl timeToLive;
    for (QFlowPacket* x: this->qPktPtrVec)
    {
        x->getQData(pktId, flowId, ts, pktSize, timeToLive);

        // Construct the SQL INSERT statement for the current row
        std::string sql =   "INSERT INTO Flows"
                                "(packetID, flowID, tsSec, tsUsec, pktSize, timeToLive)" 
                            "VALUES" 
                                "(" + std::to_string(pktId) + ", " 
                                    + std::to_string(flowId) + ", "
                                    + std::to_string(ts.sec) + ", " 
                                    + std::to_string(ts.usec) + ", " 
                                    + std::to_string(pktSize) + ", " 
                                    + std::to_string(timeToLive) + ")";

        // Execute the INSERT statement
        sqlite3_exec(db, sql.c_str(), NULL, NULL, NULL);
    }

    // Commit the transaction
    rc = sqlite3_exec(db, "COMMIT TRANSACTION", NULL, NULL, NULL);

    // Close the database connection
    rc = sqlite3_close(db);

    return rc;
}
