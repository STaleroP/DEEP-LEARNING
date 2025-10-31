# solver.py
import numpy as np
import pandas as pd
import math
from scipy.sparse import lil_matrix, linalg

def solve_pde_fourier(m, n, a, b, c, d, f, g, sol_exacta):
    """
    Resuelve la EDP Elíptica bidimensional (Laplace o Poisson) usando el Método de Diferencias Finitas (MDF).

    Args:
        m: (int) Número de intervalos en y (filas internas).
        n: (int) Número de intervalos en x (columnas internas).
        a, b, c, d: (float) Extremos del dominio [a, b] x [c, d].
        f: (fun) Función del lado derecho f(x, y) de la EDP.
        g: (fun) Función para las Condiciones de Frontera g(x, y).
        sol_exacta: (fun) Función para la Solución Analítica exacta V(x, y).

    Returns:
        pd.DataFrame: Con columnas 'x', 'y', 'V_num', 'V_ana', 'error_abs', 'error_rel'.
    """

    # Número de puntos interiores: (n-1) en x, (m-1) en y.
    num_puntos_x = n - 1
    num_puntos_y = m - 1
    total_incognitas = num_puntos_x * num_puntos_y

    h = (b - a) / n  # Paso en x
    k = (d - c) / m  # Paso en y

    # Generación de coordenadas de los puntos interiores
    x = np.array([a + i * h for i in range(1, n)]) # n-1 puntos
    y = np.array([c + j * k for j in range(1, m)]) # m-1 puntos

    # Constantes
    Lambda = (h / k)**2
    mu = 2 * (1 + Lambda)

    # Inicialización de matriz dispersa y vector B
    A = lil_matrix((total_incognitas, total_incognitas))
    B = np.zeros(total_incognitas)

    # Llenado de la matriz A y el vector B
    for l in range(total_incognitas):
        # Indice i (en x, 1 a n-1) y j (en y, 1 a m-1) del punto (x_i, y_j)
        # La indexación va de 1 a n-1 para x, y de 1 a m-1 para y.
        # Usamos el mapeo k -> (i, j) donde k es el índice en el sistema lineal (0-based)
        # y i, j son los índices de la cuadrícula (1-based).
        i = (l % num_puntos_x) + 1  # 1-based index for x
        j = (l // num_puntos_x) + 1  # 1-based index for y

        # Coordenadas reales
        xi = x[i - 1]
        yj = y[j - 1]

        # Lado derecho B
        B[l] = -h**2 * f(xi, yj)

        # Diagonal principal
        A[l, l] = mu

        # Vecinos en x (i-1 y i+1)
        if i > 1:
            A[l, l - 1] = -1
        if i < num_puntos_x:
            A[l, l + 1] = -1

        # Vecinos en y (j-1 y j+1)
        if j > 1:
            A[l, l - num_puntos_x] = -Lambda
        if j < num_puntos_y:
            A[l, l + num_puntos_x] = -Lambda

        # Condiciones de frontera (suma al vector B)
        # Borde izquierdo (i=1, x=a)
        if i == 1:
            B[l] += g(a, yj)
        # Borde derecho (i=n-1, x=b)
        if i == num_puntos_x:
            B[l] += g(b, yj)
        # Borde inferior (j=1, y=c)
        if j == 1:
            B[l] += Lambda * g(xi, c)
        # Borde superior (j=m-1, y=d)
        if j == num_puntos_y:
            B[l] += Lambda * g(xi, d)

    # Solución del sistema lineal
    V_num = linalg.spsolve(A.tocsr(), B)

    # Cálculo de la solución analítica y el error
    V_ana = np.array([sol_exacta(x[i - 1], y[j - 1])
                      for j in range(1, m)
                      for i in range(1, n)])

    error_abs = np.abs(V_ana - V_num)
    error_rel = error_abs / np.abs(V_ana)
    error_rel[np.isinf(error_rel)] = 0 # Manejo de posible división por cero o valor muy pequeño
    error_rel[np.isnan(error_rel)] = 0

    # Crear DataFrame de resultados
    X_coords = np.array([x[i - 1] for j in range(1, m) for i in range(1, n)])
    Y_coords = np.array([y[j - 1] for j in range(1, m) for i in range(1, n)])

    resultados = pd.DataFrame({
        "x": X_coords,
        "y": Y_coords,
        "V_num": V_num,
        "V_ana": V_ana,
        "error_abs": error_abs,
        "error_rel": error_rel
    })

    return resultados


# --- Definiciones de Problemas ---

# Problema 1: V(x, y) = exp(xy)
def run_problema_1(N):
    a, b = 0.0, 2.0  # Dominio x
    c, d = 0.0, 2.0  # Dominio y
    m, n = N, N

    # Solución Analítica
    def V_ana(x, y):
        return np.exp(x * y)

    # Lado Derecho f(x, y) = (x^2 + y^2) * exp(xy)
    def f(x, y):
        return (x**2 + y**2) * np.exp(x * y)

    # Condiciones de Frontera g(x, y)
    def g(x, y):
        if x == a: return 1.0  # V(0, y) = e^(0) = 1
        if x == b: return np.exp(2 * y) # V(2, y) = e^(2y)
        if y == c: return 1.0  # V(x, 0) = e^(0) = 1
        if y == d: return np.exp(2 * x) # V(x, 2) = e^(2x)
        return 0 # Caso general, no debería ocurrir en los bordes

    return solve_pde_fourier(m, n, a, b, c, d, f, g, V_ana)


# Problema 2: V(x, y) = ln(y^2 + x^2)
def run_problema_2(N):
    a, b = 1.0, 2.0
    c, d = 0.0, 2.0
    m, n = N, N

    def V_ana(x, y):
        return np.log(y**2 + x**2)

    # Lado Derecho f(x, y) = 0 (Laplace)
    def f(x, y):
        return 0.0

    # Condiciones de Frontera g(x, y)
    def g(x, y):
        if x == a: return np.log(y**2 + 1**2) # V(1, y) = ln(y^2+1)
        if x == b: return np.log(y**2 + 2**2) # V(2, y) = ln(y^2+4)
        if y == c: return np.log(0**2 + x**2) # V(x, 0) = 2*ln(x) = ln(x^2)
        if y == d: return np.log(2**2 + x**2) # V(x, 2) = ln(4+x^2)
        return 0

    return solve_pde_fourier(m, n, a, b, c, d, f, g, V_ana)


# Problema 3: V(x, y) = (x - y)^2
def run_problema_3(N):
    a, b = 1.0, 2.0
    c, d = 0.0, 2.0
    m, n = N, N

    def V_ana(x, y):
        return (x - y)**2

    # Lado Derecho f(x, y) = 4 (Poisson)
    def f(x, y):
        return 4.0

    # Condiciones de Frontera g(x, y)
    def g(x, y):
        if x == a: return (1 - y)**2 # V(1, y)
        if x == b: return (2 - y)**2 # V(2, y)
        if y == c: return (x - 0)**2 # V(x, 0) = x^2
        if y == d: return (x - 2)**2 # V(x, 2) = (x-2)^2
        return 0

    return solve_pde_fourier(m, n, a, b, c, d, f, g, V_ana)


# Problema 4: V(x, y) = xy * ln(yx)
def run_problema_4(N):
    a, b = 1.0, 2.0
    c, d = 1.0, 2.0
    m, n = N, N

    def V_ana(x, y):
        return x * y * np.log(x * y)

    # Lado Derecho f(x, y) = x/y + y/x
    def f(x, y):
        return x / y + y / x

    # Condiciones de Frontera g(x, y)
    def g(x, y):
        if x == a: return 1 * y * np.log(1 * y) # V(1, y) = y*ln(y)
        if x == b: return 2 * y * np.log(2 * y) # V(2, y) = 2y*ln(2y)
        if y == c: return x * 1 * np.log(x * 1) # V(x, 1) = x*ln(x)
        if y == d: return x * 2 * np.log(x * 2) # V(x, 2) = 2x*ln(2x)
        return 0

    return solve_pde_fourier(m, n, a, b, c, d, f, g, V_ana)

# Diccionario de problemas para el constructor
PROBLEMS = {
    1: run_problema_1,
    2: run_problema_2,
    3: run_problema_3,
    4: run_problema_4
}