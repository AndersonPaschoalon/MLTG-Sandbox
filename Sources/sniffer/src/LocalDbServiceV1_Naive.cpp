#include "LocalDbServiceV1_Naive.h"


std::mutex LocalDbServiceV1_Naive::traceDbMutex;

LocalDbServiceV1_Naive::LocalDbServiceV1_Naive()
{
    this->hasCommit = false;
    this->alreadyClosed = false;
    this->receivedFlowPktData = false;
    this->receivedTrace = false;
}

LocalDbServiceV1_Naive::~LocalDbServiceV1_Naive()
{
    if(this->alreadyClosed != true)
    {
        this->close();
    }
    // already free
    this->traceDb = nullptr;
    this->flowDb = nullptr;

}

LocalDbServiceV1_Naive::LocalDbServiceV1_Naive(const LocalDbServiceV1_Naive &obj)
{
    this->traceDb = obj.traceDb;
    this->flowDb = obj.flowDb;
    this->qTrace = obj.qTrace;
    this->qFlowPtrVec = obj.qFlowPtrVec;
    this->qPktPtrVec = obj.qPktPtrVec;
    this->hasCommit = obj.hasCommit;
    this->alreadyClosed = obj.alreadyClosed;
    this->receivedFlowPktData = obj.receivedFlowPktData;
    this->receivedTrace = obj.receivedTrace;    
}

LocalDbServiceV1_Naive &LocalDbServiceV1_Naive::operator=(LocalDbServiceV1_Naive other)
{
    if (this != &other)
    {
        this->traceDb = other.traceDb;
        this->flowDb = other.flowDb;
        this->qTrace = other.qTrace;
        this->qFlowPtrVec = other.qFlowPtrVec;
        this->qPktPtrVec = other.qPktPtrVec;
        this->hasCommit = other.hasCommit;
        this->alreadyClosed = other.alreadyClosed;
        this->receivedFlowPktData = other.receivedFlowPktData;
        this->receivedTrace = other.receivedTrace;    
    }
    return *this;
}

std::string LocalDbServiceV1_Naive::toString()
{
    return std::string("LocalDbServiceV1_Naive");
}

int LocalDbServiceV1_Naive::open()
{
    // create directory db/ if does not exit
    system("mkdir -p db/");

    int rc = sqlite3_open(FILE_TRACE_DATABASE, &this->traceDb);
    if (rc) 
    {
        LOGGER(ERROR, "Error opening SQLite database: %s",  sqlite3_errmsg(this->traceDb));
        return rc;
    }

    const char* sql = "CREATE TABLE IF NOT EXISTS Trace ("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "traceName TEXT NOT NULL, "
                        "traceSource TEXT, "
                        "traceType TEXT, "
                        "comment TEXT, "
                        "nPackets INTEGER, "
                        "nFlows INTEGER, "
                        "duration REAL "                        
                        ");";
    rc = sqlite3_exec(this->traceDb, sql, nullptr, nullptr, nullptr);
    if (rc) 
    {
        LOGGER(ERROR, "Error creating Trace table: %s",  sqlite3_errmsg(this->traceDb));
        return rc;
    }

    this->hasCommit = false;
    this->alreadyClosed = false;
    return SQLITE_OK;
}

bool LocalDbServiceV1_Naive::traceExists(const char *traceName)
{
    bool ret = LocalDbServiceV1_Naive::checkIfTraceExists(traceName, this->traceDb);
    return ret;
}

