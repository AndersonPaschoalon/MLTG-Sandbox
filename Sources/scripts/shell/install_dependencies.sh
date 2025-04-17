#!/bin/bash
# Script to install the system dependencies. 


sudo apt update

echo ==========================================================================
echo == testbed
echo ==========================================================================
sudo apt-get install openvswitch-testcontroller
sudo apt-get install mininet
sudo apt install xterm
sudo apt install nfdump
sudo apt install  tshark
sudo apt install jq
