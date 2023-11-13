aptitude search mininet
sudo apt-get install openvswitch-testcontroller

# para rodar o controller
sudo ovs-testcontroller tcp:127.0.0.1:6653

# parsear pcaps
pip install scapy

# Tipos de experimentos Propostos

a configuração basica será a seguinte:

(h1)---+   +----(h3)
       (sw0)
(h2)---+   +----(h4)

O Client deve estar localizado em h1 e o server em h3.

É possivel se mensurar:
- O Trafego gerado em h1
- O Tráfego recebido em h3
- Parametros da rede entre h1 e h3, simulando que o trafego entre h1 e h3 se trata de um trafego de background.





