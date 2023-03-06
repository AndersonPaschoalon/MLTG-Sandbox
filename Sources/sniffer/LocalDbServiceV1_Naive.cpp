#include "LocalDbServiceV1_Naive.h"

int LocalDbServiceV1_Naive::open()
{
        int rc = sqlite3_open("TraceDatabase.db", &db);
        if (rc) {
            std::cerr << "Error opening SQLite database: " << sqlite3_errmsg(db) << std::endl;
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
        if (rc) {
            std::cerr << "Error creating Trace table: " << sqlite3_errmsg(db) << std::endl;
            return rc;
        }

        return SQLITE_OK;
    }

void LocalDbServiceV1_Naive::receiveData(QTrace &newTrace)
{
}

void LocalDbServiceV1_Naive::receiveData(QFlow *head, QFlow *tail)
{
}

void LocalDbServiceV1_Naive::receiveData(QFlowPacket *head, QFlowPacket *tail)
{
}

int LocalDbServiceV1_Naive::close()
{
        return 0;
}

bool LocalDbServiceV1_Naive::hasNewCommit()
{
        return false;
}

void LocalDbServiceV1_Naive::commitToFlowDatabase()
{
        // Open the <traceName>_Flow.db database
    std::string flowDbName = traceName + "_Flow.db";
    int rc = sqlite3_open(flowDbName.c_str(), &flowDb);
    if (rc != SQLITE_OK) {
        std::cerr << "Error opening database " << flowDbName << ": " << sqlite3_errmsg(flowDb) << std::endl;
        sqlite3_close(flowDb);
        return;
    }

    // Create the Flows and Packets tables if they don't exist
    rc = sqlite3_exec(flowDb, "CREATE TABLE IF NOT EXISTS Flows ("
                              "flowID INTEGER PRIMARY KEY AUTOINCREMENT,"
                              "stack INTEGER,"
                              "portDstSrc INTEGER,"
                              "net4DstSrcSumm INTEGER,"
                              "net6DstSrc TEXT,"
                              "traceName TEXT);",
                      nullptr, nullptr, nullptr);
    if (rc != SQLITE_OK) {
        std::cerr << "Error creating Flows table: " << sqlite3_errmsg(flowDb) << std::endl;
        sqlite3_close(flowDb);
        return;
    }

    rc = sqlite3_exec(flowDb, "CREATE TABLE IF NOT EXISTS Packets ("
                              "packetID INTEGER PRIMARY KEY AUTOINCREMENT,"
                              "flowID INTEGER,"
                              "tsSec INTEGER,"
                              "tsUsec INTEGER,"
                              "pktSize INTEGER,"
                              "timeToLive INTEGER,"
                              "FOREIGN KEY (flowID) REFERENCES Flows(flowID));",
                      nullptr, nullptr, nullptr);
    if (rc != SQLITE_OK) {
        std::cerr << "Error creating Packets table: " << sqlite3_errmsg(flowDb) << std::endl;
        sqlite3_close(flowDb);
        return;
    }

}
