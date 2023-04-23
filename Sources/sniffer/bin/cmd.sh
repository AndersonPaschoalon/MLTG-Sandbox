#!/bin/bash
./sniffer.exe --name TestSkype --type pcap --device ../../../Pcap/SkypeIRC.cap.pcap --driver libpcap --link ethernet 
./sniffer.exe --name TestLandiurnal3 --type pcap --device ../../../../../Pcaps/Pcaps/lanDiurnal.pcap  --driver libpcap --link ethernet
sudo ./demo-sniffer.exe --name testEth0_03 --type live --device eth0 --driver libpcap --link ethernet


