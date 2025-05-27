## ✅ **Packet-Level Metrics**

### **1.a. Byte/Packet Throughput → Bandwidth**

* **Description**: Line plot showing bytes transferred per unit time (e.g., Mbps).
* **How to analyze**:

  * Check for consistent throughput patterns.
  * Look for bursts or gaps.
* **Key insight**: Validate if generated traffic matches expected load profiles.

---

### **1.a. Byte/Packet Throughput → Packet per second**

* **Description**: Line plot showing number of packets sent per second.
* **How to analyze**:

  * Inspect for uniformity or burstiness in packet rates.
  * Compare against ground-truth or target traffic patterns.
* **Key insight**: Detect packet-level pacing accuracy.

---

### **1.c. Inter Packet Time Distributions → Violin interarrival plot**

* **Description**: Violin plot showing the distribution of inter-packet times, with density and quantiles.
* **How to analyze**:

  * Look at spread and central tendency.
  * Check for multimodal behavior (e.g., multiple traffic phases).
* **Key insight**: Reveals variability and possible anomalies in packet timing.

---

### **1.b. Packet Size Distributions → Violin packet size plot**

* **Description**: Violin plot of packet size distribution.
* **How to analyze**:

  * Identify typical packet sizes (e.g., 64B, 1500B).
  * Look for unexpected modes or excessive variability.
* **Key insight**: Validate that size distributions align with real traffic traces.

---

### **1.c. Inter Packet Time Distributions → Box-plot of interarrival**

* **Description**: Box plot showing median, quartiles, and outliers of inter-packet times.
* **How to analyze**:

  * Spot extreme delays or tight clustering.
  * Compare interquartile range to target specs.
* **Key insight**: Simple summary of packet timing dispersion.

---

### **1.b. Packet Size Distributions → Box-plot of packet sizes**

* **Description**: Box plot for packet sizes.
* **How to analyze**:

  * Check for expected packet size ranges.
  * Detect heavy use of small or jumbo frames.
* **Key insight**: Basic compliance check of traffic generation.

---

### **1.c. Inter Packet Time Distributions → Interarrival PDF**

* **Description**: Probability density function of interarrival times.
* **How to analyze**:

  * Check shape (e.g., exponential, heavy-tailed).
  * Compare empirical PDF to theoretical distribution.
* **Key insight**: Reveals underlying arrival process assumptions.

---

### **1.c. Inter Packet Time Distributions → Interarrival by arrival**

* **Description**: Scatter plot of interarrival time vs. arrival time.
* **How to analyze**:

  * Look for temporal drift or trends in interarrival patterns.
  * Detect phases of different traffic intensities.
* **Key insight**: Captures temporal evolution of packet spacing.

---

### **1.a. Byte/Packet Throughput → Bandwidth**

(Same as first.)

---

### **1.a. Byte/Packet Throughput → Packet per second**

(Same as above.)

---

### **1.b. Packet Size Distributions → Packet size histogram**

* **Description**: Histogram showing frequency of packet sizes.
* **How to analyze**:

  * Identify dominant packet size modes.
  * Look for tail behavior indicating unusual packet lengths.
* **Key insight**: Direct view of generated packet size profile.

---

## ✅ **Burstiness and Temporal Structure**

### **2.a. Interarrival Time CDF → Interarrival CDF**

* **Description**: Cumulative distribution function of interarrival times.
* **How to analyze**:

  * Check for percentile-based thresholds.
  * Compare to real traffic CDFs to validate similarity.
* **Key insight**: Understand cumulative likelihood of interarrival intervals.

---

### **2.a. Interarrival Time CDF → Bandwidth CDF**

* **Description**: CDF of bandwidth measurements over time windows.
* **How to analyze**:

  * Assess how often certain bandwidth levels are exceeded.
  * Compare distributional shape to real traces.
* **Key insight**: Understand traffic load variability and extremes.

---

### **2.a. Interarrival Time CDF → Payload size CDF**

* **Description**: CDF of packet payload sizes.
* **How to analyze**:

  * Validate alignment with expected protocol/application payloads.
  * Look for unexpected bulk transfers or tiny payloads.
* **Key insight**: Ensures realistic payload generation.

---

### **2.a. Interarrival Time CDF → Packet load CDF**

* **Description**: CDF of packet counts in defined time intervals.
* **How to analyze**:

  * Assess load stability and burstiness.
  * Detect sustained high-packet periods.
* **Key insight**: Evaluates the intensity of generated traffic over time.

---

### **2.a. Interarrival Time CDF → Burst duration violin plot**

* **Description**: Violin plot of durations of detected traffic bursts.
* **How to analyze**:

  * Look for typical burst lengths.
  * Assess spread and presence of extreme-duration bursts.
* **Key insight**: Validates temporal burstiness structure.

---

## ✅ **Flow/Protocol-Level Metrics**

### **3.a. Flow distributions → Flow per second**

* **Description**: Line plot showing number of flows initiated per second.
* **How to analyze**:

  * Check for stability or diurnal patterns in flow starts.
  * Compare to real traffic for flow initiation rates.
* **Key insight**: Validates that generated flow-level behavior is realistic.

---

## ✅ **Summary table**

| **Validation Metric**    | **Plot**                  | **Key Insight**                      |
| ------------------------ | ------------------------- | ------------------------------------ |
| Byte/Packet Throughput   | Bandwidth, PPS            | Load generation fidelity             |
| Packet Size Distribution | Violin, Box, Histogram    | Packet content realism               |
| Inter Packet Times       | Violin, Box, PDF, Scatter | Temporal precision                   |
| Interarrival Time CDF    | CDF plots                 | Burstiness and delay characteristics |
| Payload CDF              | CDF                       | Application-level realism            |
| Flow distributions       | Flow per sec              | Session-level generation fidelity    |
| Burst durations          | Violin                    | Burst structure correctness          |

---

