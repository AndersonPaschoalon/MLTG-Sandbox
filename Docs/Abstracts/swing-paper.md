# Swing: Realistic and Responsive Network Traffic Generation

## **Abstract — Setting the Stage for Realistic Traffic Generation**

In the world of network research, generating synthetic traffic that mimics the complexities of real-world network behavior is a longstanding challenge. Enter **Swing**, a closed-loop, network-responsive traffic generator designed to capture both the **statistical structure** and **dynamic responsiveness** of real network applications. Unlike previous approaches, Swing doesn’t just generate average bandwidth—it faithfully reproduces **burstiness across multiple timescales**, capturing intricate patterns often overlooked. By analyzing traffic from a single observation point, Swing automatically extracts statistical models that encapsulate user behavior, application properties, and network dynamics. These models then drive the generation of live traffic within a network emulation environment, interacting with real protocol stacks. Through a comprehensive validation, the authors demonstrate Swing’s remarkable ability to reproduce not only aggregate metrics but also subtle bursty behaviors. Furthermore, they explore how varying model parameters can project traffic characteristics into hypothetical future scenarios—a first step towards predictive traffic modeling.

---

## **I. Introduction — Why Realistic Traffic Generation Matters**

The introduction sets the tone by underscoring the critical role of **realistic traffic generation** across a multitude of domains—from **capacity planning** and **router design** to **security studies** and **emulation-based testing**. The authors define traffic generation not as a simplistic packet spitting mechanism but as a sophisticated process that should accurately reflect key traffic features: **packet arrival rates**, **burstiness**, **flow structures**, and **packet size distributions**.

Two fundamental challenges are framed:

1. **Designing a Semantically Meaningful Model**
   The model must employ parameters that are intuitive, easy to interpret, and directly connected to application or network behaviors. This enables flexible adaptation to various **application mixes**—illustrated through longitudinal changes in protocol prevalence (e.g., HTTP, NAPSTER, SMTP) observed in real traffic datasets.

2. **Automating Model Extraction from Traces**
   To ensure realism, the model must be **populated from real traces**. This step is crucial for ensuring that the generated traffic reproduces the **essential statistical features** of the original. Alternatively, it should also support synthetic "first principles" modeling for exploring hypothetical scenarios.

With these challenges in mind, the authors introduce **Swing**, a system designed to fulfill these goals. Swing’s **primary contribution** is its ability to match **traffic burstiness** at various temporal granularities—ranging from microsecond-scale inter-arrivals to traffic behaviors unfolding over several minutes. Notably, it achieves this fidelity for both **bytes and packets**, in **both traffic directions**, and for **multiple application protocols**—a breadth not commonly achieved in prior work.

A key insight emerges: to reproduce burstiness accurately, it is **not sufficient** to model packet arrivals in isolation. Instead, one must reconstruct the **prevailing network conditions**, particularly those that impact end-host behaviors such as **Round-Trip Time (RTT)**. The authors delve into the complexities of inferring such conditions from passive traces and highlight how these inferred parameters influence the fidelity of the generated traffic.

Finally, the introduction emphasizes Swing’s **responsiveness**—since it operates using **real TCP sessions**, the traffic generation dynamically adapts to changing network states, reflecting a realism that static trace replay cannot achieve.


Here’s the blog-style but scientifically accurate and precise synthesis for **Section II - The Swing Approach** of the **Swing** paper:

---

## **II. The Swing Approach — Modeling Traffic Beyond Simple Replay**

### **A. Defining Requirements: Realism, Responsiveness, and Randomness**

The authors begin by clearly articulating the **requirements** that shape Swing’s design: the synthetic traces must be **realistic**, **responsive**, and **maximally random**. These are not abstract goals, but directly tied to how synthetic traces are used in network research:

1. **Realism**:
   The generated traffic must accurately reproduce key statistical features from original traces. Specifically:

   * **Packet inter-arrival rates and burstiness** across multiple timescales.
   * **Packet size distributions**.
   * **Flow-level characteristics**, such as arrival rates and flow lengths.
   * (Though out of scope for this paper: **destination IP/port distributions**.)

   The rationale is that depending on the research application—whether it’s **capacity planning** or **router design**—different levels of realism may be necessary. Swing aims to support a broad range of these needs.

2. **Responsiveness**:
   Swing must enable controlled **modifications to ambient network conditions**:

   * Link **bandwidth**.
   * **Round-trip time (RTT)** distributions.
   * The **mix of application types** (e.g., increasing P2P or VoIP traffic).
   * **Application-specific behaviors** (e.g., growing average P2P file sizes).

   Importantly, when these parameters are altered, the generated traces should **meaningfully reflect** these changes—emulating how real network traffic would respond.

3. **Maximally Random**:
   Unlike simple **trace replay**, which deterministically duplicates a trace, Swing seeks to generate **families of traces** that maintain core statistical properties but differ in specific connection patterns. This stochastic flexibility is essential for evaluating algorithms under a range of plausible but varied network conditions. While fully measuring randomness is beyond the scope of this work, this principle fundamentally shapes Swing's design.

---

### **B. An Overview of the Swing System**

The authors' **central hypothesis** is that to realistically and responsively generate synthetic traces, the system must model three core components:

