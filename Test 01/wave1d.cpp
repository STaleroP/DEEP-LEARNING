#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <chrono>
#include <string>
#include <iomanip>

int main() {
    using namespace std;
    using namespace std::chrono;

    // Parámetros físicos y malla
    const double L = 100.0;
    const double c = 10.0;
    const int m = 100;
    const double h = L / m;
    const double Lambda = 0.8;
    const double k = Lambda * h / c;
    const double T = 15.0;
    const int nt = static_cast<int>(ceil(T / k));
    const int n_inner = m - 1;

    vector<double> x(m + 1);
    for (int i = 0; i <= m; ++i)
        x[i] = i * h;

    // Condiciones iniciales
    auto f_init = [&](double xx) { return sin(M_PI * xx / L); };    // f(x) = u(x,0) -> desplazamiento inicial
    auto g_init = [&](double) { return 0.0; };                     // g(x) = u_t(x,0) -> velocidad inicial

    vector<double> u0(n_inner), v0(n_inner);
    for (int i = 0; i < n_inner; ++i) {
        u0[i] = f_init(x[i + 1]);
        v0[i] = g_init(x[i + 1]);
    }

    // Construcción de matriz M
    vector<vector<double>> Mmat(n_inner, vector<double>(n_inner, 0.0));
    for (int i = 0; i < n_inner; ++i)
        Mmat[i][i] = 2.0 * (1.0 - Lambda * Lambda);
    for (int i = 0; i < n_inner - 1; ++i) {
        Mmat[i][i + 1] += Lambda * Lambda;
        Mmat[i + 1][i] += Lambda * Lambda;
    }

    // Inicialización temporal
    vector<double> u_prev = u0;          // u^(0)
    vector<double> u_curr(n_inner, 0.0); // u^(1)

    // Primer paso en tiempo
    for (int i = 0; i < n_inner; ++i)
        u_curr[i] = (1.0 - Lambda * Lambda) * u0[i] + k * v0[i];

    for (int i = 1; i < n_inner - 1; ++i)
        u_curr[i] += (Lambda * Lambda / 2.0) * (u0[i - 1] + u0[i + 1]);

    // aplicar condiciones de frontera (u=0 en extremos)
    u_curr[0] = (1.0 - Lambda * Lambda) * u0[0]
                + (Lambda * Lambda / 2.0) * (u0[1])
                + k * v0[0];

    u_curr[n_inner - 1] = (1.0 - Lambda * Lambda) * u0[n_inner - 1]
                          + (Lambda * Lambda / 2.0) * (u0[n_inner - 2])
                          + k * v0[n_inner - 1];

    // Evolución temporal
    vector<vector<double>> snapshots;
    vector<double> times;

    // Guardar primeros estados
    vector<double> full0(m + 1, 0.0);
    for (int i = 1; i < m; ++i) full0[i] = u_prev[i - 1];
    snapshots.push_back(full0);
    times.push_back(0.0);

    vector<double> full1(m + 1, 0.0);
    for (int i = 1; i < m; ++i) full1[i] = u_curr[i - 1];
    snapshots.push_back(full1);
    times.push_back(k);

    vector<double> u_next(n_inner, 0.0);

    cout << "Iniciando integración temporal..." << endl;
    auto t0 = high_resolution_clock::now();

    for (int j = 1; j < nt; ++j) {
        // u^{j+1} = M * u^{j} - u^{j-1}
        for (int i = 0; i < n_inner; ++i) {
            double sum = 0.0;
            for (int l = 0; l < n_inner; ++l)
                sum += Mmat[i][l] * u_curr[l];
            u_next[i] = sum - u_prev[i];
        }

        // Guardar snapshots cada cierto número de pasos
        if (j % max(1, nt / 200) == 0) {
            vector<double> full(m + 1, 0.0);
            for (int i = 1; i < m; ++i)
                full[i] = u_next[i - 1];
            snapshots.push_back(full);
            times.push_back((j + 1) * k);
        }
        u_prev = u_curr;
        u_curr = u_next;
    }

    auto t1 = high_resolution_clock::now();
    double elapsed = duration<double>(t1 - t0).count();
    cout << "Integración completada en " << elapsed << " s, "
         << snapshots.size() << " snapshots almacenados." << endl;

    // Exportar a CSV
    string filename = "wave_cpp.csv";
    ofstream csv(filename);
    csv << fixed << setprecision(6);

    // encabezado
    csv << "t";
    for (int i = 0; i <= m; ++i)
        csv << ",x" << i;
    csv << "\n";

    // datos
    for (size_t j = 0; j < snapshots.size(); ++j) {
        csv << times[j];
        for (int i = 0; i <= m; ++i)
            csv << "," << snapshots[j][i];
        csv << "\n";
    }

    csv.close();
    return 0;
}
