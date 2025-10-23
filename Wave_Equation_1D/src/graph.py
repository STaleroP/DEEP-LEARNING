#!/usr/bin/env python3
"""
graph.py
Lee los resultados en results/{Python,Cpp,Fortran}/m_{m}/ y genera:
 - Gráfico de errores L2 a lo largo del tiempo para cada implementación
 - Gráfico de tiempos de cálculo vs m (log-log)
 - Gráfico de convergencia: L2 error final vs m (log-log)
 - Gráfico de rendimiento comparativo en porcentajes
"""
import os, glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

base = "results"
impls = {"Python":"Python", "Cpp":"Cpp", "Fortran":"Fortran"}
MS = sorted([int(os.path.basename(d).split('_')[1]) for d in glob.glob(os.path.join(base,"Python","m_*"))]) \
     if glob.glob(os.path.join(base,"Python","m_*")) else [100,200,400,800,1600]

# Coleccionar datos
timings = {"Python":[], "Cpp":[], "Fortran":[]}
errors_final = {"Python":[], "Cpp":[], "Fortran":[]}
errors_evolution = {"Python":{}, "Cpp":{}, "Fortran":{}}  # por cada m
speedup_data = []  # para guardar datos de rendimiento

print("="*60)
print("ANÁLISIS DE RESULTADOS")
print("="*60)

for m in MS:
    print(f"\n--- Procesando m = {m} ---")
    
    # Cargar datos de cada implementación
    for key, sub in impls.items():
        folder = os.path.join(base, sub, f"m_{m}")
        if not os.path.isdir(folder):
            print(f"  ⚠️  Missing {folder}")
            timings[key].append(np.nan)
            errors_final[key].append(np.nan)
            continue
        
        # Leer timing
        timing_file = os.path.join(folder, "timing.txt")
        if os.path.exists(timing_file):
            t_wall = float(open(timing_file).read().strip())
            timings[key].append(t_wall)
        else:
            timings[key].append(np.nan)
        
        # Leer errores
        errf = os.path.join(folder, "errors.csv")
        if os.path.exists(errf):
            edf = pd.read_csv(errf)
            # Limpiar espacios en nombres de columnas
            edf.columns = edf.columns.str.strip()
            errors_final[key].append(edf['L2'].values[-1])
            errors_evolution[key][m] = edf  # guardar toda la evolución
        else:
            errors_final[key].append(np.nan)

# Crear directorio de plots
os.makedirs("plots", exist_ok=True)

# =============================================================================
# GRÁFICO 1: Evolución temporal de errores L2 para cada m
# =============================================================================
print("\n" + "="*60)
print("Generando gráficos de evolución temporal de errores...")
print("="*60)