int LocalDbServiceV1_Naive::receiveData(QTrace newTrace)
{
    // 1 check if the trace name is valid
    std::string tTraceName = StringUtils::trimCopy(newTrace.get(QTRACE_TRACE_NAME));
    if(tTraceName == "" )
    {
        LOGGER(ERROR, "Invalid empty name for trace.");
        return ERROR_INVALID_TRACE_NAME;
    }

    // 2 check if the trace name already exists
    bool doExistTrace = LocalDbServiceV1_Naive::checkIfTraceExists(tTraceName.c_str(), this->traceDb);
    if (doExistTrace == true)
    {
        LOGGER(ERROR, "Cannot create trace entry %s: Already exist!", tTraceName.c_str());
        return ERROR_TRACE_ALREADY_EXISTS;
    }
    std::string flowDbFile = LocalDbServiceV1_Naive::flowDatabaseFileName(tTraceName.c_str());
    bool doExistFile = OSUtils::fileExists(flowDbFile.c_str());
    // if file exists, delete it!
    if(doExistFile == true)
    {
        LOGGER(WARN, "Flow database for trace %s exist, but no entry on TraceDatabase exist. Flow database will be deleted", tTraceName.c_str());
        OSUtils::deleteFileIfExists(flowDbFile.c_str());
    }

    // 3 store the trace object 
    this->qTrace = newTrace;
    this->receivedTrace = true;
    return SUCCESS;
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

    this->receivedFlowPktData = true;
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

    this->receivedFlowPktData = true;    
}

int LocalDbServiceV1_Naive::deleteFlowDatabase(const char *traceName)
{
    LOGGER(INFO, "Deleting trace entry %s...", traceName);
    bool ret1 = LocalDbServiceV1_Naive::deleteTraceByName(traceName, this->traceDb);
    std::string flowDbName = LocalDbServiceV1_Naive::flowDatabaseFileName(traceName);
    LOGGER(INFO, "Deleting file %s...", flowDbName.c_str());
    bool ret2 = OSUtils::deleteFileIfExists(flowDbName.c_str());
    if (ret1 == true && ret2 == true)
    {
        return SUCCESS;
    }
    else if (ret1 == false)
    {
        return ERROR_QUERY_ERROR;
    }
    else if (ret2 == false)
    {
        return ERROR_CANNOT_DELETE_FILE;
    }
    return SUCCESS;
}

void LocalDbServiceV1_Naive::displayTraceDatabase()
{
    std::vector<std::vector<std::string>> allData = LocalDbServiceV1_Naive::getAllTraceData(this->traceDb);
    std::vector<std::string> labels = {"id",
                                       "traceName",
                                       "traceSource",
                                       "traceType",
                                       "comment",
                                       "nPackets",
                                       "nFlows",
                                       "duration (sec)"};   
    Console::printTable(labels, allData);
}