1. **Users and Programs**: Who initiates the communication? How frequently? How long are their sessions? Without modeling users, it’s impossible to simulate how application or architectural changes affect user experience.

2. **Host Systems**: The behavior of the hardware and software hosting these applications, including the specifics of protocol implementations.

3. **The Network Path**: The wider network infrastructure carrying packets between endpoints, which directly impacts packet timing through **latency**, **bandwidth**, and **loss** characteristics.

The process of trace generation starts with the assumption of **perfect knowledge** about these three domains. Later sections describe how Swing infers these from a single passive trace. But fundamentally, Swing operationalizes this model by:

* **Emulating large-scale network topologies** with tools like **ModelNet**.
* **Initiating synthetic flows** between sources and sinks across an emulated network.
* **Capturing the generated packet traces** at a target link within this emulation.

Each **flow** is driven by models derived from user, application, and network behavior extracted from the original trace. This method produces a generated trace that replicates key traffic characteristics such as **average bandwidth** and **burstiness**.

Critically, this approach allows Swing to support **"what-if" analyses**: by tweaking parameters like RTTs or application mixes, researchers can project how traffic might evolve under different conditions.

Finally, these synthetic traces are valuable not just for **testing queue management** or **flow classification** algorithms, but also for evaluating real systems under controlled, reproducible traffic conditions—something difficult to achieve with existing testbeds like **PlanetLab**, where conditions are uncontrollable and non-reproducible.

---

### **C. Building a Structural Model of Traffic**

Swing’s structural model is deeply informed by prior research advocating for **multi-layer protocol modeling**. The authors pragmatically partition the modeling space into four hierarchical components:

1. **Users**:
   They define when and how often users (or automated agents) initiate activities. This includes:

   * **Activity frequency**.
   * **Destination site distribution**.
   * **"Think time"** between requests.

   Even automated behaviors, like SNMP polling, are conceptualized as "users" in this framework.

2. **Sessions**:
   High-level tasks that may involve multiple **parallel or sequential connections**—e.g., downloading a web page with embedded images or fetching chunks of a P2P file from multiple peers. Key factors include:

   * Number of connections.
   * Target distribution across sessions.

3. **Connections**:
   Low-level communication units characterized by:

   * **Destination**.
   * Number of **request-response exchanges**.
   * **Size** of requests and responses.
   * **Wait times** before responding.
   * **Inter-request spacing**.
   * Choice of **transport protocol** (TCP, UDP).
   * **Packet size distributions** and traffic types (e.g., constant bit rate).

4. **Network Characteristics**:
   End-to-end **path properties** from the original trace are essential to accurately simulate TCP dynamics:

   * **Loss rates**.
   * **Capacities**.
   * **Latencies** for each relevant host-path.

---

To define these structural elements concretely, the authors developed a parameterization summarized in **Table I** (in the paper). Importantly, their modeling process was **iterative**:

* Initially, they selected a minimal, intuitive parameter set.
* As they encountered unexplained behaviors (e.g., **persistent HTTP connections**), they introduced new parameters—such as **reqthink** time between successive HTTP requests.
* The process ended when they could comprehensively model multiple traces without an unmanageable explosion of parameters.

Each application (e.g., **HTTP**, **P2P**, **SMTP**) thus develops a distinct **"signature"** in terms of parameter distributions extracted from real traces. These signatures power Swing’s ability to simulate realistic traffic.

Although they acknowledge that their parameter set might not be universally applicable, for the applications they studied, it **sufficiently captured** traffic behavior. Later sections (**Section V**) provide a **sensitivity analysis** to quantify the impact of these parameters on trace realism.

---

### **D. Summary of Section II**:

Swing is not a naive traffic player—it’s a sophisticated, **model-driven system** that emulates how **users**, **applications**, and **networks** interact to produce traffic. By generating traces that are **realistic**, **responsive** to parameter changes, and **maximally random**, Swing bridges the gap between the static world of trace replay and the dynamic complexity of real-world network traffic.

---

Here’s the English translation of the provided section "III. ARCHITECTURE":

---

## III. ARCHITECTURE

In this section, we present our approach to populating the model outlined above for individual applications, extracting wide-area characteristics of hosts communicating across the target link, and then generating traces representative of these models.

### A. Parameterization Methodology

We begin with a trace to describe how we extract application characteristics from the target link. While our approach is general for various tracing infrastructures, we focus on `tcpdump` traces from a given link.

The first step in building per-application communication models is assigning packets and flows in a trace to appropriate application classes. Since performing such automatic classification is part of ongoing research and because we do not have access to packet payloads (typically required by existing tools) for most publicly available traces, we take the simple approach of assigning flows to application classes based on destination port numbers. Packets and flows that cannot be unambiguously assigned to an appropriate class are assigned to an "other" application class; we assign aggregate characteristics to this class. While this assumption limits the accuracy of models extracted for individual applications, it does not impact our ability to faithfully capture aggregate trace characteristics. Furthermore, our per-application models will improve as more sophisticated flow-classification techniques become available.

After assigning packets to per-application classes, we next group these packets into flows. We use TCP flags (when present) to determine connection start and end times. Then, we use the sequence and acknowledgment number advancements to calculate the size of data objects flowing in each direction of the connection. For example, consider a portion of an example tcpdump trace shown in Figure 2. The first line marks the SYN sent from an HTTP server at IP `10.0.3.172` to the client at IP `10.128.3.129`. The next line is for the ACK from the server; the acknowledgment number of 351 suggests a 351-byte request from the client. The next three lines show that the server sent a total of 4345 bytes of data in response.

