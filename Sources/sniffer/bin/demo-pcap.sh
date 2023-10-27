#!/bin/bash

./sniffer.exe --name TestSkype --type pcap --device ../../../Pcap/SkypeIRC.cap.pcap --driver libpcap --link ethernet
./sniffer.exe --name TestLandiurnal3 --type pcap --device ../../../../Pcaps/lanDiurnal.pcap  --driver libpcap --link ethernet
