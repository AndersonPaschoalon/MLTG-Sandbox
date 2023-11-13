import subprocess
import re
import argparse
import time


def measure_ping_stats(destination, interval, duration, output_file):
    command = f'ping -i {interval} -w {duration} {destination}'
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    rtt_values = []
    loss_count = 0

    while process.poll() is None:
        line = process.stdout.readline().decode('utf-8').strip()

        # Parse round-trip time and loss from the output
        match_rtt = re.search(r'time=([\d.]+) ms', line)
        match_loss = re.search(r'(\d+)% packet loss', line)

        if match_rtt:
            rtt_values.append(float(match_rtt.group(1)))
        elif match_loss:
            loss_count = int(match_loss.group(1))

    if rtt_values:
        jitter = max(rtt_values) - min(rtt_values)
        avg_rtt = sum(rtt_values) / len(rtt_values)
        with open(output_file, 'a') as file:
            file.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")},{avg_rtt},{loss_count}%,{jitter:.2f}\n')
        print(f'Round-Trip Time (avg): {avg_rtt:.2f} ms')
        print(f'Packet Loss: {loss_count}%')
        print(f'Jitter: {jitter:.2f} ms')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Measure ping statistics including RTT, loss, and jitter.')
    parser.add_argument('destination', help='Destination host or IP address')
    parser.add_argument('--interval', type=int, default=1, help='Ping interval in seconds (default: 1)')
    parser.add_argument('--duration', type=int, default=60, help='Ping duration in seconds (default: 60)')
    parser.add_argument('--output-file', default='ping_stats.csv', help='Output file for ping statistics (default: ping_stats.csv)')
    args = parser.parse_args()
    # python ping_measure.py <destination> --interval <interval> --duration <duration> --output-file <output_file>
    measure_ping_stats(args.destination, args.interval, args.duration, args.output_file)