Of course, there are many vagaries in determining the start and end of connections in a noisy trace. We use the timestamp of the first SYN packet sent by a host as the connection start time. Unless sufficient information is available in the trace to account for unseen packets for connections established before the trace began, we consider the first packet seen for a connection as the beginning of that connection when we do not see the initial SYN. Similarly, we account for connections terminated by a connection reset (RST) rather than a FIN.

Due to space constraints, we omit additional required details such as handling out-of-order packets, retransmissions, lost packets, and packets with invalid SYN/ACK values. Instead, we adopt strategies employed by earlier efforts faced with similar challenges. For instance, in the tcpdump output in Figure 2, if the response packet with sequence number `1449:2897` was lost, we would be able to infer this using the packets before and after it.

Given per-flow, per-application information, we apply a series of rules to extract values for our target parameters. The first step is to generate session information from connection information. We sort all application-related connections in increasing order of connection establishment times. The first time a connection appears with a given source IP address, we designate a session initiation and record the start time. A session consists of one or more RREs (Request-Response Exchanges). An RRE consists of one or more connections. For example, 10 parallel connections to download images in a web page constitute a single RRE. Likewise, the request for the base HTML page and its response constitute another RRE. We also initialize the start time of the first connection as the beginning of the first RRE and set the number of connections in this session to 1. Finally, we record the FIN time for the connection.

Upon seeing additional connections for an already discerned IP address, we perform one of the following actions:

1. If the SYN time of this new connection is within an RRE timeout limit (a configurable parameter), we conclude that the connection belongs to the same RRE (i.e., it is a parallel or simultaneous connection) and update our number of connections parameter. We also update the RRE end (termination time of all connections) of the RRE as the maximum of all connection termination times. Finally, we record the difference in start times of this new connection from the previous connection (interConn) in the same RRE.

2. If the SYN time of this new connection is not within the RRE timeout limit, we declare the termination of the current RRE and mark the beginning of a new RRE. We also calculate the time difference between the max FIN of the previous RRE and the start of this RRE. If that time difference is within the SESS timeout limit (another configurable parameter), we associate the new RRE with an existing session. Otherwise, we conclude that a new session has started.

For each connection, we also record the request think time as the time difference between a response from the server and the subsequent request from the client. We analyzed a variety of values for our configurable thresholds such as RRE end and SESS timeout. While we omit the details for brevity, using RRE timeout = 30 seconds and SESS timeout = 5 minutes works well for a range of scenarios.

In summary, each session consists of a number of RREs, which in turn consist of a number of protocol connections. Given information on individual sessions and their corresponding RREs, we extract a frequency distribution for each of the model parameters to generate empirical cumulative distribution functions (CDF). At this stage, we have the choice of either stopping with the empirical distributions or performing curve-fitting to analytical equations. For this work, we choose the former approach for simplicity and because it accurately represents observed data (e.g., capturing outliers), and leave the derivation and use of analytic distributions to future work.

---

### B. Extracting Network Characteristics

Given models of individual flows crossing a target network link, we next require an understanding of the characteristics of the network links responsible for transmitting data to and from the target link for the hosts communicating across the link. Our results show that accounting for such network conditions is critical to faithfully reproducing the arrival and burstiness characteristics of a packet trace.

Of course, we can only approximate the dynamically changing bandwidth, latency, and loss rate characteristics of all links that carry flows that eventually arrive at our target from a single packet trace. While we developed a number of techniques independently, and while it is impossible to determine the extent to which our approach differs from techniques in the literature (where important details may be omitted and source code is often unavailable), we do not necessarily innovate in our ability to passively extract wide-area network conditions from an existing packet trace. Rather, our contribution is to show that it is possible to both capture and replay these network conditions with sufficient fidelity to reproduce essential characteristics of the original trace.

Likewise, we assume that the modeled parameters (CDFs) are stationary for the duration of the trace. Augmenting our models to account for changing network characteristics is part of ongoing work. For the traces we consider, non-stationarity has not been a significant obstacle.

We extract network characteristics as follows. For each host (unique IP address) communicating across the target link, we wish to measure the delays, capacities, and loss rates of the set of links connecting the host to the target link. For simplicity, we aggregate all links from a source to the target and the links from the target to the destination into single logical links with aggregate capacity, loss rate, and latency corresponding to the links that make up this aggregate. Thus, in our model, we employ four separate logical links responsible for carrying traffic to and from the target link for all communicating hosts.

In cases where sufficient information is not available—for instance, if we do not see ACKs in the reverse direction—we approximate link characteristics for the host as the mean of the observed values for all other hosts on its side of the target link for the same application.

**Link delays:**
Consider a flow from a client C initiating a TCP connection to a server S. We use each flow in the underlying trace between these hosts as samples for the four sets of links responsible for carrying traffic between the flow endpoints. We record four quantities for packets arriving at the target link in both directions:

