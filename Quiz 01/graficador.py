# graficador.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

ROOT_DATOS = "resultados"
ROOT_GRAF = "graficos"
os.makedirs(ROOT_GRAF, exist_ok=True)

def graficar_tiempos(tiempos_path, outpath):
    df = pd.read_csv(tiempos_path, sep="\t")
    # convertir m a numeric si no lo está
    df["m"] = pd.to_numeric(df["m"])
    df["tiempo_ms"] = pd.to_numeric(df["tiempo_ms"])

    plt.figure(figsize=(8,6))
    for prob in df["problema"].unique():
        sub = df[df["problema"] == prob].sort_values("m")
        # graficar promedio por m si hay varias regiones con mismo m
        grouped = sub.groupby("m")["tiempo_ms"].mean().reset_index()
        plt.plot(grouped["m"], grouped["tiempo_ms"], marker="o", label=prob)

    plt.xlabel("Tamaño de malla (m = n)")
    plt.ylabel("Tiempo de ejecución [ms]")
    plt.title("Tiempo de ejecución vs Tamaño de malla (promedio sobre regiones)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    print(f"Gráfica de tiempos guardada en {outpath}")
    plt.close()

def crear_directorios_problemas():
    for prob in os.listdir(ROOT_DATOS):
        prob_path = os.path.join(ROOT_DATOS, prob)
        if os.path.isdir(prob_path):
            out_dir = os.path.join(ROOT_GRAF, prob)
            os.makedirs(out_dir, exist_ok=True)

def elegir_mayor_malla_archivo(problema_folder):
    """
    Escoge el archivo con mayor valor m (si hay empate, toma el primero)
    """
    files = [f for f in os.listdir(problema_folder) if f.endswith(".dat")]
    best_file = None
    best_m = -1
    for f in files:
        df = pd.read_csv(os.path.join(problema_folder, f), sep="\t", nrows=1)
        # m puede venir como float o int en la columna
        if "m" in df.columns:
            mval = int(df["m"].iloc[0])
            if mval > best_m:
                best_m = mval
                best_file = f
    return best_file

def graficar_3d_desde_dat(datpath, outdir, prefijo):
    """
    Lee el archivo .dat y grafica superficie 3D de u_num y u_exacta (dos archivos png).
    Se asume que en .dat hay columnas x,y,u_num,u_exacta,m,n,a,b,c,d
    """
    df = pd.read_csv(datpath, sep="\t")
    # recuperar x,y,u_num,u_exacta
    x = df["x"].values
    y = df["y"].values
    z_num = df["u_num"].values
    z_ex = df["u_exacta"].values

    # crear grid regular a partir de puntos (x,y)
    # tomamos valores únicos ordenados
    xu = np.unique(np.round(x, 12))
    yu = np.unique(np.round(y, 12))
    xu.sort()
    yu.sort()

    try:
        Xg, Yg = np.meshgrid(xu, yu)
        # pivot para transformar a matriz
        df_p = df.copy()
        # rounding to avoid floating mismatches as keys
        df_p["x_r"] = np.round(df_p["x"], 12)
        df_p["y_r"] = np.round(df_p["y"], 12)
        pivot_num = df_p.pivot_table(index="y_r", columns="x_r", values="u_num")
        pivot_ex = df_p.pivot_table(index="y_r", columns="x_r", values="u_exacta")
        Znum = pivot_num.values
        Zex = pivot_ex.values
    except Exception as e:
        print(f"Error al pivotear el archivo {datpath}: {e}")
        # intentar usar triangulación (tricontourf) no requiere rejilla
        Znum = None
        Zex = None

    # graficar superficie numérica
    out_num = os.path.join(outdir, f"{prefijo}_u_num.png")
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, projection='3d')
    if Znum is not None:
        ax.plot_surface(Xg, Yg, Znum, cmap=cm.viridis, linewidth=0, antialiased=True)
    else:
        ax.plot_trisurf(x, y, z_num, cmap=cm.viridis, linewidth=0.2)
    ax.set_title(f"{prefijo} - Solución Numérica")
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("u_num")
    plt.tight_layout()
    plt.savefig(out_num, dpi=200)
    plt.close()
    print(f"Guardada 3D numérica en {out_num}")

    # graficar superficie analítica
    out_ex = os.path.join(outdir, f"{prefijo}_u_exacta.png")
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, projection='3d')
    if Zex is not None:
        ax.plot_surface(Xg, Yg, Zex, cmap=cm.viridis, linewidth=0, antialiased=True)
    else:
        ax.plot_trisurf(x, y, z_ex, cmap=cm.viridis, linewidth=0.2)
    ax.set_title(f"{prefijo} - Solución Analítica")
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("u_exacta")
    plt.tight_layout()
    plt.savefig(out_ex, dpi=200)
    plt.close()
    print(f"Guardada 3D analítica en {out_ex}")

def main():
    # 1) Graficar tiempos: usamos el archivo de tiempos en resultados/
    tiempos_path = os.path.join(ROOT_DATOS, "tiempos_ejecucion.dat")
    if not os.path.exists(tiempos_path):
        raise FileNotFoundError(f"No encuentro {tiempos_path}. Ejecuta primero constructor.py")

    os.makedirs(ROOT_GRAF, exist_ok=True)
    graficar_tiempos(tiempos_path, os.path.join(ROOT_GRAF, "tiempos_vs_malla.png"))

    # 2) Crear carpetas por problema en graficos/
    crear_directorios_problemas()

    # 3) Para cada problema elegir el archivo con mayor m y graficar 3D
    for prob in os.listdir(ROOT_DATOS):
        prob_path = os.path.join(ROOT_DATOS, prob)
        if not os.path.isdir(prob_path):
            continue
        best_file = elegir_mayor_malla_archivo(prob_path)
        if best_file is None:
            print(f"No se encontraron .dat en {prob_path}")
            continue
        datpath = os.path.join(prob_path, best_file)
        outdir = os.path.join(ROOT_GRAF, prob)
        os.makedirs(outdir, exist_ok=True)
        prefijo = os.path.splitext(best_file)[0]
        print(f"Para {prob} seleccionando mayor m: {best_file}")
        graficar_3d_desde_dat(datpath, outdir, prefijo)

if __name__ == "__main__":
    main()
