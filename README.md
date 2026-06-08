# Physical Modeling

A structured course repository at the intersection of computational physics and scientific machine learning — progressing from classical ODE/PDE numerical methods and quantum mechanics simulations through deep neural networks, Physics-Informed Neural Networks (PINNs), quantum computing, and, finally, hardware-deployable quantized models for LHC particle jet classification.

Implementations span Python, C++, Fortran 90, and C, with exams backed by full LaTeX reports.

---

## Curriculum

| # | Module | Key Topics |
|---|--------|-----------|
| 0 | [Introduction](0.Introduccion/) | Course overview, mathematical definitions, modeling framework |
| 1 | [ODEs](1.EDOs/) | Euler, RK4, RK45, Adams–Bashforth–Moulton, stability analysis |
| 2 | [Numerov & TISE](2.Numerov-ESIT/) | Numerov method, quantum potential wells, eigenvalue problems |
| 3 | [PDEs](3.EDPs/) | Finite differences in Python, C, Fortran; heat, Poisson, wave equations |
| 4 | [Neural Networks](4.Redes_Neuronales/) | Backpropagation, CNN, RNN, LSTM, transfer learning, CIFAR-10 |
| 5 | [PINNs](5.PINNs/) | Physics-Informed Neural Networks for parabolic, elliptic, and solid-mechanics PDEs |
| 6 | [Quantum Computing](6.QC/) | Linear algebra review, quantum gates, Deutsch & Deutsch–Jozsa algorithms (Qiskit) |

---

## Exams & Applied Projects

### Test 1 — 1D Wave Equation: Multi-Language Implementation
`Test-01-Wave/`

Finite difference solver for the 1D wave equation implemented independently in three languages and benchmarked for accuracy and runtime. Each solver produces field snapshots and is validated against the analytical solution with L2 and L∞ error norms.

| Language | File | Key details |
|----------|------|-------------|
| Python | `wave_py.py` | Reference implementation |
| C++ | `wave_cpp.cpp` | `-O3 -std=c++17`, `<filesystem>`, wall-clock timing |
| Fortran 90 | `wave_fortran.f90` | Double precision, `selected_real_kind`, structured I/O |

Includes animation (`animation.py`), result plotting (`graph.py`), a `Makefile` for C++/Fortran, and a full **LaTeX lab report** with bibliography.

**Stack:** Python, C++17, Fortran 90, Matplotlib, LaTeX

---

### Test 2 — Poisson Equation: Python Finite-Difference Solver
`Test-02-Poisson/`

Modular Python solver for the 2D elliptic Poisson/Laplace equation on rectangular domains with Dirichlet boundary conditions. Uses `scipy.sparse` (LIL → CSR) for efficient assembly and solution. Outputs a comparison table of numerical vs. analytical solutions including absolute and relative error columns.

```
solver.py          # FD assembly and sparse solve (solve_pde_fourier)
constructor.py     # Domain and boundary condition builder
graficar.py        # Surface and contour plots
graficar_malla.py  # Grid visualization
```

Includes analytical verification of the Laplacian and a Jupyter notebook with side-by-side numerical/exact solution plots.

**Stack:** Python, NumPy, SciPy (sparse), Matplotlib, Jupyter

---

### Test 3 — LHC Particle Jet Tagging with Quantized Neural Networks
`Test-03-Particles/`

End-to-end pipeline for classifying particle jets from the **LHC (Large Hadron Collider)** into five categories — gluon, light quark, W boson, Z boson, and top quark — using 16 high-level features (HLF) extracted from HDF5 datasets.

The network uses **HGQ2** (Heterogeneous Graph Quantization 2) `QDense` layers, which produce models that can be synthesized directly onto **FPGAs** via `hls4ml`. This is the deployment paradigm used in real LHC trigger systems, where inference must run in microseconds.

**Pipeline stages:**
1. Dataset download from Kaggle (`hls4ml-lhc-jet-dataset-150-particles`, HDF5)
2. HLF extraction and multiprocess loading across files
3. Train/val split and `StandardScaler` normalization
4. Quantized MLP construction with HGQ2 `QDense` layers
5. Training (Adam, 200 epochs, large batch for quantization stability)
6. Evaluation: accuracy, confusion matrix (5-class + pairwise binary)
7. FPGA synthesis report via `hls4ml`

Also includes a `small-jet-tagger-with-hgq-1.ipynb` for a lighter baseline comparison.

**Stack:** TensorFlow/Keras 3, HGQ2, hls4ml, h5py, scikit-learn, NumPy, Matplotlib

