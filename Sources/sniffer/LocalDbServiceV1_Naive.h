#ifndef _LOCAL_DB_SERVICE_V1_NAICE_H__
#define _LOCAL_DB_SERVICE_V1_NAICE_H__  1

#include <iostream>
#include <sqlite3.h>
#include "ILocalDbService.h"


class LocalDbServiceV1_Naive: public ILocalDbService
{
    public: 
        int open();

        /// @brief Receive a data of a new trace. Any new Flow or packet data to be commited will requere a Trace 
        /// data as well.
        /// @param newTrace New trace to be commited. 
        void receiveData(QTrace& newTrace);

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
        void receiveData(QFlow* head, QFlow* tail);

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
        void receiveData(QFlowPacket* head, QFlowPacket* tail);

        /// @brief Close the connection with the database.
        /// @return returns 0 in case of success, and in case of failue will return an error code.
        int close();

        /// @brief Tells if the database has commited some data since last call of this method. 
        /// If this method returns true, this mean, there are some data structure with the flag hasCommit()
        /// set as true. Therefore they can be deleted with no harm.
        /// It does not keep track of the memory allocation. It will return false if the data is not desalocated.
        /// @return true if there is new data to be commited since last call, false otherwise.
        bool hasNewCommit();


    private:

        sqlite3* db;

        void commitToFlowDatabase();

};


#endif // _LOCAL_DB_SERVICE_V1_NAICE_H__