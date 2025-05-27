import matplotlib.pyplot as plt
import numpy as np
import pywt

# --- Simulate Time Series of Packet Arrivals ---

time = np.linspace(0, 10, 1000)  # Simulated 10 seconds with 1ms resolution
signal_orig = np.sin(2 * np.pi * 5 * time) + np.random.normal(0, 0.5, size=time.shape)
signal_swing = np.sin(2 * np.pi * 5 * time + 0.1) + np.random.normal(
    0, 0.5, size=time.shape
)

# --- Perform Wavelet Transform ---


def wavelet_energy(signal, wavelet="db4", level=5):
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    energies = [np.sum(np.square(c)) for c in coeffs]
    return energies


energy_orig = wavelet_energy(signal_orig)
energy_swing = wavelet_energy(signal_swing)

scales = np.arange(len(energy_orig))

# --- Plot Energy vs Scale ---

plt.figure()
plt.plot(scales, np.log2(energy_orig), label="Original")
plt.plot(scales, np.log2(energy_swing), label="Swing")
plt.xlabel("Time Scale j")
plt.ylabel("log2(Energy(j))")
plt.title("Simulated Wavelet Energy Plot")
plt.legend()
plt.grid()
plt.show()
plt.savefig("./sandbox/python-plots/wavelet_energy_plot.png", dpi=300)
