import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Cargar datos: columnas x, y, phi, vxy
data = np.loadtxt("data_poisson")

x = data[:,0]
y = data[:,1]
phi = data[:,2]
vxy = data[:,3]

# Crear la malla
nx = len(np.unique(x))
ny = len(np.unique(y))
X = x.reshape((nx, ny))
Y = y.reshape((nx, ny))
Phi = phi.reshape((nx, ny))
Vxy = vxy.reshape((nx, ny))

# Graficar solucion numerica
fig = plt.figure(figsize=(12,5))

ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(X, Y, Phi, cmap="viridis")
ax1.set_title("Solución Numérica")
ax1.set_xlabel("x (m)")
ax1.set_ylabel("y (m)")
ax1.set_zlabel("Potencial (V)")

# Graficar solucion analítica
ax2 = fig.add_subplot(122, projection='3d')
ax2.plot_surface(X, Y, Vxy, cmap="plasma")
ax2.set_title("Solución Analítica")
ax2.set_xlabel("x (m)")
ax2.set_ylabel("y (m)")
ax2.set_zlabel("Potencial (V)")

plt.tight_layout()
plt.show()
