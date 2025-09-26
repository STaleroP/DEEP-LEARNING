# graficador.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Definiciones
MALLAS = [5, 10, 20, 50, 100]
MALLA_MAXIMA = MALLAS[-1] # 100
NUM_PROBLEMAS = 4
RUTA_BASE = "resultados"
RUTA_GRAFICOS = "graficos"
TIEMPOS_FILE = os.path.join(RUTA_BASE, "tiempos_ejecucion.dat")

def setup_directorios_graficos():
    """Crea la estructura de carpetas de gráficos."""
    os.makedirs(RUTA_GRAFICOS, exist_ok=True)
    for p_id in range(1, NUM_PROBLEMAS + 1):
        os.makedirs(os.path.join(RUTA_GRAFICOS, f"problema_{p_id}"), exist_ok=True)

def graficar_tiempos():
    """Genera la gráfica de comparación 2D de Tiempos de Ejecución vs. Tamaño de Malla."""
    print("Generando gráfica de tiempos de ejecución...")

    try:
        # La primera columna es el índice (Malla)
        tiempos_df = pd.read_csv(TIEMPOS_FILE, sep='\t', index_col=0)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de tiempos en {TIEMPOS_FILE}. Ejecute constructor.py primero.")
        return

    malla_labels = [f"{N}x{N}" for N in MALLAS]
    malla_size = np.array(MALLAS)

    plt.figure(figsize=(10, 6))

    for p_id in range(1, NUM_PROBLEMAS + 1):
        col_name = f"P{p_id}"
        plt.plot(malla_size, tiempos_df[col_name].values, marker='o', label=f'Problema {p_id}')

    plt.title('Tiempos de Ejecución vs. Tamaño de Malla (Método de Diferencias Finitas)')
    plt.xlabel('Tamaño de Malla N (NxN)')
    plt.ylabel('Tiempo de Ejecución (ms)')
    plt.xticks(malla_size, malla_labels)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()

    filepath = os.path.join(RUTA_GRAFICOS, "tiempos_ejecucion_comparacion.png")
    plt.savefig(filepath)
    plt.close()
    print(f"Gráfica de tiempos guardada en: {filepath}")

def graficar_resultados_3d():
    """Genera las gráficas 3D de Solución Numérica y Analítica para la malla máxima."""
    print(f"\nGenerando gráficas 3D para la malla máxima ({MALLA_MAXIMA}x{MALLA_MAXIMA})...")

    for p_id in range(1, NUM_PROBLEMAS + 1):
        print(f"  Procesando Problema {p_id}...")

        # Ruta del archivo de resultados de la malla máxima
        carpeta = os.path.join(RUTA_BASE, f"problema_{p_id}", f"{MALLA_MAXIMA}x{MALLA_MAXIMA}")
        filepath = os.path.join(carpeta, f"resultados_{MALLA_MAXIMA}x{MALLA_MAXIMA}.dat")

        try:
            # Los archivos .dat usan tabulador como separador
            df = pd.read_csv(filepath, sep='\t')
        except FileNotFoundError:
            print(f"    Error: Archivo de datos no encontrado para el Problema {p_id}. Saltando.")
            continue

        # Preparar los datos para la gráfica 3D (grilla)
        # N es el número total de intervalos, N-1 es el número de puntos interiores en una dirección
        N_pts = MALLA_MAXIMA - 1
        X = df['x'].values.reshape(N_pts, N_pts)
        Y = df['y'].values.reshape(N_pts, N_pts)

        V_num = df['V_num'].values.reshape(N_pts, N_pts)
        V_ana = df['V_ana'].values.reshape(N_pts, N_pts)

        # Generar Gráfica 3D 1: Solución Numérica
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, V_num, cmap='viridis', edgecolor='none')
        ax.set_title(f'P{p_id}: Solución Numérica (MDF, {MALLA_MAXIMA}x{MALLA_MAXIMA})')
        ax.set_xlabel('Coordenada X')
        ax.set_ylabel('Coordenada Y')
        ax.set_zlabel('V Numérica')

        grafico_path = os.path.join(RUTA_GRAFICOS, f"problema_{p_id}", f"P{p_id}_V_Num_{MALLA_MAXIMA}x{MALLA_MAXIMA}.png")
        plt.savefig(grafico_path)
        plt.close(fig)
        print(f"    Guardado V Numérica en: {grafico_path}")

        # Generar Gráfica 3D 2: Solución Analítica
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, V_ana, cmap='plasma', edgecolor='none')
        ax.set_title(f'P{p_id}: Solución Analítica ({MALLA_MAXIMA}x{MALLA_MAXIMA})')
        ax.set_xlabel('Coordenada X')
        ax.set_ylabel('Coordenada Y')
        ax.set_zlabel('V Analítica')

        grafico_path = os.path.join(RUTA_GRAFICOS, f"problema_{p_id}", f"P{p_id}_V_Ana_{MALLA_MAXIMA}x{MALLA_MAXIMA}.png")
        plt.savefig(grafico_path)
        plt.close(fig)
        print(f"    Guardado V Analítica en: {grafico_path}")


def main():
    setup_directorios_graficos()
    graficar_tiempos()
    graficar_resultados_3d()
    print("\nVisualización completa. Gráficas guardadas en la carpeta 'graficos'.")

if __name__ == "__main__":
    main()