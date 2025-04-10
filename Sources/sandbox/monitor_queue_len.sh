#!/bin/bash

# === Help Menu ===
print_help() {
cat << EOF
Usage: $0 <switch_name> <port_number> <interval_sec> <duration_sec> <output_csv>

Monitors Open vSwitch port statistics to estimate queue behavior over time.

Arguments:
  switch_name     Name of the switch in Mininet (e.g., s1)
  port_number     Port number to monitor (usually 1 or 2)
  interval_sec    Sampling interval in seconds (e.g., 0.5)
  duration_sec    Total duration to run in seconds (e.g., 10)
  output_csv      Path to CSV file where output is saved

Example:
  $0 s1 2 0.5 10 queue_data.csv

Make sure you're running this script with sudo, and OVS is installed.
EOF
}

# === Check Arguments ===
if [ "$#" -ne 5 ]; then
    print_help
    exit 1
fi

SWITCH=$1
PORT=$2
INTERVAL=$3
DURATION=$4
OUTFILE=$5

# === Validate Dependencies ===
if ! command -v ovs-ofctl &> /dev/null; then
    echo "Error: ovs-ofctl is not installed or not in PATH."
    exit 2
fi

# === CSV Header ===
echo "timestamp,tx_packets,tx_bytes,tx_dropped" > "$OUTFILE"

# === Main Loop ===
END_TIME=$((SECONDS + DURATION))
while [ $SECONDS -lt $END_TIME ]; do
    TS=$(date +"%Y-%m-%d %H:%M:%S")

    # Extract port block for the specified port
    PORT_BLOCK=$(ovs-ofctl dump-ports "$SWITCH" | awk -v p="port $PORT:" '
        $0 ~ p {found=1; next}
        found && /^$/ {exit}
        found {print}
    ')

    TX_PKTS=$(echo "$PORT_BLOCK" | grep -oP 'tx pkts=\K[0-9]+')
    TX_BYTES=$(echo "$PORT_BLOCK" | grep -oP 'tx bytes=\K[0-9]+')
    TX_DROP=$(echo "$PORT_BLOCK" | grep -oP 'tx dropped=\K[0-9]+')

    echo "$TS,$TX_PKTS,$TX_BYTES,$TX_DROP" >> "$OUTFILE"

    sleep "$INTERVAL"
done

echo "Queue monitoring completed: $OUTFILE"

