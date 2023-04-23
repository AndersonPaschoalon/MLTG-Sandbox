Sniffer

DONE (1) CLI
    Formato da CLI
    --type/-y    {live, pcap, nspcap}
    --src/-s     {file-name, ether name, ..}
    --timeout/-t {timeout in seconds, default -1}
    --maxpackets/-m {max number of packets to be captured, default }
    --lib/-l     {libpcap, dummy, sim}
    --name/-n    {nome da captura a ser salva na db}
    --show/-s    {imprime dados da TraceDatabase}
    --version/-v {imprime a versão}
    --help/-h   {manpage}

(2) Implementar o DriverCsv

DONE (3) Implementar suporte a interface live

DONE (4) Implementar suporte a arquivo pcap

(5) Implementar suporte a arquivo nspcap

(6) Implementar suporte a protocolos de link-layer como parametro de linha de comando
    --link ethernet|wifi|5g|zigbee...

[ok] (7) Reduzir printfs

[ok] (8) Ajustar nomeclatura, e adicionar parametro captureType 

https://tshark.dev/search/


