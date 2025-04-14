#!/bin/bash

# === Check arguments ===
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <destination_ip> <output_csv_file> <duration_seconds>"
    exit 1
fi

DEST_IP=$1
OUTPUT_FILE=$2
DURATION=$3

# === Create CSV Header ===
echo "timestamp,sent_time_seconds,jitter_ms" > "$OUTPUT_FILE"

# === Run iperf3 and collect JSON output ===
iperf3 -u -c "$DEST_IP" -t "$DURATION" -i 0.1 --json > temp_iperf_output.json

# === Parse JSON and write to CSV ===
jq -r '.intervals[] | [.sum.start, .sum.jitter_ms] | @csv' temp_iperf_output.json | \
while IFS=, read -r start jitter; do
    ts=$(date +"%Y-%m-%d %H:%M:%S")
    echo "$ts,$start,$jitter" >> "$OUTPUT_FILE"
done

# === Clean up ===
rm -f temp_iperf_output.json

echo "Jitter data saved to $OUTPUT_FILE"