---

### NN Homeworks
`NN-Homeworks/`

| Notebook | Description |
|----------|-------------|
| `Fashion-CNN.ipynb` | CNN classifier on Fashion-MNIST |
| `Parachute-RNN-LSTM.ipynb` | RNN and LSTM for time-series prediction of parachutist dynamics under drag; includes physics context and ipywidgets interactive tuning |

---

## Module Highlights

### Numerov Method & Quantum Mechanics (`2.Numerov-ESIT/`)
Solves the time-independent Schrödinger equation (TISE) numerically using the Numerov algorithm — a specialized second-order ODE integrator with O(h⁴) accuracy, superior to RK4 for equations without first-derivative terms. Applied to:
- Infinite square quantum well
- Finite square quantum well
- Eigenvalue shooting method
- Benchmarked against RK/Verner methods and compared with hydrogen atom solutions

### PDE Solvers in Fortran (`3.EDPs/Fortran/`)
Complete Fortran 90 scientific computing toolkit built from scratch:

| File | Description |
|------|-------------|
| `osciladorCuantico.f90` | TISE solver for quantum harmonic oscillator via matrix diagonalization |
| `Poisson.f90` | 2D Poisson equation solver |
| `LUdescomp.f90` | LU decomposition for dense linear systems |
| `tridiagon.f90` | Thomas algorithm for tridiagonal systems |
| `diagotri.f90` | Tridiagonal matrix eigenvalue solver |
| `inversionMatriz.f90` | Matrix inversion routine |
| `sistemaEcuaciones.f90` | General linear system solver |

### PINNs (`5.PINNs/`)
Physics-Informed Neural Networks trained to satisfy a PDE as part of the loss function — no labeled solution data required. Covers:
- Simple ODE (introductory example)
- Parabolic PDEs (two variants)
- 1D heat equation with real measurement data (`datos_calor.csv`)
- Solid mechanics with displacement field data (`Displacement.csv`, `InitialPosition.csv`)
- PINNs for 2D Laplace and Poisson equations

### Quantum Computing with Qiskit (`6.QC/`)
From first principles to quantum algorithms, implemented in Qiskit:
- Dirac notation and quantum state linear algebra
- Single and multi-qubit gate circuits
- Deutsch algorithm (constant vs. balanced oracle discrimination)
- Deutsch–Jozsa algorithm (generalized to n qubits)

---

## Stack

| Domain | Tools |
|--------|-------|
| Scientific Python | NumPy, SciPy, Matplotlib, Pandas |
| Deep Learning | TensorFlow, Keras 3, PyTorch |
| Physics ML | HGQ2, hls4ml |
| Quantum Computing | Qiskit |
| Systems languages | C++17, Fortran 90, C |
| Notebook environment | Jupyter Lab |

---

## Repository Structure

```
Physical-Modeling/
├── 0.Introduccion/              # Course foundations and mathematical definitions
├── 1.EDOs/                      # ODE solvers: Euler, RK4, RK45, ABM, stability
├── 2.Numerov-ESIT/              # Numerov method + quantum well eigenvalue problems
│   └── Articles/                #   Key references (Numerov, hydrogen atom, Airy)
├── 3.EDPs/                      # PDE finite-difference solvers
│   ├── Diferencias_Finitas/     #   Python notebooks (heat, Poisson, wave)
│   ├── Fortran/                 #   Fortran 90 scientific toolkit
│   └── Codigos C/               #   C reference implementation
├── 4.Redes_Neuronales/          # Deep learning: CNN, RNN, LSTM, transfer learning
├── 5.PINNs/                     # Physics-Informed Neural Networks
│   ├── Ejemplos_1/ to 4/        #   ODE, parabolic, heat with data, solid mechanics
│   ├── PINNs_Laplace.ipynb      #   PINN for 2D Laplace equation
│   └── PINNs_Poisson.ipynb      #   PINN for 2D Poisson equation
├── 6.QC/                        # Quantum computing with Qiskit
├── NN-Homeworks/                # Fashion-MNIST CNN + parachute LSTM
├── Test-01-Wave/                # Exam 1: wave equation in Python, C++, Fortran + LaTeX report
├── Test-02-Poisson/             # Exam 2: modular Python Poisson solver
└── Test-03-Particles/           # Exam 3: LHC jet tagging with HGQ2 quantized networks
```

---

## License

This repository is for educational purposes. All code is original coursework unless otherwise noted in individual files.