for m in MS:
    plt.figure(figsize=(10, 6))
    has_data = False
    
    for key in ['Python', 'Cpp', 'Fortran']:
        if m in errors_evolution[key]:
            df = errors_evolution[key][m]
            plt.plot(df['t'], df['L2'], marker='o', markersize=3, 
                    label=key, linewidth=2, alpha=0.8)
            has_data = True
    
    if has_data:
        plt.xlabel('Tiempo (s)', fontsize=12)
        plt.ylabel('Error L2', fontsize=12)
        plt.title(f'Evolución del Error L2 vs Tiempo (m={m})', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.yscale('log')
        plt.tight_layout()
        out = os.path.join("plots", f"error_evolution_m_{m}.png")
        plt.savefig(out, dpi=150)
        print(f"  ✓ Guardado: {out}")
        plt.close()

# =============================================================================
# GRÁFICO 2: Tiempos de cálculo vs m (log-log)
# =============================================================================
print("\n" + "="*60)
print("Generando gráfico de tiempos de cálculo vs m...")
print("="*60)

plt.figure(figsize=(10, 6))
colors = {'Python': '#3776ab', 'Cpp': '#00599C', 'Fortran': '#734f96'}
markers = {'Python': 'o', 'Cpp': 's', 'Fortran': '^'}

for key in ['Python', 'Cpp', 'Fortran']:
    ys = np.array(timings[key], dtype=float)
    valid_mask = ~np.isnan(ys)
    if np.any(valid_mask):
        plt.plot(np.array(MS)[valid_mask], ys[valid_mask], 
                marker=markers[key], markersize=8, label=key, 
                linewidth=2, color=colors[key])

plt.xscale('log')
plt.yscale('log')
plt.xlabel('Tamaño de malla m (log)', fontsize=12)
plt.ylabel('Tiempo de cálculo (s, log)', fontsize=12)
plt.title('Rendimiento: Tiempo de Cálculo vs Tamaño de Malla', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3, which='both')
plt.tight_layout()
plt.savefig("plots/timing_vs_m.png", dpi=150)
print("  ✓ Guardado: plots/timing_vs_m.png")
plt.close()

# =============================================================================
# GRÁFICO 3: Convergencia - Error L2 final vs m (log-log)
# =============================================================================
print("\n" + "="*60)
print("Generando gráfico de convergencia...")
print("="*60)

plt.figure(figsize=(10, 6))
for key in ['Python', 'Cpp', 'Fortran']:
    errs = np.array(errors_final[key], dtype=float)
    valid_mask = ~np.isnan(errs)
    if np.any(valid_mask):
        plt.plot(np.array(MS)[valid_mask], errs[valid_mask], 
                marker=markers[key], markersize=8, label=key, 
                linewidth=2, color=colors[key])

plt.xscale('log')
plt.yscale('log')
plt.xlabel('Tamaño de malla m (log)', fontsize=12)
plt.ylabel('Error L2 final (log)', fontsize=12)
plt.title('Convergencia: Error L2 Final vs Tamaño de Malla', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3, which='both')
plt.tight_layout()
plt.savefig("plots/error_vs_m.png", dpi=150)
print("  ✓ Guardado: plots/error_vs_m.png")
plt.close()

# =============================================================================
# GRÁFICO 4: Comparación de rendimiento en porcentajes
# =============================================================================
print("\n" + "="*60)
print("ANÁLISIS DE RENDIMIENTO COMPARATIVO")
print("="*60)

# Calcular speedups y guardar datos
for idx, m in enumerate(MS):
    tpy = timings['Python'][idx]
    tcpp = timings['Cpp'][idx]
    tfort = timings['Fortran'][idx]
    
    print(f"\nm = {m}:")
    print(f"  Python:  {tpy:.6f} s")
    print(f"  C++:     {tcpp:.6f} s")
    print(f"  Fortran: {tfort:.6f} s")
    
    # Filtrar valores válidos
    times_list = []
    if not np.isnan(tpy):
        times_list.append((tpy, 'Python'))
    if not np.isnan(tcpp):
        times_list.append((tcpp, 'C++'))
    if not np.isnan(tfort):
        times_list.append((tfort, 'Fortran'))
    
    if len(times_list) < 2:
        print("  ⚠️  Datos insuficientes para comparación")
        continue
    
    times_list.sort()
    fastest = times_list[0]
    slowest = times_list[-1]
    
    # Calcular porcentaje de ventaja
    advantage = (slowest[0] - fastest[0]) / slowest[0] * 100.0
    
    print(f"  → Más rápido: {fastest[1]} ({fastest[0]:.6f}s)")
    print(f"  → Más lento:  {slowest[1]} ({slowest[0]:.6f}s)")
    print(f"  → Ventaja:    {advantage:.2f}%")
    
    # Guardar datos para gráfico
    speedup_data.append({
        'm': m,
        'fastest': fastest[1],
        'slowest': slowest[1],
        'advantage': advantage,
        'fastest_time': fastest[0],
        'slowest_time': slowest[0]
    })
    
    # Calcular speedup relativo a Python (si disponible)
    if not np.isnan(tpy):
        if not np.isnan(tcpp):
            speedup_cpp = tpy / tcpp
            print(f"  → Speedup C++ vs Python:    {speedup_cpp:.2f}x")
        if not np.isnan(tfort):
            speedup_fort = tpy / tfort
            print(f"  → Speedup Fortran vs Python: {speedup_fort:.2f}x")

# Gráfico de barras de ventaja porcentual
if speedup_data:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Subplot 1: Ventaja porcentual
    ms_plot = [d['m'] for d in speedup_data]
    advantages = [d['advantage'] for d in speedup_data]
    colors_bar = ['green' if d['fastest'] != 'Python' else 'orange' for d in speedup_data]
    
    bars = ax1.bar(range(len(ms_plot)), advantages, color=colors_bar, alpha=0.7, edgecolor='black')
    ax1.set_xticks(range(len(ms_plot)))
    ax1.set_xticklabels([f"m={m}" for m in ms_plot])
    ax1.set_ylabel('Ventaja de rendimiento (%)', fontsize=12)
    ax1.set_title('Ventaja Porcentual: (Más Lento - Más Rápido) / Más Lento × 100%', 
                  fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Añadir etiquetas a las barras
    for i, (bar, d) in enumerate(zip(bars, speedup_data)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%\n({d["fastest"]} vs {d["slowest"]})',
                ha='center', va='bottom', fontsize=9)
    
    # Subplot 2: Speedup relativo a Python
    ax2_data = {'m': [], 'cpp_speedup': [], 'fort_speedup': []}
    for idx, m in enumerate(MS):
        tpy = timings['Python'][idx]
        tcpp = timings['Cpp'][idx]
        tfort = timings['Fortran'][idx]
        
        if not np.isnan(tpy):
            ax2_data['m'].append(m)
            if not np.isnan(tcpp):
                ax2_data['cpp_speedup'].append(tpy / tcpp)
            else:
                ax2_data['cpp_speedup'].append(np.nan)
            
            if not np.isnan(tfort):
                ax2_data['fort_speedup'].append(tpy / tfort)
            else:
                ax2_data['fort_speedup'].append(np.nan)
    
    if ax2_data['m']:
        x_pos = np.arange(len(ax2_data['m']))
        width = 0.35
        
        cpp_valid = ~np.isnan(ax2_data['cpp_speedup'])
        fort_valid = ~np.isnan(ax2_data['fort_speedup'])
        
        if np.any(cpp_valid):
            ax2.bar(x_pos[cpp_valid] - width/2, np.array(ax2_data['cpp_speedup'])[cpp_valid], 
                   width, label='C++ vs Python', color='#00599C', alpha=0.8)
        if np.any(fort_valid):
            ax2.bar(x_pos[fort_valid] + width/2, np.array(ax2_data['fort_speedup'])[fort_valid], 
                   width, label='Fortran vs Python', color='#734f96', alpha=0.8)
        
        ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Referencia Python (1x)')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([f"m={m}" for m in ax2_data['m']])
        ax2.set_ylabel('Speedup (×)', fontsize=12)
        ax2.set_xlabel('Tamaño de malla', fontsize=12)
        ax2.set_title('Speedup Relativo a Python', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig("plots/performance_comparison.png", dpi=150)
    print("\n  ✓ Guardado: plots/performance_comparison.png")
    plt.close()

# =============================================================================
# RESUMEN FINAL
# =============================================================================
print("\n" + "="*60)
print("RESUMEN DE GRÁFICOS GENERADOS")
print("="*60)
print(f"  1. Evolución temporal de errores L2: {len(MS)} gráficos")
print("  2. Tiempos de cálculo vs m: plots/timing_vs_m.png")
print("  3. Convergencia de error: plots/error_vs_m.png")
print("  4. Comparación de rendimiento: plots/performance_comparison.png")
print("\n✓ Todos los gráficos guardados en el directorio /plots")
print("="*60)