1. We record the time difference between a SYN (from C) and the corresponding SYN+ACK (from S) as a sample to estimate the sum of link delays `l2 + l3`.
2. We measure the difference between the SYN+ACK and the corresponding ACK packet as samples to estimate the sum of delays `l4 + l1`.
3. We use the difference between a response packet and its corresponding ACK (from C) to estimate `l4 + l1`.
4. We measure the time between a data packet and its corresponding ACK (from S) as further samples for `l2 + l3`.

For this analysis, we only consider hosts that have five or more sample values in the trace. We use the median (per host) of the sample values to approximate the sum of link delays (`l1 + l4` or `l2 + l3`). We chose the median because, in our current configuration, we assign static latency values to the links in our topology and believe that the median should be representative of the time it takes for a packet to reach the target link once it leaves hosts on either end.

An assumption behind our work is that flows follow symmetric paths in the forward and reverse direction, allowing us to assign values for `l1` and `l4` from samples of `l1 + l4`.

**Link capacities:**
We employ a variant of packet-pair techniques to estimate link capacities. We extract consecutive data packets not separated by a corresponding ACK from the other side. The time difference between these packet pairs gives an estimate of the time for the packets to traverse the bottleneck link from the host to the target link. Then, it is straightforward to calculate the bottleneck capacity using the formula:

**Link Capacity × Time Difference = Packet Size.**

Since we do passive estimation, we cannot control which packets are actually sent in pairs as opposed to active measurement techniques. To account for this shortcoming, we sort the packet-pair time separation values in ascending order and ignore the bottom half, exploiting the fact that with widespread use of delayed ACKs in TCP, half of the packets are sent as packet pairs.

Of course, it is known that packet-pair techniques overestimate the bottleneck capacity. For instance, queuing at a higher capacity downstream link can reduce the packet-pair separation, thereby inflating the capacity estimate. Likewise, packets sent in pairs might not arrive at the bottleneck in pairs. To account for these, we use the 50th percentile of the remaining sample values to approximate path capacity from a given host to the target link and leave a more exhaustive capacity estimation for future work. Finally, we assume that the incoming link to a host has capacity at least as large as the outgoing link and hence approximate `c4` and `c2` to the values of `c1` and `c3` respectively.

**Loss rates:**
Extracting loss rates accurately proved to be the most challenging aspect of capturing the network characteristics we considered. We measure loss rates using retransmissions and a simple algorithm. The algorithm starts by arranging packets of a flow based on increasing timestamps. In the absence of any losses, retransmissions, or reordering, we would expect to see a series of increasing TCP sequence numbers. However, if a packet en route to the target link is lost, the corresponding sequence number will be "missing" in our series, i.e., we will see the packets before and after the lost packet as consecutive arrivals at the target link.

This likely candidate for a loss is established if the lost packet (and the corresponding TCP sequence number) is seen at a later time (i.e., out-of-order), indicating retransmission from the sender. Such a missing sequence number is called a "hole" and we count it as a loss event.

However, it is possible that an out-of-order packet might have been a retransmitted packet. To disambiguate these two cases, we use a simple heuristic that considers all such candidates as packet losses unless the time difference between the timestamp of the packet and the corresponding hole is smaller than the RTT of the flow.

On the other hand, if there is an out-of-order TCP packet (retransmission) with no corresponding hole, it is likely that the packet arrived at the target but was lost en route to the destination. We use this loss event to estimate downstream loss rates. We estimate loss rates in a similar manner when we see flows in the opposite direction.

There are a number of assumptions that we make in the above algorithm to extract loss rates. We assume that losses experienced by a flow are typically not caused by the traffic we measure directly, i.e., losses on upstream and downstream links are caused by ambient congestion elsewhere in the network and not at some congestion point shared by multiple hosts from our trace. Using this assumption, we assign distinct loss rates for links connecting each host to the target rather than attempting to account for such shared congestion.

Our methodology cannot detect losses of retransmitted packets and losses during the TCP handshake.


---

## IV. VALIDATION


## Abstract: Validating Swing – Realistic and Responsive Network Traffic Generation

In this part of our study, we rigorously validated **Swing**, our network traffic generator, across diverse real-world traces from Japan (Mawi), New Zealand (Auckland), and the USA (CAIDA). These traces span different bandwidths and application mixes, offering an ideal testbed to evaluate Swing’s ability to reproduce not just high-level traffic metrics but also the fine-grained **burstiness** characteristics of network traffic at multiple time scales.

Our validation process followed a simple, yet thorough loop:

1. **Extract** application, user, and network parameter distributions from the original trace.
2. **Generate** synthetic traffic using Swing based on these parameters.
3. **Re-extract** the parameters from the generated trace and compare them to the originals.

The comparison focused on several aspects:

* Application mix and aggregate bandwidth.
* Packet and byte arrival burstiness.
* Per-application bandwidth.
* Fine-grained parameter distributions.

To compare burstiness, we leveraged **wavelet-based multi-resolution analysis (MRA)** — a robust method to visualize and quantify traffic variance across time scales. Here, energy plots illustrate the “burstiness signature” of traffic, with characteristic dips revealing underlying phenomena like TCP’s self-clocking behavior or upstream bottlenecks.

### Key Findings

