#include "NetTypes.h"


std::ostream& operator<<(std::ostream& os, const LinkProtocol& n)
{
    switch (n)
    {
        case LinkProtocol::NONE: os << "NONE"; break;
        case LinkProtocol::ETHERNET: os << "Ethernet"; break;
        case LinkProtocol::IEEE_802_11: os << "IEEE-802.11"; break;
        default: os.setstate(std::ios_base::failbit);
    }
    return os;
}


std::ostream& operator<<(std::ostream& os, const NetworkProtocol& n)
{
    switch (n)
    {
        case NetworkProtocol::NONE: os << "NONE"; break;
        case NetworkProtocol::IPv4: os << "IPv4"; break;
        case NetworkProtocol::IPv6: os << "IPv6"; break;
        case NetworkProtocol::ARP: os << "ARP"; break;
        case NetworkProtocol::RARP: os << "RARP"; break;
        case NetworkProtocol::LOOPBACK: os << "LOOPBACK"; break;
        case NetworkProtocol::WOL: os << "WOL"; break;
        case NetworkProtocol::ATA: os << "ATA"; break;
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
        case TransportProtocol::ICMP: os << "ICMP"; break;
        case TransportProtocol::ICMPv6: os << "ICMPv6"; break;
        case TransportProtocol::DCCP: os << "DCCP"; break;
        case TransportProtocol::SCTP: os << "SCTP"; break;
        case TransportProtocol::IGMP: os << "IGMP"; break;
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
        case ApplicationProtocol::DHCP: os << "DHCP"; break;
        case ApplicationProtocol::DNS: os << "DNS"; break;
        case ApplicationProtocol::FTP: os << "FTP"; break;
        case ApplicationProtocol::IMAP: os << "IMAP"; break;
        case ApplicationProtocol::HTTP: os << "HTTP"; break;
        case ApplicationProtocol::HTTPS: os << "HTTPS"; break;
        case ApplicationProtocol::MDNS: os << "MDNS"; break;
        case ApplicationProtocol::NTP: os << "NTP"; break;
        case ApplicationProtocol::POP3: os << "POP3"; break;
        case ApplicationProtocol::QUIC: os << "QUIC"; break;
        case ApplicationProtocol::RTP: os << "RTP"; break;
        case ApplicationProtocol::SSDP: os << "SSDP"; break; 
        case ApplicationProtocol::SIP: os << "SIP"; break;
        case ApplicationProtocol::SSH: os << "SSH"; break;
        case ApplicationProtocol::SNMP: os << "SNMP"; break;
        case ApplicationProtocol::SMTP: os << "SMTP"; break;
        case ApplicationProtocol::SMTPS: os << "SMTPS"; break;
        case ApplicationProtocol::Telnet: os << "Telnet"; break;
        case ApplicationProtocol::TFTP: os << "TFTP"; break;
        case ApplicationProtocol::TLS_SSL: os << "TLS_SSL"; break;

        default: os.setstate(std::ios_base::failbit);
    }
    return os;
}


std::string to_string(LinkProtocol protocol)
{
    switch (protocol)
    {
        case LinkProtocol::NONE:
            return "NONE";
        case LinkProtocol::ETHERNET:
            return PROTOCOL_ETHERNET;
        case LinkProtocol::IEEE_802_11:
            return PROTOCOL_IEEE_802_11;            
        default:
            return "UNKNOWN";
    }
}


std::string to_string(NetworkProtocol protocol)
{
    switch (protocol)
    {
        case NetworkProtocol::NONE:
            return "NONE";
        case NetworkProtocol::IPv4:
            return "IPv4";
        case NetworkProtocol::IPv6:
            return "IPv6";            
        case NetworkProtocol::ARP:
            return "ARP";
        case NetworkProtocol::RARP:
            return "RARP";
        case NetworkProtocol::LOOPBACK:
            return "LOOPBACK";
        case NetworkProtocol::WOL:
            return "WOL";
        case NetworkProtocol::ATA:
            return "ATA";
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
        case TransportProtocol::ICMP:
            return "ICMP";
        case TransportProtocol::ICMPv6:
            return "ICMPv6";
        case TransportProtocol::DCCP:
            return "DCCP";
        case TransportProtocol::SCTP:
            return "SCTP";
        case TransportProtocol::IGMP:
            return "IGMP";            
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
        case ApplicationProtocol::DHCP:
            return "DHCP";
        case ApplicationProtocol::DNS:
            return "DNS";
        case ApplicationProtocol::FTP:
            return "FTP";
        case ApplicationProtocol::IMAP:
            return "IMAP";
        case ApplicationProtocol::HTTP:
            return "HTTP";
        case ApplicationProtocol::HTTPS:
            return "HTTPS";
        case ApplicationProtocol::MDNS:
            return "MDNS";
        case ApplicationProtocol::NTP:
            return "NTP";
        case ApplicationProtocol::POP3:
            return "POP3";            
        case ApplicationProtocol::QUIC:
            return "QUIC";
        case ApplicationProtocol::RTP:
            return "RTP";
        case ApplicationProtocol::SSDP:
            return "SSDP";
        case ApplicationProtocol::SIP:
            return "SIP";
        case ApplicationProtocol::SSH:
            return "SSH";
        case ApplicationProtocol::SNMP:
            return "SNMP";
        case ApplicationProtocol::SMTP:
            return "SMTP";
        case ApplicationProtocol::SMTPS:
            return "SMTPS";
        case ApplicationProtocol::Telnet:
            return "Telnet";
        case ApplicationProtocol::TFTP:
            return "TFTP";
        case ApplicationProtocol::TLS_SSL:
            return "TLS/SSL";
        default:
            return "UNKNOWN";
    }
}


