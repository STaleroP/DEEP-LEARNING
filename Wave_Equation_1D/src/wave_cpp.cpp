// wave_cpp.cpp
// Compile: g++ -O3 -std=c++17 -o wave_cpp wave_cpp.cpp
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <fstream>
#include <chrono>
#include <iomanip>
#include <string>
#include <filesystem>

using namespace std;
namespace fs = std::filesystem;

int main(int argc, char** argv){
    int m = 100;
    if (argc > 1) m = stoi(argv[1]);

    const double L = 100.0;
    const double c = 10.0;
    const double h = L / m;
    const double Lambda = 0.8;
    const double k = Lambda * h / c;
    const double T = 100.0;
    const int nt = static_cast<int>(ceil(T / k));
    const int n_inner = m - 1;

    vector<double> x(m+1);
    for(int i=0;i<=m;++i) x[i] = i * h;

    auto f_init = [&](double xx){ return sin(M_PI * xx / L); };
    auto g_init = [&](double){ return 0.0; };

    vector<double> u0(n_inner), v0(n_inner);
    for(int i=0;i<n_inner;++i){
        u0[i] = f_init(x[i+1]);
        v0[i] = g_init(x[i+1]);
    }

    // Build tridiagonal M (dense storage but only 3 diag used in prod)
    vector<double> diag(n_inner, 2.0*(1.0 - Lambda*Lambda));
    vector<double> off(n_inner-1, Lambda*Lambda);

    // initial steps
    vector<double> u_prev = u0;
    vector<double> u_curr(n_inner,0.0);
    for(int i=0;i<n_inner;++i) u_curr[i] = (1.0 - Lambda*Lambda)*u0[i] + k * v0[i];
    for(int i=1;i<n_inner-1;++i) u_curr[i] += (Lambda*Lambda/2.0) * (u0[i-1] + u0[i+1]);
    u_curr[0] = (1.0 - Lambda*Lambda)*u0[0] + (Lambda*Lambda/2.0) * u0[1] + k * v0[0];
    u_curr[n_inner-1] = (1.0 - Lambda*Lambda)*u0[n_inner-1] + (Lambda*Lambda/2.0) * u0[n_inner-2] + k * v0[n_inner-1];

    // storage
    vector<vector<double>> snapshots;
    vector<double> times;
    auto push_full = [&](const vector<double>& interior, double tt){
        vector<double> full(m+1, 0.0);
        for(int i=0;i<n_inner;++i) full[i+1] = interior[i];
        snapshots.push_back(full);
        times.push_back(tt);
    };

    push_full(u_prev, 0.0);
    push_full(u_curr, k);

    // error storage (t, L2, Linf)
    vector<array<double,3>> errors;
    // compute initial errors
    vector<double> ex(m+1);
    
    // Error at t=0
    for(int i=0;i<=m;++i) ex[i] = sin(M_PI * x[i] / L);
    double hdp = h;
    double L2 = 0.0, Linf = 0.0;
    for(int i=1;i<m;++i){ 
        double e = snapshots[0][i] - ex[i]; 
        L2 += e*e; 
        Linf = max(Linf, fabs(e)); 
    }
    L2 = sqrt(hdp * L2);
    errors.push_back({0.0, L2, Linf});
    
    // Error at t=k
    double tt = k;
    for(int i=0;i<=m;++i) ex[i] = cos(c*M_PI*tt/L) * sin(M_PI * x[i] / L);
    L2 = 0.0; Linf = 0.0;
    for(int i=1;i<m;++i){ 
        double e = snapshots[1][i] - ex[i]; 
        L2 += e*e; 
        Linf = max(Linf, fabs(e)); 
    }
    L2 = sqrt(hdp * L2);
    errors.push_back({tt, L2, Linf});

    // time stepping
    int save_interval = max(1, nt/200);
    auto t0 = chrono::high_resolution_clock::now();
    vector<double> u_next(n_inner,0.0);
    
    for(int j=1;j<nt;++j){
        // compute M*u_curr via stencil
        if(n_inner==1){
            u_next[0] = diag[0]*u_curr[0] - u_prev[0];
        } else {
            u_next[0] = diag[0]*u_curr[0] + off[0]*u_curr[1] - u_prev[0];
            for(int i=1;i<n_inner-1;++i){
                u_next[i] = diag[i]*u_curr[i] + off[i]*u_curr[i+1] + off[i-1]*u_curr[i-1] - u_prev[i];
            }
            u_next[n_inner-1] = diag[n_inner-1]*u_curr[n_inner-1] + off[n_inner-2]*u_curr[n_inner-2] - u_prev[n_inner-1];
        }

        // Save snapshot if needed
        if(j % save_interval == 0){
            push_full(u_next, (j+1)*k);
        }
        
        // compute error using u_next
        double time_now = (j+1)*k;
        for(int i=0;i<=m;++i) ex[i] = cos(c*M_PI*time_now/L) * sin(M_PI * x[i] / L);
        L2 = 0.0; Linf = 0.0;
        for(int i=0;i<n_inner;++i){ 
            double e = u_next[i] - ex[i+1]; 
            L2 += e*e; 
            Linf = max(Linf, fabs(e)); 
        }
        L2 = sqrt(hdp * L2);
        errors.push_back({time_now, L2, Linf});

        u_prev.swap(u_curr);
        u_curr.swap(u_next);
    }
    auto t1 = chrono::high_resolution_clock::now();
    double wall = chrono::duration<double>(t1 - t0).count();

    // prepare directories
    fs::path outdir = fs::path("results") / "Cpp" / ("m_" + to_string(m));
    fs::create_directories(outdir);

    // write snapshots CSV
    string csvfile = (outdir / "wave_cpp.csv").string();
    ofstream csv(csvfile);
    csv<<fixed<<setprecision(6);
    csv<<"t";
    for(int i=0;i<=m;++i) csv<<",x"<<i;
    csv<<"\n";
    for(size_t s=0;s<snapshots.size();++s){
        csv<<times[s];
        for(int i=0;i<=m;++i) csv<<","<<snapshots[s][i];
        csv<<"\n";
    }
    csv.close();

    // write errors
    string errfile = (outdir / "errors.csv").string();
    ofstream ef(errfile);
    ef<<"t,L2,Linf\n";
    for(auto &row: errors) ef<<row[0]<<","<<row[1]<<","<<row[2]<<"\n";
    ef.close();

    // timing
    string timefile = (outdir / "timing.txt").string();
    ofstream tf(timefile);
    tf<<wall<<"\n";
    tf.close();

    cout<<"C++: m="<<m<<", snaps="<<snapshots.size()<<", time="<<wall<<"s -> "<<csvfile<<"\n";
    return 0;
}