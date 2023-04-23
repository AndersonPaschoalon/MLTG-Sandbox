CREATE TABLE IF NOT EXISTS Trace (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    traceName TEXT NOT NULL, 
    traceSource TEXT, 
    traceType TEXT, 
    comment TEXT, 
    nPackets INTEGER, 
    nFlows INTEGER, 
    duration REAL                       
);




