///////////////////////////////////////////////////////////////////////////////
// CONSTANTS
///////////////////////////////////////////////////////////////////////////////


#define MAX_PORT_VALUE       0xFFFF
#define PORT_OFFSET_VALUE    0x10000
#define PORT_NONE            0x0

#define MAX_IPV4_VALUE       0xFFFFFFFF
#define IPV4_OFFSET_VALUE    0x100000000
#define IPV4_NONE            0x0

///////////////////////////////////////////////////////////////////////////////
// Protocols
///////////////////////////////////////////////////////////////////////////////

enum class NetworkProtocol
{   
    NONE,
    ARP,
    ICMP,
    ICMPv6,
    IPv4,
    IPv6,
    RIPv1,
    RIPv2,
};

enum class TransportProtocol
{
    NONE,
    TCP,
    UDP,
    DCCP,
    SCTP
};

enum class ApplicationProtocol
{
    NONE,
    BGP,
    DNS,
    FTP,
    HTTP,
    HTTPS,
    SSH,
    SMTP,
    Telnet,
    TLS_SSL,
};


///////////////////////////////////////////////////////////////////////////////
// DATA TYPES
///////////////////////////////////////////////////////////////////////////////

typedef double             time_stamp;
typedef unsigned int       packet_size;
typedef unsigned short     ttl;
typedef unsigned short     port_number; 
typedef unsigned int       ipv4_address;
typedef unsigned long long flow_id;


///////////////////////////////////////////////////////////////////////////////
// METADATA
///////////////////////////////////////////////////////////////////////////////

enum class TraceType
{
    LIVE,
    FILE
};

enum class CaptureLibrary
{
    LIBPACKP,
    DPDK,
    LIBTINS,
}