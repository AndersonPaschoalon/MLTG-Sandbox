#!/bin/bash
# Run this on client machine

# Show help if needed
if [ "$1" = "--help" ] || [ $# -eq 0 ]; then
  echo "Usage: $0 <server_ip> <duration_sec> [output.csv]"
  echo "Example: $0 192.168.1.100 10 results.csv"
  exit 0
fi

SERVER_IP=$1
DURATION=$2
OUTPUT_CSV=${3:-"jitter_results.csv"}
OUTPUT_JSON="${OUTPUT_CSV%.*}.json"

# Run test (reverse mode for receiver-side jitter)
echo "Measuring jitter for ${DURATION}s..."
iperf3 -c $SERVER_IP -t $DURATION -u -R -J > "$OUTPUT_JSON"

# Extract key metrics
jitter=$(jq -r '.end.sum.jitter_ms' "$OUTPUT_JSON")
lost=$(jq -r '.end.sum.lost_packets' "$OUTPUT_JSON")
total=$(jq -r '.end.sum.packets' "$OUTPUT_JSON")
loss_pct=$(echo "scale=2; $lost/$total*100" | bc)

# Save CSV
echo "timestamp,jitter_ms,packets_lost,packets_total,loss_percent" > "$OUTPUT_CSV"
echo "$(date +'%F %T'),$jitter,$lost,$total,$loss_pct" >> "$OUTPUT_CSV"

echo "Test complete!"
echo "Jitter: ${jitter}ms, Loss: ${lost}/${total} (${loss_pct}%)"
echo "Files saved:"
echo "- ${OUTPUT_JSON}"
echo "- ${OUTPUT_CSV}"