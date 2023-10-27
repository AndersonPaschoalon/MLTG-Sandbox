#!/bin/bash

# Default values
PCAP_NAME=""
ETHERNET=""
START_DELAY=0
CAPTURE_TIME=""

# Function to display help
function display_help {
    echo "Usage: tcpdump-capture.sh [options]"
    echo "Options:"
    echo "  --pcap-name     Specify the name of the pcap file (required)"
    echo "  --ether         Specify the Ethernet interface to capture (required)"
    echo "  --start-delay   Specify the start delay in seconds (default is 0)"
    echo "  --capture-time  Specify the capture time in seconds (default is unlimited)"
    echo "  --help          Display this help menu"
    echo ""
    echo "Example:"
    echo "    This will capture packets on the eth0 interface for 3600 seconds (1 hour) after a 5-second delay and save "
    echo "    them to mycapture.pcap."
    echo "./tcpdump-capture.sh --pcap-name mycapture.pcap --ether eth0 --start-delay 5 --capture-time 3600"
}

# Parse command line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        --pcap-name)
            PCAP_NAME="$2"
            shift 2
            ;;
        --ether)
            ETHERNET="$2"
            shift 2
            ;;
        --start-delay)
            START_DELAY="$2"
            shift 2
            ;;
        --capture-time)
            CAPTURE_TIME="$2"
            shift 2
            ;;
        --help)
            display_help
            exit 0
            ;;
        *)
            echo "Error: Unknown option '$1'"
            display_help
            exit 1
            ;;
    esac
done

# Check for required options
if [ -z "$PCAP_NAME" ] || [ -z "$ETHERNET" ]; then
    echo "Error: Both --pcap-name and --ether options are required."
    display_help
    exit 1
fi

# Wait for the start delay, if specified
if [ "$START_DELAY" -gt 0 ]; then
    echo "Waiting for $START_DELAY seconds before starting capture..."
    sleep "$START_DELAY"
fi

# Start tcpdump to capture packets
echo "Starting packet capture on interface $ETHERNET..."
if [ -n "$CAPTURE_TIME" ]; then
    tcpdump -i "$ETHERNET" -w "$PCAP_NAME" -G "$CAPTURE_TIME"
else
    tcpdump -i "$ETHERNET" -w "$PCAP_NAME"
fi

echo "Packet capture complete. Saved as $PCAP_NAME"
