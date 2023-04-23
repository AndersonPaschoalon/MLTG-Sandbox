#ifndef _I_LOCAL_DB_SERVICE__H_
#define _I_LOCAL_DB_SERVICE__H_ 1

#include <stdio.h>
#include <string>
#include <vector>
#include <filesystem>
#include "cpptools.h"
#include "Logger.h"
//#include "Utils.h"
#include "NetTypes.h"
#include "QTrace.h"
#include "QFlow.h"
#include "QFlowPacket.h"


#define DIR_DATABASE                 "db"
#define FILE_TRACE_DATABASE          "db/TraceDatabase.db"
#define FILE_FLOW_DB_SUFIX           "_Flow.db"


// error list
#define SUCCESS                       0
#define ERROR_TRACE_ALREADY_EXISTS    -1
#define ERROR_INVALID_TRACE_NAME      -2
#define ERROR_CANNOT_DELETE_FILE      -3
#define ERROR_QUERY_ERROR             -4

class ILocalDbService
{
    public:

        /// @brief Open a connection wiht the database
        /// @return 
        virtual int open() = 0;
        
        /// @brief 
        /// @param traceName 
        /// @return 
        virtual bool traceExists(const char* traceName) = 0;

        /// @brief Receive a data of a new trace. Any new Flow or packet data to be commited will requere a Trace 
        /// data as well.
        /// @param newTrace New trace to be commited. 
        virtual int receiveData(QTrace newTrace) = 0;

        /// @brief Receive the data of a new flow. 
        /// Receive the pointers of the data to be stored in the database. This method only receive the pointer
        /// wich store the data to be commited, and should not be assumed it commit the data itself. 
        /// When the data will be commited, depends on the implementation. 
        /// SimpleTraceDbManager -> commit all the data in a single call after close()
        /// AssyncTraceDbManager -> A separate thread launched on open() isa resposible for managing the databuffer 
        /// from time to time.
        /// the pointers of the linked list are note modified. All alements are internally accesseby by std::vectors,
        /// so they can be modified latter.
        /// receiveData(QTrace& newTrace)        
        /// @param head first element of the linked list to be set
        /// @param tail  last element of the linked list to be set. pass NULL to set all elements
        virtual void receiveData(QFlow* head, QFlow* tail) = 0;

        /// @brief Receive the data of a new flow. 
        /// Receive the pointers of the data to be stored in the database. This method only receive the pointer
        /// wich store the data to be commited, and should not be assumed it commit the data itself. 
        /// When the data will be commited, depends on the implementation. 
        /// SimpleTraceDbManager -> commit all the data in a single call after close()
        /// AssyncTraceDbManager -> A separate thread launched on open() isa resposible for managing the databuffer 
        /// from time to time.
        /// the pointers of the linked list are note modified. All alements are internally accesseby by std::vectors,
        /// so they can be modified latter.
        /// receiveData(QTrace& newTrace)        
        /// @param head first element of the linked list to be set
        /// @param tail  last element of the linked list to be set. pass NULL to set all elements
        virtual void receiveData(QFlowPacket* head, QFlowPacket* tail) = 0;

        /// @brief Delete an existing flow database.
        /// @param traceName 
        /// @return 
        virtual int deleteFlowDatabase(const char* traceName) = 0;

        /// @brief 
        /// @param traces 
        //virtual void selectAllTraces(std::vector<QTrace>& traces) = 0;
        virtual void displayTraceDatabase() = 0;

        /// @brief Close the connection with the database.
        /// @return returns 0 in case of success, and in case of failue will return an error code.
        virtual int close() = 0;

        /// @brief Tells if the database has commited some data since last call of this method. 
        /// If this method returns true, this mean, there are some data structure with the flag hasCommit()
        /// set as true. Therefore they can be deleted with no harm.
        /// It does not keep track of the memory allocation. It will return false if the data is not desalocated.
        /// @return true if there is new data to be commited since last call, false otherwise.
        virtual bool hasNewCommit() = 0;

    private:

};


#endif // _I_LOCAL_DB_SERVICE__H_