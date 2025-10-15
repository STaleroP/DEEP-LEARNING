import numpy as np
import matplotlib.pyplot as plt
import time
import csv
from matplotlib.animation import FuncAnimation

# Parámetros físicos y malla
L = 100.0
c = 10.0
m = 100
h = L / m
x = np.linspace(0, L, m + 1)

T = 15.0
Lambda = 0.8
k = Lambda * h / c
nt = int(np.ceil(T / k))
t = np.linspace(0, nt * k, nt + 1)

# Condiciones iniciales
def f_init(x): return np.sin(np.pi * x / L)
def g_init(x): return np.zeros_like(x)

n_inner = m - 1
xi = x[1:-1]
u0 = f_init(xi)
v0 = g_init(xi)

# Matriz tridiagonal M
M = np.zeros((n_inner, n_inner))
for i in range(n_inner):
    M[i, i] = 2.0 * (1.0 - Lambda ** 2)
    if i > 0:
        M[i, i - 1] = Lambda ** 2
    if i < n_inner - 1:
        M[i, i + 1] = Lambda ** 2

# Paso inicial
u_jm1 = u0.copy()
u_j = ((1 - Lambda ** 2) * u0
       + (Lambda ** 2 / 2.0) * (np.roll(u0, -1) + np.roll(u0, 1))
       + k * v0)
u_j[0] = (1 - Lambda ** 2) * u0[0] + (Lambda ** 2 / 2.0) * u0[1]
u_j[-1] = (1 - Lambda ** 2) * u0[-1] + (Lambda ** 2 / 2.0) * u0[-2]

# Evolución temporal
snapshots = []
times = []

snapshots.append(np.concatenate(([0.0], u_jm1, [0.0])))
times.append(0.0)
snapshots.append(np.concatenate(([0.0], u_j, [0.0])))
times.append(k)

tstart = time.perf_counter()
u_prev = u_jm1.copy()
u_curr = u_j.copy()

for j in range(1, nt):
    u_next = M.dot(u_curr) - u_prev
    if j % max(1, nt // 200) == 0:
        snapshots.append(np.concatenate(([0.0], u_next, [0.0])))
        times.append((j + 1) * k)
    u_prev, u_curr = u_curr, u_next
tend = time.perf_counter()

print(f"Simulación completada en {tend - tstart:.4f} s con {len(snapshots)} snapshots")

# Exportar CSV con evolución
csv_file = "wave_py.csv"
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    header = ["t"] + [f"x{i}" for i in range(len(x))]
    writer.writerow(header)
    for ti, ui in zip(times, snapshots):
        writer.writerow([ti] + ui.tolist())
