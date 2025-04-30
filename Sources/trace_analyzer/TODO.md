# 1. Basic Performance Metrics
- [ ] Throughput / Bandwidth (bps, Mbps)
- [ ] Packet Rate (pps)
- [ ] Packet Loss & Loss Rate
- [ ] Latency (Min/Max/Avg)
- [ ] Jitter (Latency Variation)

# 2. Burstiness & Temporal Analysis
- [ ] Interarrival Mean
- [ ] Interarrival variance
- [ ] Interarrival CDF
- [ ] Burst Size Distribution (Duration and size of traffic bursts)
- [ ] Peak-to-Average Ratio
- [ ] Coefficient of Variation (CV) of interarrival times

# 3. Scaling & Self-Similarity Analysis
- [ ] Hurst Exponent (H): Estimation via R/S analysis
- [ ] Hurst Exponent (H): variance-time plot 
- [ ] Hurst Exponent (H): wavelet-based methods
- [ ] Wavelet Analysis (Use multiresolution analysis to detect scaling behavior: Plot energy vs. time-scale)
- [ ] Log-Log Plot of Variance (To analyze long-range dependence (LRD))
- [ ] Interarrival Time CDF (against best fit using bic?)

# 4. Sensitivity Analysis
- [ ] Vary Load and Measure Impact: Throughput vs. packet rate
- [ ] Vary Load and Measure Impact: Latency vs. queue size
- [ ] Vary Load and Measure Impact: Loss vs. background traffic

# 5. Protocol & Flow-Level Behavior
- [ ] Flow Duration & Size Distributions
- [ ] Per-flow packet rate / burstiness
- [ ] Port & Protocol distribution