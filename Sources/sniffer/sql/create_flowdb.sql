CREATE TABLE IF NOT EXISTS Flows (
    flowID INTEGER, 
    traceID INTEGER, 
    stack TEXT, 
    portDstSrc TEXT, 
    net4DstSrcSumm TEXT, 
    net6DstSrc TEXT, 
    numberOfPackets INTEGER, 
    PRIMARY KEY (flowID, traceID) 
);


CREATE TABLE IF NOT EXISTS Packets (
    packetID INTEGER, 
    traceID INTEGER, 
    flowID INTEGER, 
    tsSec INTEGER, 
    tsUsec INTEGER, 
    pktSize INTEGER, 
    timeToLive INTEGER, 
    PRIMARY KEY (packetID, traceID), 
    FOREIGN KEY (flowID) REFERENCES Flows(flowID)
);