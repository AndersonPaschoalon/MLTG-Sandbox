from NetQA.NetQA import NetQA
from mininet.node import Host, Switch


class PingMeasurer(NetQA):

    def __init__(self, destination, interval, duration, output_file):
        super().__init__(destination, interval, duration, output_file)

    def start(self, host):
        command = f"python3 ping-measurer.py {self.destination} --interval {self.interval} --duration {self.duration} --output-file {self.output_file}"
        print(command)
        self.proc = host.popen(command)

    def stop(self):
        self.proc.terminate()


