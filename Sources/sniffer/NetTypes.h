#ifndef _NET_TYPES__H_ 
#define _NET_TYPES__H_ 1

#include <string>
#include <sstream>
#include <iomanip>

///////////////////////////////////////////////////////////////////////////////
// CONSTANTS
///////////////////////////////////////////////////////////////////////////////


#define MAX_PORT_VALUE       0xFFFF
#define PORT_OFFSET_VALUE    0x10000
#define PORT_NONE            0x0
#define PORT_LSB_MASK        0xFFFF
#define PORT_MSB_MASK        0xFFFF0000

#define MAX_IPV4_VALUE       0xFFFFFFFF
#define IPV4_OFFSET_VALUE    0x100000000
#define IPV4_NONE            0x0
#define IPV6_NONE            ""
#define IPV4_LSB_MASK        0xFFFFFFFF
#define IPV4_MSB_MASK        0xFFFFFFFF00000000

#define FLOW_ID_NONE         0


///////////////////////////////////////////////////////////////////////////////
// DATA TYPES
///////////////////////////////////////////////////////////////////////////////

typedef long int           ts_sec;
typedef long int           ts_usec;
// typedef double             time_stamp;
typedef unsigned int       packet_size;
typedef unsigned short     ttl;
typedef unsigned short     port_number; 
typedef unsigned int       ipv4_address;
typedef size_t             flow_id;
typedef unsigned long int  flow_hash;
typedef unsigned short     protocol_stack; 

typedef struct packet_time_stamp_struct{
    ts_sec sec;
    ts_usec usec;
}PacketTimeStamp;

std::string hexToDottedDecimal(ipv4_address hexAddress);

double interArrival(const PacketTimeStamp& t0, const PacketTimeStamp& t1);

PacketTimeStamp delta(const PacketTimeStamp& t0, const PacketTimeStamp& t1);




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


std::ostream& operator<<(std::ostream& os, const NetworkProtocol& n);
std::ostream& operator<<(std::ostream& os, const TransportProtocol& n);
std::ostream& operator<<(std::ostream& os, const ApplicationProtocol& n);

std::string to_string(NetworkProtocol protocol);
std::string to_string(TransportProtocol protocol);
std::string to_string(ApplicationProtocol protocol);

/// @brief Compress the network protocols into a bitmap.
/// @param n Network protocol enum.
/// @param t Transport protocol enum.
/// @param a Application protocol enum.
/// @return The bitmap.
protocol_stack zip_stack(NetworkProtocol n, TransportProtocol t, ApplicationProtocol a);

/// @brief Compress two port numbers into a unsigned long
/// @param dst 
/// @param src 
/// @return 
flow_hash zip_ports(port_number dst, port_number src);

/// @brief Compress two IPV4 adresses into a unsigned long.
/// @param dst 
/// @param src 
/// @return 
flow_hash zip_ipv4(ipv4_address dst, ipv4_address src);


/// @brief Returns the Network Protocol from the bitmap protocol stack.
/// @param stack Bitmap.
/// @return Network Protocol Enum.
NetworkProtocol to_network_protocol(protocol_stack stack);

/// @brief Returns the Transport Protocol from the bitmap protocol stack.
/// @param stack Bitmap.
/// @return Transport Protocol Enum.
TransportProtocol to_transport_protocol(protocol_stack stack);

/// @brief Returns the Application Protocol from the bitmap protocol stack.
/// @param stack Bitmap.
/// @return Application Protocol Enum.
ApplicationProtocol to_application_protocol(protocol_stack stack);



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
};




#endif // _NET_TYPES__H_