std::string hex_to_dotted_decimal(ipv4_address hexAddress)
{
    std::stringstream ss;
    ss << ((hexAddress >> 24) & 0xFF) << '.' << ((hexAddress >> 16) & 0xFF) << '.' << ((hexAddress >> 8) & 0xFF) << '.' << (hexAddress & 0xFF);
    return ss.str();
}


double inter_arrival(const timeval &t0, const timeval &t1)
{
    timeval deltaTime = delta(t0, t1);
    double deltaDouble = static_cast<double>(deltaTime.tv_sec) + static_cast<double>(deltaTime.tv_usec) / 1000000.0;
    return deltaDouble;
}


timeval delta(const timeval &t0, const timeval &t1)
{
    timeval pts;
    long int sec_diff = t1.tv_sec - t0.tv_sec;
    long int usec_diff = t1.tv_usec - t0.tv_usec;
    if (usec_diff < 0) {
        usec_diff += 1000000;
        sec_diff -= 1;
    }
    pts.tv_sec = sec_diff;
    pts.tv_usec = usec_diff;
    return pts;
}


/// @brief Compress the network protocols into a bitmap.
/// @param n Network protocol enum.
/// @param t Transport protocol enum.
/// @param a Application protocol enum.
/// @return The bitmap.
protocol_stack zip_stack(NetworkProtocol n, TransportProtocol t, ApplicationProtocol a)
{
    // protocol_stack stack = 0;
    // stack |= static_cast<protocol_stack>(n) << 8;
    // stack |= static_cast<protocol_stack>(t) << 4;
    // stack |= static_cast<protocol_stack>(a);
    // return stack;

    int nn = static_cast<int>(n);
    int tt = static_cast<int>(t);
    int aa = static_cast<int>(a);

    if (nn < 0 || nn > 255 || tt < 0 || tt > 255 || aa < 0 || aa > 255) 
    {
        // Error: protocol value out of range
        return -1; 
    }

    return (nn << 16) | (tt << 8) | aa;    
}


flow_hash zip_ports(port_number dst, port_number src)
{
    return PORT_OFFSET_VALUE*dst + src;
}


flow_hash zip_ipv4(ipv4_address dst, ipv4_address src)
{
    return IPV4_OFFSET_VALUE*dst + src;
}


size_t hash_strings(std::string a, std::string b)
{
    std::hash<std::string> hasher;
    std::string strToHash = a + b;
    size_t hash = hasher(strToHash);
    return hash;    
}


LinkProtocol to_link_protocol(const char *str)
{
    std::string linkProtocolStr = StringUtils::toLower(StringUtils::trimCopy(str).c_str());

    if(linkProtocolStr == PROTOCOL_ETHERNET)
    {
        return LinkProtocol::ETHERNET;
    }
    else if(linkProtocolStr == PROTOCOL_IEEE_802_11)
    {
        return LinkProtocol::IEEE_802_11;
    }

    return LinkProtocol::NONE;
}


void recover_ipv4(flow_hash summ, ipv4_address &dst, ipv4_address &src)
{
    flow_hash lsbValue = summ & IPV4_LSB_MASK;
    flow_hash msbValue = (summ & IPV4_MSB_MASK) >> 16*2;
    src = (ipv4_address)lsbValue;
    dst = (ipv4_address)msbValue;    
}


void recover_ports(flow_hash summ, port_number &dst, port_number &src)
{
    flow_hash lsbValue = summ & PORT_LSB_MASK;
    flow_hash msbValue = (summ & PORT_MSB_MASK) >> 16;
    src = (port_number)lsbValue;
    dst = (port_number)msbValue;    
}


