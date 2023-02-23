#include "NetTypes.h"

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