1. **High Fidelity in Aggregate Reproduction**
   For all traces—ranging from Auckland's 5 Mbps to CAIDA's 200 Mbps backbone—we were able to closely replicate the original traffic’s aggregate characteristics. Parameters like HTTP bandwidth and per-application packets per second (PPS) matched closely, demonstrating Swing's efficacy without the need for manual tuning.

2. **Fine-Grained Parameter Matching**
   We accurately captured structural parameters, such as request/response sizes, number of parallel connections, and user think times. While reproducing human-driven timing parameters like inter-session delays posed challenges (e.g., minor differences in inter-connection times), mechanistic parameters like request sizes were matched almost perfectly.

3. **Capturing Burstiness Across Time Scales**
   Our energy plots showed a near-exact match between the original and Swing-generated traces across various applications (HTTP, Squid, Napster, etc.) and time scales, from sub-millisecond to minutes. This fidelity is unprecedented, especially in reproducing burstiness not just globally (as earlier work did) but also at fine-grained, sub-RTT scales.

4. **Wide-Area Network Effects Matter**
   Our sensitivity analyses revealed that accurately modeling **network conditions**—latency, capacity, and loss—is essential to reproducing realistic burstiness. Ignoring these aspects led to synthetic traces that superficially resembled the originals in bandwidth but diverged significantly in temporal structure.

5. **Model Parameter Sensitivity**
   Beyond network effects, we found that structural parameters like inter-connection timing (interConn) and inter-request exchanges (interRRE) critically influence the shape of traffic burstiness. Omitting these led to significant deviations, reinforcing the necessity of Swing’s detailed modeling.

6. **Responsiveness to What-If Scenarios**
   We also demonstrated Swing’s strength in projecting traffic into alternate scenarios:

* Doubling link latencies shifted characteristic dips in the energy plot, matching theoretical expectations.
* Increasing application session counts or modifying request/response sizes resulted in intuitive changes in burstiness and aggregate bandwidth.
* For example, amplifying Squid sessions 20-fold made the overall trace's burstiness profile resemble Squid's more than HTTP’s.

### Conclusion

Swing is the **first system** to demonstrate the faithful reproduction of **burstiness characteristics** at multiple time scales across multiple real-world traces, capturing both the byte and packet-level dynamics in both traffic directions. Our approach, driven by empirical distribution extraction rather than fitting assumed distributions, proves that a simple, structurally-aware model is sufficient to generate realistic, responsive synthetic traffic.

Moreover, Swing’s modular design enables exploring **hypothetical future scenarios**—altering network conditions, application mixes, or user behaviors—and observing their impact on traffic dynamics. This makes Swing a powerful tool for system designers, researchers, and practitioners aiming to evaluate systems under realistic and diverse network conditions.

This is a fantastic exercise! Let's approach it methodically.

---

## **1. Explanation of Plots Used in A and B Validation**

### **A. Distribution Parameter Validation:**

The authors validated their parameter extraction by comparing **empirical cumulative distribution functions (CDFs)** for three key network characteristics:

**Fig. 7: Host-to-Target Link Delays CDF**

* X-axis: Delay from host to the target link (ms).
* Y-axis: Cumulative fraction.
* Purpose: Confirm that extracted network delays match between original and Swing-generated traces.
  ✅ **Metric Source:** Time difference between specific TCP control packets (e.g., SYN and SYN-ACK).

---

**Fig. 8: Link Capacities CDF**

* X-axis: Link capacity in Mbps.
* Y-axis: Cumulative fraction.
* Purpose: Validate that upstream/downstream link capacity distributions are preserved.
  ✅ **Metric Source:** Derived using passive "packet-pair" techniques measuring time deltas between consecutive packets.

---

**Fig. 9: Link Loss Rates CDF**

* X-axis: Loss rate percentage.
* Y-axis: Cumulative fraction.
* Purpose: Confirm that packet loss characteristics are preserved.
  ✅ **Metric Source:** Based on TCP retransmission detection in packet traces.

---

✅ **In summary**, in section A, they used **CDF plots of network performance metrics** — latency, bandwidth, and packet loss — to validate their model's realism.

---

### **B. Wavelet-Based Analysis:**

Here, the authors employed **Wavelet Multi-Resolution Energy Analysis (WMEA)** to study **burstiness** across **multiple time scales**.

Each **Energy plot** (Figures 10-17) shows:

* **X-axis:** Time scale `j` (logarithmic steps, e.g., 1ms, 2ms, 4ms, etc.).
* **Y-axis:** log₂(Energy(j)) — energy content (variance) at that time scale.

✅ **Key insight**: Dips in the plot indicate regularities or periodic behaviors. E.g.:

* Dips at \~200ms: Correspond to Round Trip Time (RTT).
* Dips at \~8ms: Indicate upstream link bandwidth bottlenecks.

✅ **Metric Source**: The input signal is **bytes or packets arrival time series** (e.g., bandwidth over time), not inter-arrival times directly.

> **IMPORTANT:** The WMEA is applied on **aggregated bandwidth or byte arrival processes**, typically as a time series of byte counts in fixed-width bins (e.g., every 1ms).
> It is NOT applied directly to the inter-arrival times themselves, but to the **time series representation** derived from those events.

---

✅ **In summary:**

* WMEA is based on **byte or packet arrival time series**, often transformed into **bandwidth time series** (e.g., bytes per millisecond).
* The wavelet transform is then applied to this time series to analyze how variance (energy) changes with time scale.