int LocalDbServiceV1_Naive::close()
{
    int ret = 0;
    if (this->alreadyClosed != true && this->receivedTrace == true)
    {
        // commit to trace database
        this->traceId = LocalDbServiceV1_Naive::insertTraceData(this->traceDb, 
                                                                this->qTrace.get(QTRACE_TRACE_NAME).c_str(),
                                                                this->qTrace.get(QTRACE_TRACE_SOURCE).c_str(),
                                                                this->qTrace.get(QTRACE_TRACE_TYPE).c_str(),
                                                                this->qTrace.get(QTRACE_COMMENT).c_str(),
                                                                this->qTrace.getLong(QTRACE_N_PACKETS),
                                                                this->qTrace.getLong(QTRACE_N_FLOWS),
                                                                this->qTrace.getDouble(QTRACE_DURATION));                                                                
        if(this->traceId < 0)
        {
            LOGGER(ERROR, "Error {%d} commiting data to Trace Database!\n", traceId);
            return ERROR_QUERY_ERROR;
        }

        if(this->receivedFlowPktData == true)
        {
            // commit to flow database
            int ret = this->commitToFlowDatabase();
            if(ret != SQLITE_OK)
            {
                LOGGER(ERROR, "Error commiting data to fLOW Database! Code:%d\n", ret);
                return ret;
            }
        }

        // update class flags
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
    std::string traceName = this->qTrace.get(QTRACE_TRACE_NAME);
    if( traceName == "") 
    {
        return false;
    }

    // Open the <traceName>_Flow.db database
    std::string flowDbName =  LocalDbServiceV1_Naive::flowDatabaseFileName(traceName.c_str());
    int rc = sqlite3_open(flowDbName.c_str(), &this->flowDb);
    if (rc != SQLITE_OK) 
    {
        std::cerr << "Error opening database " << flowDbName << ": " << sqlite3_errmsg(this->flowDb) << std::endl;
        sqlite3_close(this->flowDb);
        return rc;
    }

    // Create the Flows and Packets tables if they don't exist
    rc = sqlite3_exec(this->flowDb, "CREATE TABLE IF NOT EXISTS Flows ("
                                    "flowID INTEGER, "
                                    "traceID INTEGER, "
                                    "stack TEXT, "
                                    "portDstSrc TEXT, "
                                    "net4DstSrcSumm TEXT, "
                                    "net6DstSrc TEXT, "
                                    "numberOfPackets INTEGER, "
                                    "PRIMARY KEY (flowID, traceID) "
                                    ");",
                      nullptr, nullptr, nullptr);
    if (rc != SQLITE_OK) 
    {
        std::cerr << "Error creating Flows table: " << sqlite3_errmsg(this->flowDb) << std::endl;
        sqlite3_close(this->flowDb);
        return rc;
    }
    rc = sqlite3_exec(this->flowDb, "CREATE TABLE IF NOT EXISTS Packets ("
                                    "packetID INTEGER, "
                                    "traceID INTEGER, "
                                    "flowID INTEGER, "
                                    "tsSec INTEGER, "
                                    "tsUsec INTEGER, "
                                    "pktSize INTEGER, "
                                    "timeToLive INTEGER, "
                                    "PRIMARY KEY (packetID, traceID), "
                                    "FOREIGN KEY (flowID) REFERENCES Flows(flowID));",
                      nullptr, 
                      nullptr, 
                      nullptr);
    if (rc != SQLITE_OK) 
    {
        std::cerr << "Error creating Packets table: " << sqlite3_errmsg(this->flowDb) << std::endl;
        sqlite3_close(this->flowDb);
        return rc;
    }

    // Start a transaction
    rc = sqlite3_exec(this->flowDb, "BEGIN TRANSACTION", NULL, NULL, NULL);

    // Insert Flows
    flow_id flowId = -1;
    protocol_stack stack; 
    flow_hash portDstSrc;
    flow_hash net4DstSrcSumm;
    std::string net6DstSrc;
    size_t nPackets = 0;
    for (QFlow* x: this->qFlowPtrVec)
    {
        x->getQData(flowId, nPackets, stack, portDstSrc, net4DstSrcSumm, net6DstSrc);
        // Construct the SQL INSERT statement for the current row
        std::string sql =   "INSERT INTO Flows"
                                  "(flowID, traceID, stack, portDstSrc, net4DstSrcSumm, net6DstSrc, numberOfPackets)" 
                            "VALUES" 
                                "(" + std::to_string(flowId) + ", " 
                                    + std::to_string(this->traceId) + ", " 
                                    + '"' + StringUtils::toHexString(stack) + '"' + ", " 
                                    + '"' + StringUtils::toHexString(portDstSrc) + '"' + ", " 
                                    + '"' + StringUtils::toHexString(net4DstSrcSumm) + '"' + ", "                                    
                                    + '"' + net6DstSrc + '"' + ", "  
                                    + std::to_string(nPackets) + 
                                    + " )";

        // Execute the INSERT statement
        rc = sqlite3_exec(this->flowDb, sql.c_str(), NULL, NULL, NULL);
        if (rc != SQLITE_OK) 
        {
            std::cerr << "Error on  sqlite3_exec() on query INSET into Flows table. flowDbName:" 
                    << flowDbName << ", Error: " << sqlite3_errmsg(this->flowDb) << std::endl;
            std::cerr << "Query: " << sql.c_str()<< std::endl;
            sqlite3_close(this->flowDb);
            return rc;
        }
    }
    // Insert Packets
    size_t pktId = -1;
    flowId = -1;
    timeval ts;
    packet_size pktSize;
    ttl timeToLive;
    for (QFlowPacket* x: this->qPktPtrVec)
    {
        x->getQData(pktId, flowId, ts, pktSize, timeToLive);

        // Construct the SQL INSERT statement for the current row
        std::string sql =   "INSERT INTO Packets"
                                "(packetID, traceID, flowID, tsSec, tsUsec, pktSize, timeToLive)" 
                            "VALUES" 
                                "(" + std::to_string(pktId) + ", " 
                                    + std::to_string(this->traceId) + ", "
                                    + std::to_string(flowId) + ", "
                                    + std::to_string(ts.tv_sec) + ", " 
                                    + std::to_string(ts.tv_usec) + ", " 
                                    + std::to_string(pktSize) + ", " 
                                    + std::to_string(timeToLive) + ")";

        // Execute the INSERT statement
        rc = sqlite3_exec(this->flowDb, sql.c_str(), NULL, NULL, NULL);
        if (rc != SQLITE_OK) 
        {
            std::cerr << "Error on  sqlite3_exec() on query INSET into Packets table. flowDbName:" 
                    << flowDbName << ", Error: " << sqlite3_errmsg(this->flowDb) << std::endl;
            sqlite3_close(this->flowDb);
            return rc;
        }
    }

    // Commit the transaction
    rc = sqlite3_exec(this->flowDb, "COMMIT TRANSACTION", NULL, NULL, NULL);
    if (rc != SQLITE_OK) 
    {
            std::cerr << "Error on  sqlite3_exec() on query COMMIT. flowDbName:" 
                    << flowDbName << ", Error: " << sqlite3_errmsg(this->flowDb) << std::endl;
            sqlite3_close(this->flowDb);
            return rc;
    }

    // Close the database connection
    rc = sqlite3_close(this->flowDb);

    return rc;
}


const int LocalDbServiceV1_Naive::insertTraceData(sqlite3* db, 
                                                   const char* traceName, 
                                                   const char* traceSource, 
                                                   const char* traceType, 
                                                   const char* comment, 
                                                   long nPackets, 
                                                   long nFlows,
                                                   double duration)
{
    // first, lock the access to the database
    std::lock_guard<std::mutex> dbLockguard(LocalDbServiceV1_Naive::traceDbMutex);

    /// Start a transaction
    int rc = sqlite3_exec(db, "BEGIN TRANSACTION", NULL, NULL, NULL);
    if (rc != SQLITE_OK) 
    {
        LOGGER(ERROR, "Cannot start transaction. Reason:%s\n", sqlite3_errmsg(db));
        return -1;
    }

    // Prepare the SQL statement with placeholders for the values to be inserted
    const char* sql = "INSERT INTO Trace"
                          "(traceName, traceSource, traceType, comment, nPackets, nFlows, duration) "
                          "VALUES (?, ?, ?, ?, ?, ?, ?) ";
    sqlite3_stmt* stmt;
    rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) 
    {
        LOGGER(ERROR, "Error preparing insert statement: %s", sqlite3_errmsg(db));
        return -2;
    }

    // Bind values to the placeholders in the SQL statement
    rc = sqlite3_bind_text(stmt, 1, traceName, -1, SQLITE_STATIC);
    if (rc != SQLITE_OK)
    {
        LOGGER(ERROR, "Error binding traceName: <%s>, Error Msg: <%s>", traceName, sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -3;
    }

    rc = sqlite3_bind_text(stmt, 2, traceSource, -1, SQLITE_STATIC);
    if (rc != SQLITE_OK) 
    {
        LOGGER(ERROR, "Error binding traceSource: <%s>, Error Msg: <%s>", traceSource, sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -4;
    }

    rc = sqlite3_bind_text(stmt, 3, traceType, -1, SQLITE_STATIC);
    if (rc != SQLITE_OK) 
    {
        LOGGER(ERROR, "Error binding traceType: <%s>, Error Msg: <%s>", traceType, sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -5;
    }    

    rc = sqlite3_bind_text(stmt, 4, comment, -1, SQLITE_STATIC);
    if (rc != SQLITE_OK) 
    {
        LOGGER(ERROR, "Error binding comment <%s>, Error Msg: %s", comment, sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -6;
    }

    rc = sqlite3_bind_int(stmt, 5, nPackets);
    if (rc != SQLITE_OK) 
    {
        LOGGER(ERROR, "Error binding nPackets <%lu>, Error Msg: <%s>", nPackets, sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -7;
    }

    rc = sqlite3_bind_int(stmt, 6, nFlows);
    if (rc != SQLITE_OK) 
    {
        LOGGER(ERROR, "Error binding nFlows <%ld>, Error Msg: <%s>", nFlows, sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -8;
    }

    rc = sqlite3_bind_int(stmt, 7, duration);
    if (rc != SQLITE_OK) 
    {
        LOGGER(ERROR, "Error binding duration: <%f>, Error Msg: <%s>", duration, sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -9;
    }

    // Execute the SQL statement
    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) 
    {
        LOGGER(ERROR, "Error inserting trace data: %s", sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -13;
    }

    // Finalize the prepared statement
    sqlite3_finalize(stmt);

    // Commit the transaction
    rc = sqlite3_exec(db, "COMMIT", nullptr, nullptr, nullptr);
    if (rc != SQLITE_OK) 
    {
        LOGGER(ERROR, "Error committing transaction: %s", sqlite3_errmsg(db));
        return -14;
    }


    int insertedId = sqlite3_last_insert_rowid(db);
    LOGGER(INFO, "Trace %s inserted with ID %d", traceName, insertedId);
    return insertedId;
}

const bool LocalDbServiceV1_Naive::checkIfTraceExists(const char *traceName, sqlite3 *tDb)
{
    bool exists = false;
    sqlite3_stmt* stmt = nullptr;
    const char* sql = "SELECT count(*) FROM Trace WHERE traceName = ?;";
    int rc = sqlite3_prepare_v2(tDb, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        LOGGER(ERROR, "Error preparing SQL statement: %s", sqlite3_errmsg(tDb));
        return false;
    }
    rc = sqlite3_bind_text(stmt, 1, traceName, -1, SQLITE_TRANSIENT);
    if (rc != SQLITE_OK) {
        LOGGER(ERROR, "Error binding parameter: %s", sqlite3_errmsg(tDb));
        sqlite3_finalize(stmt);
        return false;
    }
    rc = sqlite3_step(stmt);
    if (rc == SQLITE_ROW) {
        int count = sqlite3_column_int(stmt, 0);
        exists = count > 0;
    } else if (rc != SQLITE_DONE) {
        LOGGER(ERROR, "Error executing SQL statement: %s", sqlite3_errmsg(tDb));
    }
    sqlite3_finalize(stmt);
    return exists;
}

const bool LocalDbServiceV1_Naive::deleteTraceByName(const char *traceName, sqlite3 *db)
{
    std::string sql = "DELETE FROM Trace WHERE traceName=?";
    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    if (rc != SQLITE_OK) 
    {
        LOGGER(ERROR, "Error preparing delete statement: %s", sqlite3_errmsg(db));
        return false;
    }

    rc = sqlite3_bind_text(stmt, 1, traceName, std::strlen(traceName), SQLITE_TRANSIENT);
    if (rc != SQLITE_OK) 
    {
        LOGGER(ERROR, "Error binding parameter to delete statement: %s", sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return false;
    }

    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) 
    {
        LOGGER(ERROR, "Error deleting trace: %s", sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return false;
    }

    sqlite3_finalize(stmt);
    return true;
}

const std::string LocalDbServiceV1_Naive::flowDatabaseFileName(const char *traceName)
{
    std::string flowDbName =  std::string(DIR_DATABASE) + "/" + std::string(traceName) + 
                              std::string(FILE_FLOW_DB_SUFIX);
    return flowDbName;
}

const std::vector<std::vector<std::string>> LocalDbServiceV1_Naive::getAllTraceData(sqlite3 *tDb)
{
    std::vector<std::vector<std::string>> result;

    const char* sql = "SELECT * FROM Trace;";
    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(tDb, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        LOGGER(ERROR, "Error preparing SELECT statement: %s", sqlite3_errmsg(tDb));
        return result;
    }

    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) 
    {
        int num_cols = sqlite3_column_count(stmt);
        std::vector<std::string> row(num_cols);
        for (int i = 0; i < num_cols; ++i) {
            const char* col_text = reinterpret_cast<const char*>(sqlite3_column_text(stmt, i));
            row[i] = col_text ? col_text : "";
        }
        result.push_back(row);
    }

    sqlite3_finalize(stmt);

    if (rc != SQLITE_DONE) {
        LOGGER(ERROR, "Error getting trace data: %s", sqlite3_errmsg(tDb));
        result.clear();
    }

    return result;
}
