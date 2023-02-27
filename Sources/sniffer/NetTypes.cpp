#include "NetTypes.h"

std::ostream& operator<<(std::ostream& os, const NetworkProtocol& n)
{
    switch (n)
    {
        case NetworkProtocol::NONE: os << "NONE"; break;
        case NetworkProtocol::ARP: os << "ARP"; break;
        case NetworkProtocol::ICMP: os << "ICMP"; break;
        case NetworkProtocol::ICMPv6: os << "ICMPv6"; break;
        case NetworkProtocol::IPv4: os << "IPv4"; break;
        case NetworkProtocol::IPv6: os << "IPv6"; break;
        case NetworkProtocol::RIPv1: os << "RIPv1"; break;
        case NetworkProtocol::RIPv2: os << "RIPv2"; break;
        default: os.setstate(std::ios_base::failbit);
    }
    return os;
}

std::ostream& operator<<(std::ostream& os, const TransportProtocol& n)
{
    switch (n)
    {
        case TransportProtocol::NONE: os << "NONE"; break;
        case TransportProtocol::TCP: os << "TCP"; break;
        case TransportProtocol::UDP: os << "UDP"; break;
        case TransportProtocol::DCCP: os << "DCCP"; break;
        case TransportProtocol::SCTP: os << "SCTP"; break;
        
        default: os.setstate(std::ios_base::failbit);
    }
    return os;
}

std::ostream& operator<<(std::ostream& os, const ApplicationProtocol& n)
{
    switch (n)
    {
        case ApplicationProtocol::NONE: os << "NONE"; break;
        case ApplicationProtocol::BGP: os << "BGP"; break;
        case ApplicationProtocol::DNS: os << "DNS"; break;
        case ApplicationProtocol::FTP: os << "FTP"; break;
        case ApplicationProtocol::HTTP: os << "HTTP"; break;
        case ApplicationProtocol::HTTPS: os << "HTTPS"; break;            
        case ApplicationProtocol::SSH: os << "SSH"; break;    
        case ApplicationProtocol::SMTP: os << "SMTP"; break;
        case ApplicationProtocol::Telnet: os << "Telnet"; break;            
        case ApplicationProtocol::TLS_SSL: os << "TLS_SSL"; break;           
        default: os.setstate(std::ios_base::failbit);
    }
    return os;
}


std::string to_string(NetworkProtocol protocol)
{
    switch (protocol)
    {
        case NetworkProtocol::NONE:
            return "NONE";
        case NetworkProtocol::ARP:
            return "ARP";
        case NetworkProtocol::ICMP:
            return "ICMP";
        case NetworkProtocol::ICMPv6:
            return "ICMPv6";
        case NetworkProtocol::IPv4:
            return "IPv4";
        case NetworkProtocol::IPv6:
            return "IPv6";
        case NetworkProtocol::RIPv1:
            return "RIPv1";
        case NetworkProtocol::RIPv2:
            return "RIPv2";
        default:
            return "UNKNOWN";
    }
}

std::string to_string(TransportProtocol protocol)
{
    switch (protocol)
    {
        case TransportProtocol::NONE:
            return "NONE";
        case TransportProtocol::TCP:
            return "TCP";
        case TransportProtocol::UDP:
            return "UDP";
        case TransportProtocol::DCCP:
            return "DCCP";
        case TransportProtocol::SCTP:
            return "SCTP";
        default:
            return "UNKNOWN";
    }
}

std::string to_string(ApplicationProtocol protocol)
{
    switch (protocol)
    {
        case ApplicationProtocol::NONE:
            return "NONE";
        case ApplicationProtocol::BGP:
            return "BGP";
        case ApplicationProtocol::DNS:
            return "DNS";
        case ApplicationProtocol::FTP:
            return "FTP";
        case ApplicationProtocol::HTTP:
            return "HTTP";
        case ApplicationProtocol::HTTPS:
            return "HTTPS";
        case ApplicationProtocol::SSH:
            return "SSH";
        case ApplicationProtocol::SMTP:
            return "SMTP";
        case ApplicationProtocol::Telnet:
            return "Telnet";
        case ApplicationProtocol::TLS_SSL:
            return "TLS/SSL";
        default:
            return "UNKNOWN";
    }
}

std::string hexToDottedDecimal(ipv4_address hexAddress)
{
    std::stringstream ss;
    ss << ((hexAddress >> 24) & 0xFF) << '.' << ((hexAddress >> 16) & 0xFF) << '.' << ((hexAddress >> 8) & 0xFF) << '.' << (hexAddress & 0xFF);
    return ss.str();
}


/// @brief Compress the network protocols into a bitmap.
/// @param n Network protocol enum.
/// @param t Transport protocol enum.
/// @param a Application protocol enum.
/// @return The bitmap.
protocol_stack zip_stack(NetworkProtocol n, TransportProtocol t, ApplicationProtocol a)
{
    protocol_stack stack = 0;
    stack |= static_cast<protocol_stack>(n) << 8;
    stack |= static_cast<protocol_stack>(t) << 4;
    stack |= static_cast<protocol_stack>(a);
    return stack;
}

/// @brief Returns the Network Protocol from the bitmap protocol stack.
/// @param stack Bitmap.
/// @return Network Protocol Enum.
NetworkProtocol to_network_protocol(protocol_stack stack)
{
    return static_cast<NetworkProtocol>((stack >> 8) & 0x0F);
}

/// @brief Returns the Transport Protocol from the bitmap protocol stack.
/// @param stack Bitmap.
/// @return Transport Protocol Enum.
TransportProtocol to_transport_protocol(protocol_stack stack)
{
    return static_cast<TransportProtocol>((stack >> 4) & 0x0F);
}

/// @brief Returns the Application Protocol from the bitmap protocol stack.
/// @param stack Bitmap.
/// @return Application Protocol Enum.
ApplicationProtocol to_application_protocol(protocol_stack stack)
{
    return static_cast<ApplicationProtocol>(stack & 0x0F);
}


/*

int main()
{
    // create a protocol stack bitmap
    protocol_stack stack = zip_stack(NetworkProtocol::IPv4, TransportProtocol::TCP, ApplicationProtocol::HTTPS);

    // extract the individual protocols
    NetworkProtocol n = to_network_protocol(stack);
    TransportProtocol t = to_transport_protocol(stack);
    ApplicationProtocol a = to_application_protocol(stack);

    // print the protocols
    std::cout << "Network protocol: " << n << std::endl;
    std::cout << "Transport protocol: " << t << std::endl;
    std::cout << "Application protocol: " << a << std::endl;

    return 0;
}
Output:
Network protocol: IPv4
Transport protocol: TCP
Application protocol: HTTPS

**/