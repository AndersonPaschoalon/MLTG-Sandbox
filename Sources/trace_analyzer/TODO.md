# Milestone \#0

## 1. Basic Performance Metrics
- [x] Throughput / Bandwidth (bps, Mbps)
- [x] Packet Rate (pps)
- [x] Packet size histogram
- [-] Packet Loss & Loss Rate
- [-] Latency (Min/Max/Avg)
- [-] Jitter (Latency Variation)
- [x] bandwidth cdf
- [x]packet size pdf

## 2. Burstiness & Temporal Analysis
- [x] Interarrival Mean (Violin/Boxplot)
- [x] Interarrival variance (Violin/Boxplot)
- [x] Interarrival CDF
- [x] Interarrival PDF
- [x] Burst Size Distribution (Duration and size of traffic bursts)
- [ ] Peak-to-Average Ratio
- [ ] Coefficient of Variation (CV) of interarrival times

## 3. Scaling & Self-Similarity Analysis
- [x] Hurst Exponent (H): Estimation via R/S analysis
- [x] Hurst Exponent (H): variance-time plot 
- [x] Hurst Exponent (H): Pediodogram 
- [ ] Hurst Exponent (H): wavelet-based methods
- [x] Wavelet Analysis (Use multiresolution analysis to detect scaling behavior: Plot energy vs. time-scale)
- [ ] Log-Log Plot of Variance (To analyze long-range dependence (LRD))
- [ ] Interarrival Time CDF (against best fit using bic?)

## 4. Sensitivity Analysis
- [-] Vary Load and Measure Impact: Throughput vs. packet rate
- [-] Vary Load and Measure Impact: Latency vs. queue size
- [-] Vary Load and Measure Impact: Loss vs. background traffic

## 5. Protocol & Flow-Level Behavior
- [x] Flow rate (flows per second)
- [ ] Flow Duration & Size Distributions
- [ ] Per-flow packet rate / burstiness
- [ ] Port & Protocol distribution

---

# Milestone \#1

## 1. Basic Performance Metrics
- [-] Packet Loss & Loss Rate
- [-] Latency (Min/Max/Avg)
- [-] Jitter (Latency Variation)

## 2. Burstiness & Temporal Analysis
- [ ] Peak-to-Average Ratio
- [ ] Coefficient of Variation (CV) of interarrival times

## 3. Scaling & Self-Similarity Analysis
- [ ] Log-Log Plot of Variance (To analyze long-range dependence (LRD))
- [ ] Interarrival Time CDF (against best fit using bic?)

## 4. Sensitivity Analysis
- [-] Vary Load and Measure Impact: Throughput vs. packet rate
- [-] Vary Load and Measure Impact: Latency vs. queue size
- [-] Vary Load and Measure Impact: Loss vs. background traffic

## 5. Protocol & Flow-Level Behavior
- [ ] Flow Duration & Size Distributions
- [ ] Per-flow packet rate / burstiness
- [ ] Port & Protocol distribution