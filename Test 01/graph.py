import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd

# --- Parámetros del dominio (deben coincidir en los tres códigos)
L = 100.0

# --- Lectura Python (CSV)
wave_py = pd.read_csv("wave_py.csv")
times_py = wave_py["t"].values
x_py = np.arange(len(wave_py.columns) - 1) * (L / (len(wave_py.columns) - 1))
data_py = wave_py.iloc[:, 1:].values

# --- Lectura C++ (CSV)
wave_cpp = pd.read_csv("wave_cpp.csv")
times_cpp = wave_cpp["t"].values
x_cpp = np.arange(len(wave_cpp.columns) - 1) * (L / (len(wave_cpp.columns) - 1))
data_cpp = wave_cpp.iloc[:, 1:].values

# --- Lectura Fortran (BIN + meta) - CORREGIDO
meta = np.loadtxt("wave1d_meta.txt", dtype=int)
n_snap, nx = meta

# CORRECCIÓN: Usar order='F' para orden Fortran (column-major)
data_fortran_raw = np.fromfile("wave1d_fortran.bin", dtype=np.float64)
data_fortran = data_fortran_raw.reshape((n_snap, nx), order='F')

times_fortran = np.linspace(0, times_py[-1], n_snap)
x_fortran = np.linspace(0, L, nx)

# Verificación de dimensiones
print(f"Python: {data_py.shape}, C++: {data_cpp.shape}, Fortran: {data_fortran.shape}")
print(f"Fortran - Primer snapshot (debería ser ~sin(πx/L)):")
print(f"  Min: {data_fortran[0].min():.4f}, Max: {data_fortran[0].max():.4f}")
print(f"Python - Primer snapshot:")
print(f"  Min: {data_py[0].min():.4f}, Max: {data_py[0].max():.4f}")

# --- Configuración de la figura
fig, ax = plt.subplots(figsize=(8, 5))
line_py, = ax.plot([], [], label="Python", lw=2)
line_cpp, = ax.plot([], [], label="C++", lw=2)
line_f,  = ax.plot([], [], label="Fortran", lw=2)
ax.set_xlim(0, L)
ax.set_ylim(-1.1, 1.1)
ax.set_xlabel("x")
ax.set_ylabel("u(x,t)")
ax.legend()
ax.set_title("Comparación Ecuación de Onda 1D - Diferentes Implementaciones")

# --- Animación
def init():
    line_py.set_data([], [])
    line_cpp.set_data([], [])
    line_f.set_data([], [])
    return line_py, line_cpp, line_f

def update(frame):
    i_py = min(frame, len(data_py) - 1)
    i_cpp = min(frame, len(data_cpp) - 1)
    i_f = min(frame, len(data_fortran) - 1)
    line_py.set_data(x_py, data_py[i_py])
    line_cpp.set_data(x_cpp, data_cpp[i_cpp])
    line_f.set_data(x_fortran, data_fortran[i_f])
    ax.set_title(f"Evolución temporal (frame={frame})")
    return line_py, line_cpp, line_f

anim = FuncAnimation(fig, update, frames=min(len(data_py), len(data_cpp), len(data_fortran)),
                     init_func=init, blit=True, interval=40)

plt.tight_layout()
plt.show()