# constructor.py
import os
import time
import pandas as pd
import numpy as np
from solver import PROBLEMS

# Definiciones
MALLAS = [5, 10, 20, 50, 100]
NUM_PROBLEMAS = 4
RUTA_BASE = "resultados"
TIEMPOS_FILE = os.path.join(RUTA_BASE, "tiempos_ejecucion.dat")

def setup_directorios():
    """Crea la estructura de carpetas de resultados."""
    if os.path.exists(RUTA_BASE):
        # Opcional: Limpiar o mover carpeta existente
        pass
    os.makedirs(RUTA_BASE, exist_ok=True)
    for p_id in range(1, NUM_PROBLEMAS + 1):
        for N in MALLAS:
            carpeta = os.path.join(RUTA_BASE, f"problema_{p_id}", f"{N}x{N}")
            os.makedirs(carpeta, exist_ok=True)

def guardar_resultados(df, p_id, N):
    """Guarda el DataFrame de resultados en el archivo .dat."""
    carpeta = os.path.join(RUTA_BASE, f"problema_{p_id}", f"{N}x{N}")
    filepath = os.path.join(carpeta, f"resultados_{N}x{N}.dat")

    # Formato de números cortos (cuatro cifras significativas)
    float_format = '%.4g'

    # Escribir el archivo
    with open(filepath, 'w') as f:
        # Escribir encabezados
        f.write(df.to_csv(index=False, sep='\t', header=True).split('\n')[0] + '\n')
        # Escribir datos formateados
        df.to_csv(f, index=False, sep='\t', header=False, float_format=float_format)

def ejecutar_simulacion():
    """Implementa el doble ciclo, mide el tiempo y guarda los datos."""
    print("Iniciando la simulación y generación de datos...")

    # Tabla para almacenar tiempos
    tiempos_data = {f"P{i}": [] for i in range(1, NUM_PROBLEMAS + 1)}
    tiempos_data["Malla"] = [f"{N}x{N}" for N in MALLAS]

    setup_directorios()

    for p_id in range(1, NUM_PROBLEMAS + 1):
        print(f"\n--- Procesando Problema {p_id} ---")
        run_func = PROBLEMS[p_id]

        for N in MALLAS:
            print(f"  Malla {N}x{N}...")

            # Medición de tiempo de ejecución
            start_time = time.perf_counter()
            resultados_df = run_func(N)
            end_time = time.perf_counter()

            tiempo_ms = (end_time - start_time) * 1000 # Tiempo en milisegundos
            tiempos_data[f"P{p_id}"].append(tiempo_ms)

            # Guardar resultados
            guardar_resultados(resultados_df, p_id, N)
            print(f"    Tiempo: {tiempo_ms:.2f} ms")


    # Guardar tabla de tiempos
    tiempos_df = pd.DataFrame(tiempos_data)
    tiempos_df = tiempos_df.set_index("Malla")

    # Formato de números cortos
    float_format = '%.4g'

    with open(TIEMPOS_FILE, 'w') as f:
        # Escribir encabezados
        f.write(tiempos_df.to_csv(sep='\t', header=True).split('\n')[0] + '\n')
        # Escribir datos formateados
        tiempos_df.to_csv(f, sep='\t', header=False, float_format=float_format)

    print(f"\nSimulación completa. Tiempos guardados en: {TIEMPOS_FILE}")
    print("Datos de resultados guardados en la carpeta 'resultados'.")

if __name__ == "__main__":
    ejecutar_simulacion()