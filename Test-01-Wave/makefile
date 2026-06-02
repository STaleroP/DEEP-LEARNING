# Makefile para compilar y ejecutar pruebas en Python, C++, Fortran
PY=python3
CXX=g++
FC=gfortran
CXXFLAGS=-O3 -march=native -std=c++17
FFLAGS=-O3 -march=native

MS = 1000

.PHONY: all build run clean graphs

all: build run graphs

build:
	@mkdir -p build
	@echo "Compilando C++..."
	$(CXX) $(CXXFLAGS) -o build/wave_cpp src/wave_cpp.cpp
	@echo "Compilando Fortran..."
	$(FC) $(FFLAGS) -o build/wave_fortran src/wave_fortran.f90
	@echo "Build completado."

# Ejecuta las tres implementaciones para cada m
run:
	@echo "Ejecutando tests para MS: $(MS)"
	@mkdir -p results/Python results/Cpp results/Fortran build
	@for m in $(MS); do \
	  echo "=== m=$$m ==="; \
	  echo "Python run..."; \
	  $(PY) src/wave_py.py $$m; \
	  echo "C++ run..."; \
	  ./build/wave_cpp $$m; \
	  echo "Fortran run..."; \
	  ./build/wave_fortran $$m; \
	  echo "done m=$$m"; \
	done
	@echo "Ejecuciones completadas."

# Genera gráficas y comparativas con graph.py (no guarda mp4)
graphs:
	@echo "Generando gráficas (graph.py)..."
	$(PY) src/graph.py
	@echo "Gráficas generadas."

animation:
	@echo "Generando animaciones (animation.py)..."
	$(PY) src/animation.py /home/byob/Documents/Computational/Physical-Modeling/Wave_Equation_1D/results/Cpp/m_1000
	@echo "Animaciones generadas."

clean:
	rm -rf build results plots
