# constructor.py
import os
import time
import pandas as pd
from solver import Eliptica, PROBLEMAS

def ms_time():
    return time.time() * 1000.0  # milisegundos

def main():
    # Estructura de carpetas
    root_out = "resultados"
    os.makedirs(root_out, exist_ok=True)

    # Parámetros: 2 tamaños de malla y 3 regiones -> 6 ejecuciones por problema
    # Ajusta estos valores a lo que quieras experimentar.
    mesh_sizes = [20, 40]   # dos tamaños de malla (m=n)
    regions = [
        (0.1, 0.6, 0.1, 0.6),   # region 1
        (0.0, 1.0, 0.0, 1.0),   # region 2
        (1.0, 2.0, 1.0, 2.0)    # region 3
    ]

    tiempos = []  # lista para guardar tiempos por ejecución

    for (f, g, sol, tag) in PROBLEMAS:
        carpeta_prob = os.path.join(root_out, tag)
        os.makedirs(carpeta_prob, exist_ok=True)

        for (a, b, c, d) in regions:
            region_id = f"a{a}_b{b}_c{c}_d{d}".replace('.', 'p')
            for m in mesh_sizes:
                n = m
                # nombre archivo con metadatos
                filename = f"{tag}_reg_{region_id}_m{m}_n{n}.dat"
                filepath = os.path.join(carpeta_prob, filename)

                t0 = ms_time()
                df = Eliptica(m, n, a, b, c, d, f, g, sol)
                t1 = ms_time()

                # guardar df en archivo .dat con tab separado
                df.to_csv(filepath, index=False, sep="\t", float_format="%.10e")
                elapsed_ms = t1 - t0

                print(f"Guardado: {filepath}  (tiempo = {elapsed_ms:.2f} ms)")

                tiempos.append({
                    "problema": tag,
                    "region": region_id,
                    "a": a, "b": b, "c": c, "d": d,
                    "m": m, "n": n,
                    "tiempo_ms": elapsed_ms,
                    "archivo": filepath
                })

    # Guardar tiempos en archivo resumen .dat (tab-separated)
    tiempos_df = pd.DataFrame(tiempos)
    tiempos_df.to_csv(os.path.join(root_out, "tiempos_ejecucion.dat"), index=False, sep="\t", float_format="%.6f")
    print(f"\nTiempos guardados en {os.path.join(root_out, 'tiempos_ejecucion.dat')}")

if __name__ == "__main__":
    main()
