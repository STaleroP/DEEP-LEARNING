#!/usr/bin/env python3
"""
wave_py.py
Resolución EDO-1D (MDF matricial) — versión parametrizable por m.
Salida en carpeta results/Python/m_{m}/:
 - wave_py.csv   : snapshots (t,x0,x1,...,xm)
 - errors.csv    : t, L2, Linf
 - timing.txt    : wall time (s)
"""
import sys, os, time, csv
import numpy as np

# parse m from argv
if len(sys.argv) > 1:
    m = int(sys.argv[1])
else:
    m = 100

# Physical params
L = 100.0
c = 10.0
T = 100.0

# Mesh
h = L / m
x = np.linspace(0, L, m + 1)

# CFL settings
Lambda = 0.8
k = Lambda * h / c
nt = int(np.ceil(T / k))
tvec = np.linspace(0, nt * k, nt + 1)

# initial conditions
def f_init(x): return np.sin(np.pi * x / L)
def g_init(x): return np.zeros_like(x)

n_inner = m - 1
xi = x[1:-1]
u0 = f_init(xi)
v0 = g_init(xi)

# build tridiagonal M directly
M = np.zeros((n_inner, n_inner), dtype=np.float64)
for i in range(n_inner):
    M[i, i] = 2.0 * (1.0 - Lambda**2)
    if i > 0:
        M[i, i - 1] = Lambda**2
    if i < n_inner - 1:
        M[i, i + 1] = Lambda**2

# initial steps
u_jm1 = u0.copy()
# use safe stencil + velocity term
u_j = (1 - Lambda**2) * u0 + (Lambda**2 / 2.0) * (np.roll(u0, -1) + np.roll(u0, 1)) + k * v0
# correct boundaries (Dirichlet u=0)
u_j[0] = (1 - Lambda**2) * u0[0] + (Lambda**2 / 2.0) * u0[1] + k * v0[0]
u_j[-1] = (1 - Lambda**2) * u0[-1] + (Lambda**2 / 2.0) * u0[-2] + k * v0[-1]

# storage
snapshots = []
times = []
errors = []

# exact solution for mode fundamental
def exact_solution(xi, tt):
    return np.cos(c * np.pi * tt / L) * np.sin(np.pi * xi / L)

# store initial two snapshots (include boundaries)
snapshots.append(np.concatenate(([0.0], u_jm1, [0.0])))
times.append(0.0)
# compute errors for t=0
err0 = np.concatenate(([0.0], u_jm1, [0.0])) - np.sin(np.pi * x / L)  # exact at t=0
L2_0 = np.sqrt(h * np.sum(err0[1:-1]**2))
Linf_0 = np.max(np.abs(err0))
errors.append((0.0, L2_0, Linf_0))

snapshots.append(np.concatenate(([0.0], u_j, [0.0])))
times.append(k)
u_ex = exact_solution(x[1:-1], k)
err1_inner = u_j - u_ex
L2_1 = np.sqrt(h * np.sum(err1_inner**2))
Linf_1 = np.max(np.abs(err1_inner))
errors.append((k, L2_1, Linf_1))

# time stepping
tstart = time.perf_counter()
u_prev = u_jm1.copy()
u_curr = u_j.copy()

save_interval = max(1, nt // 200)
for j in range(1, nt):
    u_next = M.dot(u_curr) - u_prev
    if j % save_interval == 0:
        snapshots.append(np.concatenate(([0.0], u_next, [0.0])))
        times.append((j + 1) * k)
    # error vs exact
    tt = (j + 1) * k
    u_ex = exact_solution(x[1:-1], tt)
    err = u_next - u_ex
    L2 = np.sqrt(h * np.sum(err**2))
    Linf = np.max(np.abs(err))
    errors.append((tt, L2, Linf))
    u_prev, u_curr = u_curr, u_next
tend = time.perf_counter()

wall_time = tend - tstart

# results folder
outdir = os.path.join("results", "Python", f"m_{m}")
os.makedirs(outdir, exist_ok=True)

# write snapshots CSV
csv_file = os.path.join(outdir, "wave_py.csv")
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    header = ["t"] + [f"x{i}" for i in range(len(x))]
    writer.writerow(header)
    for ti, ui in zip(times, snapshots):
        writer.writerow([ti] + ui.tolist())

# write errors
err_file = os.path.join(outdir, "errors.csv")
with open(err_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t", "L2", "Linf"])
    for row in errors:
        writer.writerow(row)

# timing
with open(os.path.join(outdir, "timing.txt"), "w") as f:
    f.write(f"{wall_time:.6f}\n")

print(f"Python: m={m}, snaps={len(snapshots)}, time={wall_time:.6f}s -> {csv_file}")