ApplicationProtocol estimate_application_protocol_v01(TransportProtocol proto, uint16_t src_port, uint16_t dst_port)
{
    if (proto == TransportProtocol::TCP) // TCP
    {
        // Check for well-known TCP ports
        switch (src_port)
        {
            case 20:
            case 21:
                return ApplicationProtocol::FTP;
            case 22:
                return ApplicationProtocol::SSH;
            case 25:
                return ApplicationProtocol::SMTP;
            case 80:
                return ApplicationProtocol::HTTP;
            case 110:
                return ApplicationProtocol::POP3;
            case 143:
                return ApplicationProtocol::IMAP;
            case 443:
                return ApplicationProtocol::HTTPS;
            case 587:
                return ApplicationProtocol::SMTPS;
            default:
                break;
        }
        
        switch (dst_port)
        {
            case 20:
            case 21:
                return ApplicationProtocol::FTP;
            case 22:
                return ApplicationProtocol::SSH;
            case 25:
                return ApplicationProtocol::SMTP;
            case 80:
                return ApplicationProtocol::HTTP;
            case 110:
                return ApplicationProtocol::POP3;
            case 143:
                return ApplicationProtocol::IMAP;
            case 443:
                return ApplicationProtocol::HTTPS;
            case 587:
                return ApplicationProtocol::SMTPS;
            default:
                break;
        }

    }
    else if (proto == TransportProtocol::UDP) // UDP
    {
        // Check for well-known UDP ports
        switch (src_port)
        {
            case 53:
                return ApplicationProtocol::DNS;
            case 67:
            case 68:
                return ApplicationProtocol::DHCP;
            case 161:
                return ApplicationProtocol::SNMP;
            case 69:
                return ApplicationProtocol::TFTP;
            case 123:
                return ApplicationProtocol::NTP;    
            case 5060:
            case 5061:
                return ApplicationProtocol::SIP;
            case 443:
            case 80:
                return ApplicationProtocol::QUIC;
            case 5353:
                return ApplicationProtocol::MDNS;
            case 1900:
                return ApplicationProtocol::SSDP;      
            default:
                break;
        }

        switch (dst_port)
        {
            case 53:
                return ApplicationProtocol::DNS;
            case 67:
            case 68:
                return ApplicationProtocol::DHCP;
            case 161:
                return ApplicationProtocol::SNMP;
            case 69:
                return ApplicationProtocol::TFTP;
            case 123:
                return ApplicationProtocol::NTP;    
            case 5060:
            case 5061:
                return ApplicationProtocol::SIP;
            case 443:
            case 80:
                return ApplicationProtocol::QUIC;
            case 5353:
                return ApplicationProtocol::MDNS;
            case 1900:
                return ApplicationProtocol::SSDP;      
            default:
                break;
        }
    }
    
    return ApplicationProtocol::NONE;
}


ipv4_address pa_byte_to_int(const uint8_t arp_spa[4])
{
    unsigned int result = 0;
    for (int i = 0; i < 4; i++) {
        result <<= 8;  // shift left by 8 bits
        result |= arp_spa[i];  // bitwise OR with the next byte
    }
    return result;
}


void recover_ipv4_str(flow_hash summ, std::string& dst, std::string& src)
{
    ipv4_address val_dst = 0;
    ipv4_address val_src = 0;
    recover_ipv4(summ, val_dst, val_src);
    dst = hex_to_dotted_decimal(val_dst);
    src = hex_to_dotted_decimal(val_src);
}

/// @brief Returns the Network Protocol from the bitmap protocol stack.
/// @param stack Bitmap.
/// @return Network Protocol Enum.
NetworkProtocol to_network_protocol(protocol_stack stack)
{
    int n = (stack >> 16) & 0xFF;
    return static_cast<NetworkProtocol>(n);
    // return static_cast<NetworkProtocol>((stack >> 8) & 0x0F);
}


/// @brief Returns the Transport Protocol from the bitmap protocol stack.
/// @param stack Bitmap.
/// @return Transport Protocol Enum.
TransportProtocol to_transport_protocol(protocol_stack stack)
{
    int t = (stack >> 8) & 0xFF;
    return static_cast<TransportProtocol>(t);    
    // return static_cast<TransportProtocol>((stack >> 4) & 0x0F);
}


/// @brief Returns the Application Protocol from the bitmap protocol stack.
/// @param stack Bitmap.
/// @return Application Protocol Enum.
ApplicationProtocol to_application_protocol(protocol_stack stack)
{
    int a = stack & 0xFF;
    return static_cast<ApplicationProtocol>(a);
    // return static_cast<ApplicationProtocol>(stack & 0x0F);
}


