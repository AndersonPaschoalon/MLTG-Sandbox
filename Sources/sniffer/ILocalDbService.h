
// open()
// Receive the pointers of the data to be stored in the database. This method only receive the pointer
// wich store the data to be commited, and should not be assumed it commit the data itself. 
// When the data will be commited, depends on the implementation. 
// SimpleTraceDbManager -> commit all the data in a single call after close()
// AssyncTraceDbManager -> A separate thread launched on open() isa resposible for managing the databuffer from time to time.
// head - first element of the linked list to be set
// tail - last element of the linked list to be set. pass NULL to set all elements
// the pointers of the linked list are note modified. All alements are internally accesseby by std::vectors,
// so they can be modified latter.
// receiveData(QTrace& newTrace)
// receiveData(QFlow* head, QFlow* tail)
// receiveData(QFlowPacket* head, QFlowPacket* tail)
// hasNewCommit() -> tells if the database has commited some data since last call of this method. 
//                   If this method returns true, this mean, there are some data structure with the flag hasCommit()
//                   set as true. Therefore they can be deleted with no harm.
//                   It does not keep track of the memory allocation. It will return false if the data is not desalocated.
// close()
