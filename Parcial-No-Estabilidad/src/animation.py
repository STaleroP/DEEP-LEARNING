import sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Leer argumentos
if len(sys.argv) < 2:
    print("Uso: python3 animate_wave.py <carpeta_de_resultados>")
    print("Ejemplo: python3 animate_wave.py results/Python/m_400/")
    sys.exit(1)

folder = sys.argv[1]
if not os.path.isdir(folder):
    sys.exit(f"Error: no existe la carpeta '{folder}'")

# Buscar el archivo de snapshots (wave_*.csv)
csv_files = [f for f in os.listdir(folder) if f.startswith("wave_") and f.endswith(".csv")]
if not csv_files:
    sys.exit("No se encontró archivo wave_*.csv en la carpeta.")
csv_path = os.path.join(folder, csv_files[0])

print(f"Leyendo datos desde: {csv_path}")
df = pd.read_csv(csv_path)
times = df["t"].values
x = np.arange(len(df.columns) - 1)  # índice espacial (x0, x1, ...)
u_data = df.iloc[:, 1:].values

# Intentar reconstruir el dominio espacial real
L = 100.0
m = len(x) - 1
x_phys = np.linspace(0, L, m + 1)

# Configurar animación
fig, ax = plt.subplots(figsize=(8, 4))
line, = ax.plot([], [], lw=2)
ax.set_xlim(0, L)
ax.set_ylim(-1.1, 1.1)
ax.set_xlabel("x")
ax.set_ylabel("u(x, t)")
ax.set_title(f"Evolución de la onda")

# función de inicialización
def init():
    line.set_data([], [])
    return line,

# función de actualización (por frame)
def update(frame):
    line.set_data(x_phys, u_data[frame])
    ax.set_title(f"{os.path.basename(folder)} | t = {times[frame]:.3f}")
    return line,

# número total de frames
nframes = len(times)
interval = 30  # ms entre frames → ~33 fps

anim = FuncAnimation(fig, update, frames=nframes,
                     init_func=init, blit=True, interval=interval)

plt.tight_layout()
plt.show()
