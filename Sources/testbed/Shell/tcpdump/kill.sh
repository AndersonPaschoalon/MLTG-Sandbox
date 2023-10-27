#!/bin/bash

# Kill any running instances of tcpdump
pkill tcpdump

# Check if any instances were killed
if [ $? -eq 0 ]; then
    echo "Killed all running instances of tcpdump."
else
    echo "No instances of tcpdump were found."
fi
