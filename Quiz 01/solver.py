# solver.py
import numpy as np
import pandas as pd
import math
import os

def Eliptica(m, n, a, b, c, d, f, g, sol_exacta):
    """
    Método de diferencias finitas para la ecuación de Poisson en un rectángulo [a,b]x[c,d].
    Devuelve un DataFrame con columnas x,y,u_num,u_exacta,error_abs,error_rel
    y añade metadatos repetidos m,n,a,b,c,d para facilitar reconstrucción.
    """

    # pasos
    h = (b - a) / n
    k = (d - c) / m

    # puntos internos (excluimos fronteras)
    x_in = np.array([a + (i + 1) * h for i in range(n)])      # len n
    y_in = np.array([c + (j + 1) * k for j in range(m)])      # len m

    Lambda = (h**2) / (k**2)
    mu = 2 * (1 + Lambda)

    N_unknowns = (n - 1) * (m - 1)
    A = np.zeros((N_unknowns, N_unknowns))
    B = np.zeros(N_unknowns)

    # ensamblado matrix A y vector B (notación adaptada a tu implementacion)
    for l in range(1, N_unknowns + 1):
        # recuperar i,j desde l
        i = l - (math.ceil(l / (n - 1)) - 1) * (n - 1)
        j = m - math.ceil(l / (n - 1))

        xi = x_in[i - 1]
        yj = y_in[j - 1]

        B[l - 1] = - (h**2) * f(xi, yj)
        A[l - 1, l - 1] = mu

        # vecino izquierda
        if (i - 1) >= 1:
            A[l - 1, l - 2] = -1
        # vecino derecha
        if (i + 1) <= n - 1:
            A[l - 1, l] = -1
        # vecino abajo (j-1)
        if (j - 1) >= 1:
            A[l - 1, l + (n - 1) - 1] = -Lambda
        # vecino arriba (j+1)
        if (j + 1) <= m - 1:
            A[l - 1, l - (n - 1) - 1] = -Lambda

        # condiciones de frontera (valores de g en las fronteras)
        if i == 1:
            B[l - 1] += g(a, yj)
        if i == n - 1:
            B[l - 1] += g(b, yj)
        if j == 1:
            B[l - 1] += Lambda * g(xi, c)
        if j == m - 1:
            B[l - 1] += Lambda * g(xi, d)

    # resolver sistema
    u_vec = np.linalg.solve(A, B)

    # construir arrays de salida en el mismo orden en que se guardará
    coor_x = np.zeros_like(u_vec, dtype=float)
    coor_y = np.zeros_like(u_vec, dtype=float)
    u_exacta = np.zeros_like(u_vec, dtype=float)
    err_abs = np.zeros_like(u_vec, dtype=float)
    err_rel = np.zeros_like(u_vec, dtype=float)

    idx = 0
    # recorrimos desde y = c+(m-1)*k down to ...  (igual que tu original)
    y_list = np.array([c + (d - c) / m * i for i in range(m - 1, 0, -1)])
    x_list = np.array([a + (b - a) / n * j for j in range(1, n)])

    for y0 in y_list:
        for x0 in x_list:
            coor_x[idx] = x0
            coor_y[idx] = y0
            u_e = sol_exacta(x0, y0)
            u_num = u_vec[idx]
            u_exacta[idx] = u_e
            err_abs[idx] = abs(u_e - u_num)
            # error relativo guardando nan si exacta es 0
            if abs(u_e) > 1e-16:
                err_rel[idx] = err_abs[idx] / abs(u_e)
            else:
                err_rel[idx] = np.nan
            idx += 1

    # DataFrame con metadatos repetidos para facilitar graficación
    df = pd.DataFrame({
        "x": coor_x,
        "y": coor_y,
        "u_num": u_vec,
        "u_exacta": u_exacta,
        "err_abs": err_abs,
        "err_rel": err_rel,
        "m": np.full_like(coor_x, m),
        "n": np.full_like(coor_x, n),
        "a": np.full_like(coor_x, a),
        "b": np.full_like(coor_x, b),
        "c": np.full_like(coor_x, c),
        "d": np.full_like(coor_x, d)
    })

    return df


# =========================
# Definición de los 4 problemas
# Cada problema define f,g y sol_exacta
# =========================

# Problema 1: ∇^2 φ = (x^2 + y^2) e^{xy}   con condiciones de frontera V(a,y)=..., etc.
def f1(x, y):
    return (x**2 + y**2) * np.exp(x*y)

def g1(x, y):
    # En la tabla las condiciones eran V(0,y)=1, V(2,y)=e^{2y}, V(x,0)=1, V(x,1)=e^x
    # Para ser consistentes con la solución exacta e^{xy} tomamos g = e^{xy} en frontera.
    return np.exp(x*y)

def sol1(x, y):
    return np.exp(x*y)

# Problema 2: Laplaciano 0, solución ln(y^2 + x^2)
def f2(x, y):
    return 0.0

def g2(x, y):
    # condición de frontera tomada según tabla: V(1,y) = ln(y^2+1) etc.
    # devolvemos ln(x^2 + y^2) por consistencia
    val = x**2 + y**2
    # evitar log(0)
    return np.log(val + 1e-16)

def sol2(x, y):
    return np.log(x**2 + y**2 + 1e-16)

# Problema 3: ∇^2 φ = 4, solución (x - y)^2
def f3(x, y):
    return 4.0

def g3(x, y):
    # condición frontera acorde con solución (x-y)^2
    return (x - y)**2

def sol3(x, y):
    return (x - y)**2

# Problema 4: ∇^2 φ = x/y + y/x, solución x*y*ln(x*y)
def f4(x, y):
    # cuidado con division by zero: domains must avoid x=0,y=0
    return (x / y) + (y / x)

def g4(x, y):
    return x * y * np.log(x * y + 1e-16)

def sol4(x, y):
    return x * y * np.log(x * y + 1e-16)


# Exportar problemas en una lista para que constructor.py los importe fácilmente
PROBLEMAS = [
    (f1, g1, sol1, "problema_1"),
    (f2, g2, sol2, "problema_2"),
    (f3, g3, sol3, "problema_3"),
    (f4, g4, sol4, "problema_4"),
]

if __name__ == "__main__":
    # prueba rápida (si se ejecuta solo)
    os.makedirs("resultados", exist_ok=True)
    df = Eliptica(6, 6, 0.1, 0.6, 0.1, 0.6, f3, g3, sol3)
    print(df.head())
