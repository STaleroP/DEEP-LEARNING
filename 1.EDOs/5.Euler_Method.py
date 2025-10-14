# Euler's Method for Radioactive Decay (Explicit & Implicit) with Error Analysis
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------
# Problem: Radioactive decay
# dN/dt = -alpha * N
# ------------------------------
N0 = 100        # initial number of nuclei
alpha = 0.25    # decay constant
t0 = 0          # initial time
tf = 5          # final time
dt = 0.5        # integration step

# ------------------------------
# Time setup
# ------------------------------
nt = int((tf - t0) / dt)
t_vals = np.linspace(t0, tf, nt + 1)

# Arrays for solutions
N_explicit = np.zeros(nt + 1)
N_implicit = np.zeros(nt + 1)
N_exact = N0 * np.exp(-alpha * t_vals)

# Initial conditions
N_explicit[0] = N0
N_implicit[0] = N0

# ------------------------------
# Euler iterations
# ------------------------------
for i in range(nt):
    # Explicit Euler
    N_explicit[i + 1] = N_explicit[i] - alpha * dt * N_explicit[i]
    # Implicit Euler
    N_implicit[i + 1] = N_implicit[i] / (1 + alpha * dt)

# ------------------------------
# Error Analysis
# ------------------------------
local_error_explicit = np.abs(N_exact[:-1] - N_explicit[:-1])
local_error_implicit = np.abs(N_exact[:-1] - N_implicit[:-1])

global_error_explicit = np.abs(N_exact - N_explicit)
global_error_implicit = np.abs(N_exact - N_implicit)

# ------------------------------
# Plots: Solutions
# ------------------------------
plt.figure(figsize=(8, 5))
plt.plot(t_vals, N_exact, 'k-', label="Exact")
plt.plot(t_vals, N_explicit, 'o-', label="Explicit Euler")
plt.plot(t_vals, N_implicit, 's-', label="Implicit Euler")
plt.xlabel("Time")
plt.ylabel("Number of nuclei N(t)")
plt.title("Radioactive Decay: Explicit vs Implicit Euler")
plt.legend()
plt.grid(True)
plt.show()

# ------------------------------
# Plots: Errors
# ------------------------------
plt.figure(figsize=(8, 5))
plt.plot(t_vals, global_error_explicit, 'o-', label="Explicit Global Error")
plt.plot(t_vals, global_error_implicit, 's-', label="Implicit Global Error")
plt.xlabel("Time")
plt.ylabel("Global Error")
plt.title("Global Errors over Time")
plt.legend()
plt.grid(True)
plt.show()

# Log scale error plot
plt.figure(figsize=(8, 5))
plt.semilogy(t_vals, global_error_explicit, 'o-', label="Explicit Global Error")
plt.semilogy(t_vals, global_error_implicit, 's-', label="Implicit Global Error")
plt.xlabel("Time")
plt.ylabel("Global Error (log scale)")
plt.title("Global Errors (Log Scale)")
plt.legend()
plt.grid(True, which="both")
plt.show()

# ------------------------------
# Convergence Study
# ------------------------------
dt_values = [0.5, 0.25, 0.1, 0.05, 0.01]
errors_explicit = []
errors_implicit = []

for dt in dt_values:
    nt = int((tf - t0) / dt)
    t_vals_temp = np.linspace(t0, tf, nt + 1)

    N_explicit = np.zeros(nt + 1)
    N_implicit = np.zeros(nt + 1)
    N_exact = N0 * np.exp(-alpha * t_vals_temp)

    N_explicit[0] = N0
    N_implicit[0] = N0

    for i in range(nt):
        # Explicit Euler
        N_explicit[i + 1] = N_explicit[i] - alpha * dt * N_explicit[i]
        # Implicit Euler
        N_implicit[i + 1] = N_implicit[i] / (1 + alpha * dt)

    # Global error at final time
    errors_explicit.append(abs(N_exact[-1] - N_explicit[-1]))
    errors_implicit.append(abs(N_exact[-1] - N_implicit[-1]))

# ------------------------------
# Plot: Convergence (log-log)
# ------------------------------
plt.figure(figsize=(8, 5))
plt.loglog(dt_values, errors_explicit, 'o-', label="Explicit Euler")
plt.loglog(dt_values, errors_implicit, 's-', label="Implicit Euler")

# Reference O(dt) line
ref = errors_explicit[-1] * (np.array(dt_values) / dt_values[-1])
plt.loglog(dt_values, ref, 'k--', label="O(dt) reference")

plt.xlabel("Time step size dt")
plt.ylabel("Global error at $t=tf$")
plt.title("Convergence of Euler Methods (Radioactive Decay)")
plt.legend()
plt.grid(True, which="both")
plt.show()
