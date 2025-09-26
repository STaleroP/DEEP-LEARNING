import os
import pandas as pd
import matplotlib.pyplot as plt

def cargar_datos(filepath):
    """
    Intenta leer un archivo .dat separado por tabulador o coma.
    Normaliza los nombres de columnas.
    """
    try:
        data = pd.read_csv(filepath, sep="\t")
        if len(data.columns) == 1:  # si no se separó bien
            data = pd.read_csv(filepath, sep=",")
    except Exception:
        data = pd.read_csv(filepath, sep=",")

    # Normalizar nombres de columnas (sin espacios ni mayúsculas)
    data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_")

    return data


def graficar_numerico(filepath, outdir, show=False, save=True):
    data = cargar_datos(filepath)

    print(f"Archivo leído: {filepath}")
    print("Columnas:", data.columns.tolist())

    if not {"x", "y", "u"}.issubset(data.columns):
        raise ValueError(
            f"El archivo {filepath} no tiene las columnas necesarias. "
            f"Columnas reales: {data.columns}"
        )

    x, y, u = data["x"], data["y"], data["u"]

    plt.figure(figsize=(6, 5))
    sc = plt.scatter(x, y, c=u, cmap="viridis")
    plt.colorbar(sc, label="u (numérico)")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(f"Distribución numérica: {os.path.basename(filepath)}")

    if save:
        os.makedirs(outdir, exist_ok=True)
        outfile = os.path.join(
            outdir, os.path.basename(filepath).replace(".dat", ".png")
        )
        plt.savefig(outfile, dpi=300)
        print(f"✅ Gráfico guardado en {outfile}")

    if show:
        plt.show()

    plt.close()


def procesar_todo(indir="resultados", outdir="numerico"):
    """
    Procesa todos los .dat en la carpeta resultados y
    los guarda en numerico/problema_X
    """
    for root, _, files in os.walk(indir):
        for file in files:
            if file.endswith(".dat"):
                filepath = os.path.join(root, file)
                # nombre del problema = carpeta padre
                problema = os.path.basename(root)
                outdir_problema = os.path.join(outdir, problema)
                graficar_numerico(filepath, outdir_problema)


if __name__ == "__main__":
    procesar_todo()
