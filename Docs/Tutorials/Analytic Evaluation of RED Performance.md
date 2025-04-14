# 📄 "Analytic Evaluation of RED Performance"

-   Authors: Jean-Yves Le Boudec and Patrick Thiran​
-   Access: Available on ResearchGate​


# 🔍 Key Insights

This paper provides an in-depth analytical comparison between Random Early Detection (RED) and Tail Drop queue management strategies under varying traffic conditions, including bursty and self-similar traffic patterns.​

Main findings include:

-   RED vs. Tail Drop: RED is more effective in mitigating the negative effects of bursty traffic compared to Tail Drop, leading to reduced packet loss and improved queue stability.​
    ResearchGate+3ResearchGate+3arXiv+3

-   Impact of Bursty Traffic: The study demonstrates that bursty traffic significantly increases the likelihood of packet loss and queue overflows, particularly under Tail Drop mechanisms.​

-   Queue Behavior Analysis: Through analytical modeling, the paper illustrates how different queue management strategies respond to varying traffic burstiness levels, providing insights into optimal configurations for minimizing jitter and maintaining QoS.​


# 🧪 Applying the Insights in Mininet

To replicate and study these effects within your Mininet environment:​

1.  Implement RED Queue Management:
    - Configure RED on your virtual switches using tc (traffic control) in Linux.​
    Example command:
    ```
    sudo tc qdisc add dev s1-eth1 root red limit 100000 min 30000 max 60000 avpkt 1000 burst 20 bandwidth 10mbit probability 0.02
    ```

2.  Generate Bursty Traffic:
    Utilize traffic generation tools like iperf3 to create controlled bursty traffic patterns between hosts.​
    Example:
    ```
    iperf3 -c <server_ip> -u -b 10M -t 60 -i 1
    ```

3.  Monitor Queue Length and Jitter:
    Use tc to monitor queue statistics:​
    ```
    tc -s qdisc show dev s1-eth1
    ```
    Capture and analyze jitter using iperf3's UDP mode with JSON output for detailed metrics.​

4.  Data Analysis:
    Collect and analyze the data to observe the effects of bursty traffic on queue lengths and jitter under different queue management strategies.​








