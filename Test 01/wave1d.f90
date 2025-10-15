! wave1d_fortran.f90
program wave1d_fortran
  implicit none

  ! ---------- precision ----------
  integer, parameter :: dp = selected_real_kind(15, 307)

  ! ---------- parámetros del problema ----------
  real(dp), parameter :: Ldom = 100.0_dp     ! longitud del dominio
  real(dp), parameter :: c = 10.0_dp         ! velocidad de la onda
  integer, parameter :: m = 100              ! número de subintervalos
  real(dp), parameter :: h = Ldom / real(m, dp) ! paso espacial
  real(dp), parameter :: Lambda = 0.8_dp     ! número de Courant
  real(dp), parameter :: kstep = Lambda * h / c  ! paso temporal
  real(dp), parameter :: T = 15.0_dp         ! tiempo final
  
  ! Constantes matemáticas
  real(dp), parameter :: pi = 4.0_dp * atan(1.0_dp)
  
  ! Variables derivadas
  integer :: nt, n_inner, save_interval, n_snap_expected
  integer :: ii, jj, ll, sn, unit_bin, unit_meta, ios
  real(dp) :: tstart, tend, wall_time, sum_val
  character(len=128) :: filename_bin, filename_meta
  
  ! ---------- arrays allocatables ----------
  real(dp), allocatable :: x(:)              ! puntos de la malla 0..m
  real(dp), allocatable :: u0(:), v0(:)      ! condiciones iniciales
  real(dp), allocatable :: u_prev(:)         ! u^(j-1)
  real(dp), allocatable :: u_curr(:)         ! u^(j)  
  real(dp), allocatable :: u_next(:)         ! u^(j+1)
  real(dp), allocatable :: Mmat(:,:)         ! matriz M
  real(dp), allocatable :: snapshots(:,:)    ! matriz de snapshots
  real(dp), allocatable :: times(:)          ! tiempos de los snapshots

  ! ---------- cálculo de dimensiones ----------
  nt = ceiling(T / kstep)
  n_inner = m - 1
  save_interval = max(1, nt / 200)
  n_snap_expected = 2 + (nt - 1) / save_interval

  ! ---------- asignación de memoria ----------
  allocate(x(0:m))
  allocate(u0(n_inner), v0(n_inner))
  allocate(u_prev(n_inner), u_curr(n_inner), u_next(n_inner))
  allocate(Mmat(n_inner, n_inner))
  allocate(snapshots(n_snap_expected, 0:m))
  allocate(times(n_snap_expected))

  ! ---------- inicialización de la malla ----------
  do ii = 0, m
    x(ii) = real(ii, dp) * h
  end do

  ! ---------- condiciones iniciales ----------
  do ii = 1, n_inner
    u0(ii) = sin(pi * x(ii) / Ldom)    ! desplazamiento inicial f(x)
    v0(ii) = 0.0_dp                    ! velocidad inicial g(x) = 0
  end do

  ! ---------- construcción de la matriz M ----------
  ! La matriz M implementa: u^(n+1) = M * u^(n) - u^(n-1)
  ! Donde M * u^(n) = 2u^n - λ²(u^n_{i-1} - 2u^n_i + u^n_{i+1})
  !                 = λ²u^n_{i-1} + (2 - 2λ²)u^n_i + λ²u^n_{i+1}
  
  Mmat = 0.0_dp
  
  ! Diagonal principal: 2 - 2λ²
  do ii = 1, n_inner
    Mmat(ii, ii) = 2.0_dp - 2.0_dp * Lambda * Lambda
  end do
  
  ! Subdiagonales: λ²
  do ii = 1, n_inner - 1
    Mmat(ii, ii + 1) = Lambda * Lambda
    Mmat(ii + 1, ii) = Lambda * Lambda
  end do

  ! ---------- inicialización temporal ----------
  u_prev = u0  ! u^(0)
  
  ! Cálculo de u^(1) usando el esquema de Taylor para el primer paso
  ! u^1 = u^0 + k*v^0 + (k²/2)*u_tt^0
  ! donde u_tt = c²*u_xx, entonces: u^1 = u^0 + k*v^0 + (λ²/2)*(u^0_{i-1} - 2u^0_i + u^0_{i+1})
  do ii = 1, n_inner
    if (ii == 1) then
      ! Punto adyacente a frontera izquierda (u0(0) = 0)
      u_curr(ii) = u0(ii) + kstep * v0(ii) + &
                   (Lambda * Lambda / 2.0_dp) * (0.0_dp - 2.0_dp * u0(ii) + u0(ii + 1))
    else if (ii == n_inner) then
      ! Punto adyacente a frontera derecha (u0(n_inner+1) = 0)
      u_curr(ii) = u0(ii) + kstep * v0(ii) + &
                   (Lambda * Lambda / 2.0_dp) * (u0(ii - 1) - 2.0_dp * u0(ii) + 0.0_dp)
    else
      ! Puntos internos
      u_curr(ii) = u0(ii) + kstep * v0(ii) + &
                   (Lambda * Lambda / 2.0_dp) * (u0(ii - 1) - 2.0_dp * u0(ii) + u0(ii + 1))
    end if
  end do

  ! ---------- almacenamiento de snapshots iniciales ----------
  sn = 1
  
  ! Snapshot en t = 0
  snapshots(sn, 0) = 0.0_dp      ! frontera izquierda
  do ii = 1, n_inner
    snapshots(sn, ii) = u_prev(ii) ! puntos internos
  end do
  snapshots(sn, m) = 0.0_dp      ! frontera derecha
  times(sn) = 0.0_dp
  
  ! Snapshot en t = kstep
  sn = sn + 1
  snapshots(sn, 0) = 0.0_dp      ! frontera izquierda
  do ii = 1, n_inner
    snapshots(sn, ii) = u_curr(ii) ! puntos internos
  end do
  snapshots(sn, m) = 0.0_dp      ! frontera derecha
  times(sn) = kstep
  sn = sn + 1

  ! ---------- integración temporal ----------
  call cpu_time(tstart)

  do jj = 1, nt - 1
    ! u^{j+1} = M * u^{j} - u^{j-1}
    do ii = 1, n_inner
      sum_val = 0.0_dp
      do ll = 1, n_inner
        sum_val = sum_val + Mmat(ii, ll) * u_curr(ll)
      end do
      u_next(ii) = sum_val - u_prev(ii)
    end do

    ! Guardar snapshot periódicamente
    if (mod(jj, save_interval) == 0) then
      snapshots(sn, 0) = 0.0_dp      ! frontera izquierda
      do ii = 1, n_inner
        snapshots(sn, ii) = u_next(ii) ! puntos internos
      end do
      snapshots(sn, m) = 0.0_dp      ! frontera derecha
      times(sn) = real(jj, dp) * kstep
      sn = sn + 1
    end if

    ! Avanzar en el tiempo
    u_prev = u_curr
    u_curr = u_next
  end do

  call cpu_time(tend)
  wall_time = tend - tstart

  ! Ajustar número real de snapshots
  n_snap_expected = sn - 1

  write(*, '(A, F8.4, A, I0, A)') 'Integración completada en ', wall_time, &
       ' s, ', n_snap_expected, ' snapshots almacenados.'

  ! ---------- exportar datos binarios ----------
  filename_bin = 'wave1d_fortran.bin'
  filename_meta = 'wave1d_meta.txt'
  
  ! Escribir metadata
  open(newunit=unit_meta, file=filename_meta, status='replace', action='write', iostat=ios)
  if (ios == 0) then
    write(unit_meta, *) n_snap_expected, m + 1
    close(unit_meta)
  else
    write(*,*) 'Error escribiendo archivo de metadata'
  end if

  ! Escribir datos binarios
  open(newunit=unit_bin, file=filename_bin, status='replace', action='write', &
       form='unformatted', access='stream', iostat=ios)
  if (ios == 0) then
    write(unit_bin) snapshots(1:n_snap_expected, 0:m)
    close(unit_bin)
    write(*,*) 'Archivos binarios generados: ', trim(filename_bin), ' y ', trim(filename_meta)
  else
    write(*,*) 'Error escribiendo archivo binario'
  end if

  ! ---------- liberar memoria ----------
  deallocate(x, u0, v0, u_prev, u_curr, u_next, Mmat, snapshots, times)

end program wave1d_fortran