---

## **2. Code Example: Simulating A and B Validation Plots**

We'll simulate **both CDF plots (for A)** and **Wavelet Energy Plots (for B)** using **random data**.

### **Install required packages first:**

```bash
pip install numpy matplotlib pywavelets
```

---

### ✅ **Step 1: Simulating CDF Plots for A**

```python
import numpy as np
import matplotlib.pyplot as plt

# --- Simulate Random Data ---

np.random.seed(42)

# Simulate delays in ms
original_delays = np.random.normal(loc=100, scale=20, size=1000)
swing_delays = np.random.normal(loc=105, scale=20, size=1000)

# Simulate capacities in Mbps
original_caps = np.random.uniform(1, 100, size=1000)
swing_caps = np.random.uniform(1, 100, size=1000)

# Simulate loss rates in %
original_loss = np.random.beta(a=2, b=10, size=1000) * 100
swing_loss = np.random.beta(a=2.2, b=9.5, size=1000) * 100

# --- Plot CDFs ---

def plot_cdf(data1, data2, xlabel, title):
    sorted1 = np.sort(data1)
    sorted2 = np.sort(data2)
    y = np.linspace(0, 1, len(sorted1))
    
    plt.figure()
    plt.plot(sorted1, y, label='Original')
    plt.plot(sorted2, y, label='Swing')
    plt.xlabel(xlabel)
    plt.ylabel('Cumulative fraction')
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.show()

# Plot for delay
plot_cdf(original_delays, swing_delays, 'Delay (ms)', 'Fig. 7: Host-to-Link Delay CDF')

# Plot for capacity
plot_cdf(original_caps, swing_caps, 'Capacity (Mbps)', 'Fig. 8: Link Capacity CDF')

# Plot for loss
plot_cdf(original_loss, swing_loss, 'Loss Rate (%)', 'Fig. 9: Loss Rate CDF')
```

---

### ✅ **Code explanation:**

1. **np.random.normal**: simulate normally distributed delays.
2. **np.random.uniform**: simulate uniformly distributed capacities.
3. **np.random.beta**: simulate loss rates skewed towards low values.
4. **np.sort** + **np.linspace**: standard method to plot a **CDF**.
5. **matplotlib**: plot each CDF.

---

### ✅ **Step 2: Simulating Wavelet Energy Plot for B**

```python
import pywt

# --- Simulate Time Series of Packet Arrivals ---

time = np.linspace(0, 10, 1000)  # Simulated 10 seconds with 1ms resolution
signal_orig = np.sin(2 * np.pi * 5 * time) + np.random.normal(0, 0.5, size=time.shape)
signal_swing = np.sin(2 * np.pi * 5 * time + 0.1) + np.random.normal(0, 0.5, size=time.shape)

# --- Perform Wavelet Transform ---

def wavelet_energy(signal, wavelet='db4', level=5):
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    energies = [np.sum(np.square(c)) for c in coeffs]
    return energies

energy_orig = wavelet_energy(signal_orig)
energy_swing = wavelet_energy(signal_swing)

scales = np.arange(len(energy_orig))

# --- Plot Energy vs Scale ---

plt.figure()
plt.plot(scales, np.log2(energy_orig), label='Original')
plt.plot(scales, np.log2(energy_swing), label='Swing')
plt.xlabel('Time Scale j')
plt.ylabel('log2(Energy(j))')
plt.title('Simulated Wavelet Energy Plot')
plt.legend()
plt.grid()
plt.show()
```

---

### ✅ **Code explanation:**

1. **Simulated time series**: Sine wave with noise represents packet arrivals over time.
2. **pywt.wavedec**: Performs discrete wavelet decomposition.
3. **Energy** at each level = sum of squares of coefficients.
4. **np.log2**: plotting energy in log-scale as per paper.
5. **Plot** original and Swing signals' wavelet energy for comparison.

---

## ✅ **Key Takeaways:**

* **A validation (CDFs):** Classic way to compare statistical distributions.
* **B validation (Wavelet Energy):** Highlights differences in variance ("burstiness") across time scales — a core part of **Wavelet Multi-Resolution Energy Analysis (WMEA)**.
* **WMEA works on bandwidth-like time series**, not raw inter-arrival times.

---

Would you like me to expand this example to include real packet arrival simulations and a more complex WMEA (e.g., continuous wavelet transform)? Let me know!


Great and very precise questions — this shows your deep engagement with the **methodology** of traffic characterization! Let's clarify **each one**:

---

## ✅ **Fig. 7: Host-to-Target Link Delays CDF**

### **How can this be measured with a single captured pcap?**

The **Swing authors** used **passive delay inference** based on analyzing **TCP handshake packets** within **a single packet trace** (pcap) collected at a network link.

### **Method:**

1. **SYN → SYN-ACK timing:**
   For TCP connections initiated by a client, the trace can observe:

   * SYN from client.
   * SYN+ACK from server.

   The **time difference** between these packets corresponds to the **round-trip time (RTT)** plus any local processing delays at the server.

2. **Assumptions:**

   * Flows are **symmetric** (i.e., similar delays both directions).
   * Processing delay is **negligible** or uniform.
   * Trace point captures **both directions** of the traffic.

