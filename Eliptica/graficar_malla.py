# graficador_mallas.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- Configuraciones ---
MALLAS = [5, 10, 20, 50, 100]
NUM_PROBLEMAS = 4
RUTA_BASE = "resultados"
RUTA_GRAFICOS = "graficos"
COMPARACION_MALLAS_DIR = os.path.join(RUTA_GRAFICOS, "comparacion_mallas")

def setup_directorios_comparacion():
    """Crea la carpeta para las gráficas de comparación de mallas."""
    os.makedirs(COMPARACION_MALLAS_DIR, exist_ok=True)

def graficar_mallas_comparacion():
    """
    Genera un único plot con subgráficas 3D para comparar la solución numérica
    en las diferentes mallas para cada problema.
    """
    print("\nGenerando gráficas de comparación de mallas (3D)...")

    setup_directorios_comparacion()

    # Iterar sobre cada problema
    for p_id in range(1, NUM_PROBLEMAS + 1):
        print(f"  Procesando Problema {p_id}...")

        # 5 mallas -> 5 subgráficas. Usamos 1 fila y 5 columnas para que sea legible.
        fig = plt.figure(figsize=(25, 6))
        fig.suptitle(f'Problema {p_id}: Convergencia de la Solución Numérica (MDF)', fontsize=16)

        datos_cargados = True

        # Iterar sobre cada tamaño de malla
        for idx, N in enumerate(MALLAS):
            N_label = f"{N}x{N}"

            # Construir la ruta al archivo
            carpeta = os.path.join(RUTA_BASE, f"problema_{p_id}", N_label)
            filepath = os.path.join(carpeta, f"resultados_{N}x{N}.dat")

            try:
                # Cargar datos
                df = pd.read_csv(filepath, sep='\t')
            except FileNotFoundError:
                print(f"    Advertencia: Archivo de datos no encontrado para P{p_id}, Malla {N_label}. Saltando.")
                datos_cargados = False
                continue

            # Preparar datos 3D
            N_pts = N - 1 # Número de puntos interiores

            # Asegurarse de que el número de puntos sea consistente
            if len(df) != N_pts * N_pts:
                print(f"    Error de datos: El número de filas en {N_label} no coincide con el esperado.")
                datos_cargados = False
                continue

            # Remodelar las coordenadas y la solución
            X = df['x'].values.reshape(N_pts, N_pts)
            Y = df['y'].values.reshape(N_pts, N_pts)
            V_num = df['V_num'].values.reshape(N_pts, N_pts)

            # Crear el subplot 3D
            ax = fig.add_subplot(1, 5, idx + 1, projection='3d')

            # Graficar la superficie
            surf = ax.plot_surface(X, Y, V_num, cmap='viridis', edgecolor='none')

            # Configuración de ejes y título
            ax.set_title(f'{N_label}', fontsize=12)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')

            # Para evitar que el eje Z cambie drásticamente entre plots, se puede fijar el rango
            # Si no se fija, matplotlib ajustará el rango a los datos de cada subplot

        if datos_cargados:
            # Ajustar layout y guardar la figura
            plt.tight_layout(rect=[0, 0, 1, 0.95]) # Deja espacio para el suptitle

            filepath_guardar = os.path.join(COMPARACION_MALLAS_DIR, f"P{p_id}_Mallas_Comparacion.png")
            plt.savefig(filepath_guardar)
            plt.close(fig)
            print(f"  Gráfica de comparación guardada para P{p_id} en: {filepath_guardar}")
        else:
            plt.close(fig)

    print("\nGeneración de gráficas de mallas completa.")


if __name__ == "__main__":
    graficar_mallas_comparacion()