3. **Approximation:**

   * For each TCP handshake, measure:
     `Δt = t_SYN+ACK - t_SYN`
   * Use Δt as **a sample** of the combined upstream + downstream delay.

4. **Aggregate** many such samples into a **CDF**.

---

✅ **Bottom line:** Even with a **single passive trace**, observing both SYN and SYN+ACK allows **estimating delay** without injecting any probes.

---

## ✅ **Fig. 8: Link Capacities CDF**

### **How is this measured in practice?**

The authors used a **passive "packet-pair" technique** — typically used in **active measurements**, but applied here to passive traces.

### **Method:**

1. **Identify packet pairs**:

   * Look for **consecutive data packets** sent from a host to the destination **without an ACK** in between.
     These likely represent **back-to-back packets** sent by the sender.

2. **Measure time difference:**

   * Δt = `t_packet2 - t_packet1`

3. **Estimate capacity:**

   * Assume both packets are **maximum segment size (MSS)**, e.g., 1500 bytes.
   * Then:
     `Capacity ≈ PacketSize / Δt`

4. **Why this works:**
   On a congested link, the time between back-to-back packets reflects **serialization delay** at the **bottleneck link**.

5. **Challenges:**

   * Packet coalescing or reordering can affect accuracy.
   * Must filter for clean packet-pairs.
   * Use statistical methods, e.g., **take median** of many such measurements.

6. **Plot** CDF of estimated link capacities.

---

✅ **Bottom line:** **Passive packet-pair measurements** allow rough estimation of **link capacities** without active probing.

---

## ✅ **Fig. 9: Link Loss Rates CDF**

### **How can loss be inferred with just a trace?**

By analyzing **sequence numbers** and **retransmissions** in **TCP flows**.

### **Method:**

1. **Observe sequence numbers:**

   * In an ideal flow: seq1 < seq2 < seq3 ... (monotonic).

2. **Detect missing sequences:**

   * If a packet is missing, and later a **retransmitted packet** with the **same sequence number** is observed, infer that the **original packet was lost**.

3. **Count retransmissions:**

   * For each flow, count how many **distinct retransmissions** occur.

4. **Estimate loss rate:**

   * `Loss Rate = (Number of losses) / (Total number of packets)`

5. **Aggregate:**

   * Repeat across multiple flows.
   * Plot CDF of inferred loss rates for different hosts/links.

### **Example:**

If:

* Host A sends 100 packets.
* Trace shows 2 retransmissions (due to missing seq numbers).

Then:
**Estimated loss rate** = 2%.

---

✅ **Bottom line:** **TCP retransmissions** and **sequence analysis** enable **passive inference** of **loss rates**, even from a single trace.

---

## ✅ **Summary of how all three are done:**

| **Metric**    | **Method**                                            | **Data Needed**                               |
| ------------- | ----------------------------------------------------- | --------------------------------------------- |
| **Delay**     | SYN → SYN-ACK time difference                         | TCP handshake packets                         |
| **Capacity**  | Passive packet-pair: time between consecutive packets | Pairs of data packets without intervening ACK |
| **Loss rate** | Detect missing sequence numbers + retransmissions     | TCP sequence and acknowledgment numbers       |

---

✅ These are all **passive measurement techniques**, widely accepted in network measurement research. Swing innovatively applied **all three** together from **single-trace analysis**.

---

Would you like me to simulate an example of **passive delay estimation** or **passive packet-pair capacity estimation** in Python? Let me know which one!


Excellent! This is a key part of understanding **how to validate** and **analyze** traffic generation models using **controlled perturbations**.

Let’s go step by step.

---

## ✅ **1. Explanation of the plots and validations for C and D**

---

## **C. Sensitivity Analysis**

**Goal:**
To understand **how sensitive** the generated traffic is to specific **model parameters**. If you remove or change a parameter, does the traffic still match the original?

**How they did it:**

### ➡️ **Fig. 18: Sensitivity to network characteristics**

* Swing generated multiple traces with different levels of **network modeling**:

  * **NoNetwork** → no emulation at all.
  * **LinkLatencies** → only emulate network delays.
  * **LatencyCapacities** → emulate delays and link capacities.
  * **LatencyCapacityLossRates** → emulate everything.
* Compared these to **Mawi** original trace.
* The more parameters you emulate, the **closer** the generated **energy plot** is to the original.

**Insight:**
Network parameters like **latency**, **capacity**, and **loss rate** **significantly affect burstiness**, especially at fine time scales.

---

### ➡️ **Fig. 19: Sensitivity to interRRE and interconn**

* Tested impact of removing **application-level timing parameters**:

  * For **HTTP**: remove inter-RRE timing → traffic looks much **less bursty**.
  * For **SQUID**: remove inter-connection timing → alters large time-scale burstiness.

**Insight:**
Both **application behavior** (e.g., how sessions and connections are spaced) and **network behavior** impact the **burstiness**.

---

### ➡️ **Fig. 20: Variability across runs**

* Ran Swing **10 times** with the **same parameters** but **different random seeds**.
* Plotted **mean and standard deviation** of energy plots.

**Insight:**
Even with a **deterministic model**, randomness in trace generation can cause **variability**, especially at **large time scales**.

---

## ✅ **Key takeaway for sensitivity:**

Models must capture **both** network and application-level behaviors accurately to reproduce **realistic burstiness**.

---

---

## **D. Responsiveness**

**Goal:**
Show that Swing can **adapt** to different scenarios, not just replicate one trace.

**How they did it:**

### ➡️ **Fig. 21: Doubling latency and response size**

* Modified the generated trace to:

  * **Double link latency** → the **dip** in the energy plot **shifts right** (longer RTT).
  * **Double response size** → overall **energy increases** across all time scales.

**Insight:**
The model reacts **as expected** when network or application parameters change — a sign that the **structural model is sound**.

---

### ➡️ **Fig. 22: Changing application mix**

* Increased **SQUID sessions** by a factor of **20**.
* The energy plot of the overall trace becomes **similar** to the **SQUID-only** trace.

**Insight:**
Changing **application mix** significantly alters traffic burstiness.

---

✅ **Key takeaway for responsiveness:**
A good traffic generator allows controlled exploration of **what-if scenarios** and **reacts predictably** to changes in parameters.

---

---

## ✅ **2. Code example: Simulating these plots with random data**

We’ll use Python with **NumPy** and **Matplotlib** to simulate **energy plots** for:

* **Sensitivity:** varying inclusion of model components.
* **Responsiveness:** changing model parameters.

---

### ✅ **Step 1: Import libraries**

```python
import numpy as np
import matplotlib.pyplot as plt
```

---

### ✅ **Step 2: Define function to simulate energy plot**

We'll simulate **energy** at multiple **time scales**.

```python
def simulate_energy(base_level=10, variability=5, time_scales=15, shift=0, amplification=1):
    """
    Simulates a fake wavelet energy plot.
    
    Parameters:
        base_level: Base energy.
        variability: Variability across scales.
        time_scales: Number of scales.
        shift: Shift in the energy dip (e.g., simulating RTT shift).
        amplification: Amplify overall energy (e.g., doubling response size).
        
    Returns:
        Array of log2 energy values for each scale.
    """
    scales = np.arange(time_scales)
    # Simulate base energy with variability
    energy = base_level + variability * np.sin(0.3 * (scales + shift)) + np.random.normal(0, 0.5, time_scales)
    energy = energy * amplification
    return energy
```

---

### ✅ **Step 3: Sensitivity plots (like Fig. 18)**

```python
time_scales = 15
scales = np.arange(time_scales)

# Simulating different network modeling levels
no_network = simulate_energy(base_level=10, variability=2)
latency_only = simulate_energy(base_level=10, variability=3)
latency_capacity = simulate_energy(base_level=10, variability=4)
full_model = simulate_energy(base_level=10, variability=5)
original = simulate_energy(base_level=10, variability=5)

plt.figure(figsize=(8,6))
plt.plot(scales, no_network, label='No Network')
plt.plot(scales, latency_only, label='Latency')
plt.plot(scales, latency_capacity, label='Latency + Capacity')
plt.plot(scales, full_model, label='Full Model')
plt.plot(scales, original, label='Original (Mawi)')
plt.xlabel("Time Scale j")
plt.ylabel("log2(Energy(j))")
plt.title("Sensitivity to Network Characteristics")
plt.legend()
plt.grid(True)
plt.show()
```

---

### ✅ **Step 4: Responsiveness plot (like Fig. 21)**

```python
# Base simulation
base = simulate_energy()

# Doubling latency -> shift the dip
latency_double = simulate_energy(shift=2)

# Doubling response size -> amplify energy
rsp_double = simulate_energy(amplification=2)

plt.figure(figsize=(8,6))
plt.plot(scales, base, label='Swing Baseline')
plt.plot(scales, latency_double, label='Latency x2')
plt.plot(scales, rsp_double, label='Response Size x2')
plt.xlabel("Time Scale j")
plt.ylabel("log2(Energy(j))")
plt.title("Responsiveness to Latency and Response Size")
plt.legend()
plt.grid(True)
plt.show()
```

---

### ✅ **Step 5: Variability across runs (like Fig. 20)**

```python
runs = []
for _ in range(10):
    run = simulate_energy()
    runs.append(run)

runs = np.array(runs)
mean_run = runs.mean(axis=0)
std_run = runs.std(axis=0)

plt.figure(figsize=(8,6))
plt.plot(scales, mean_run, label='Mean of 10 Runs')
plt.fill_between(scales, mean_run - std_run, mean_run + std_run, alpha=0.3, label='±1 std')
plt.xlabel("Time Scale j")
plt.ylabel("log2(Energy(j))")
plt.title("Variability across multiple runs")
plt.legend()
plt.grid(True)
plt.show()
```

---

## ✅ **Code Explanation:**

* `simulate_energy`: generates synthetic energy plot data with configurable base level, variability, shift, and amplification.
* For **sensitivity**, we compare multiple **levels of modeling**.
* For **responsiveness**, we change parameters (shift or scale).
* For **variability**, we simulate **multiple runs** and compute **mean + std**.

---

## ✅ **Key insight from this code:**

These kinds of **synthetic experiments** allow you to **test the behavior of your traffic generation framework** without needing real traces initially, to **validate model changes** visually and statistically.

---

If you want, I can adapt this further to simulate specific **parameter omission** like **no inter-RRE** or **no interconn**!

