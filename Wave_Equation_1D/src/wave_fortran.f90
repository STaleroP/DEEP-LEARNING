! wave_fortran.f90
program wave_fortran
  implicit none
  integer, parameter :: dp = selected_real_kind(15,307)
  integer :: m, i, nt, n_inner, save_interval, n_snap_expected, sn, j, ios
  real(dp) :: L, c, h, Lambda, k, T, wall_time, tstart, tend
  real(dp) :: L2, Linf, tt, exact, e
  real(dp), allocatable :: x(:), u0(:), v0(:), u_prev(:), u_curr(:), u_next(:)
  real(dp), allocatable :: snapshots(:,:), times(:)
  character(len=32) :: arg
  character(len=128) :: outdir, csvfile, errfile, timefile
  intrinsic :: ceiling
  
  ! defaults
  L = 100.0_dp
  c = 10.0_dp
  m = 100
  T = 100.0_dp
  Lambda = 0.8_dp

  call get_command_argument(1, arg, status=ios)
  if (ios == 0) then
     read(arg,*) m
  end if

  h = L / real(m, dp)
  k = Lambda * h / c
  nt = ceiling(T / k)
  n_inner = m - 1
  save_interval = nt / 200
  if (save_interval < 1) save_interval = 1
  n_snap_expected = 2 + ( (nt - 1 + save_interval - 1) / save_interval )

  allocate(x(0:m))
  allocate(u0(n_inner), v0(n_inner))
  allocate(u_prev(n_inner), u_curr(n_inner), u_next(n_inner))
  allocate(snapshots(n_snap_expected, m+1))
  allocate(times(n_snap_expected))

  do i = 0, m
     x(i) = real(i, dp) * h
  end do

  ! initial conds
  do i = 1, n_inner
     u0(i) = sin(acos(-1.0_dp) * x(i) / L)
     v0(i) = 0.0_dp
  end do

  u_prev = u0
  do i = 1, n_inner
     u_curr(i) = (1.0_dp - Lambda*Lambda) * u0(i) + k * v0(i)
  end do
  do i = 2, n_inner - 1
     u_curr(i) = u_curr(i) + (Lambda*Lambda / 2.0_dp) * (u0(i-1) + u0(i+1))
  end do
  if (n_inner >= 1) then
     u_curr(1) = (1.0_dp - Lambda*Lambda) * u0(1) + &
                 (Lambda*Lambda / 2.0_dp) * u0(2) + k * v0(1)
  end if
  if (n_inner >= 2) then
     u_curr(n_inner) = (1.0_dp - Lambda*Lambda) * u0(n_inner) + &
                       (Lambda*Lambda / 2.0_dp) * u0(n_inner-1) + k * v0(n_inner)
  end if

  ! store first two
  sn = 1
  snapshots(sn, :) = 0.0_dp
  do i = 1, m-1
     snapshots(sn, i+1) = u_prev(i)
  end do
  times(sn) = 0.0_dp
  sn = sn + 1

  snapshots(sn, :) = 0.0_dp
  do i = 1, m-1
     snapshots(sn, i+1) = u_curr(i)
  end do
  times(sn) = k
  sn = sn + 1

  call cpu_time(tstart)
  do j = 1, nt-1
     ! compute u_next stencil
     if (n_inner == 1) then
        u_next(1) = (2.0_dp*(1.0_dp - Lambda*Lambda)) * u_curr(1) - u_prev(1)
     else
        u_next(1) = (2.0_dp*(1.0_dp - Lambda*Lambda)) * u_curr(1) + Lambda*Lambda * u_curr(2) - u_prev(1)
        if (n_inner > 2) then
           do i = 2, n_inner-1
              u_next(i) = (2.0_dp*(1.0_dp - Lambda*Lambda)) * u_curr(i) + &
                          Lambda*Lambda * (u_curr(i-1) + u_curr(i+1)) - u_prev(i)
           end do
        end if
        if (n_inner >= 2) then
           u_next(n_inner) = (2.0_dp*(1.0_dp - Lambda*Lambda)) * u_curr(n_inner) + &
                             Lambda*Lambda * u_curr(n_inner-1) - u_prev(n_inner)
        end if
     end if

     if (mod(j, save_interval) == 0) then
        snapshots(sn, :) = 0.0_dp
        do i = 1, m-1
           snapshots(sn, i+1) = u_next(i)
        end do
        times(sn) = real(j+1, dp) * k
        sn = sn + 1
     end if

     u_prev = u_curr
     u_curr = u_next
  end do
  call cpu_time(tend)
  wall_time = tend - tstart

  ! create output directory
  outdir = 'results/Fortran/m_' // trim(adjustl(itoa(m)))
  call system('mkdir -p ' // trim(outdir))

  csvfile = trim(outdir) // '/wave_fort.csv'
  open(unit=11, file=csvfile, status='replace', action='write', iostat=ios)
  if (ios /= 0) stop 'Cannot open csv for writing'

  write(11,'(A)',advance='no') 't'
  do i = 0, m
     write(11,'(A,I0)',advance='no') ',x', i
  end do
  write(11,*)

  do j = 1, sn-1
     write(11,'(F12.6)',advance='no') times(j)
     do i = 0, m
        write(11,'(A,F12.6)',advance='no') ',', snapshots(j,i+1)
     end do
     write(11,*)
  end do
  close(11)

  ! compute errors (L2, Linf) across saved snapshots
  errfile = trim(outdir) // '/errors.csv'
  open(unit=12, file=errfile, status='replace', action='write', iostat=ios)
  if (ios /= 0) stop 'Cannot open errors.csv'
  write(12,*) 't,L2,Linf'
  do j = 1, sn-1
     tt = times(j)
     L2 = 0.0_dp
     Linf = 0.0_dp
     do i = 1, m-1
        exact = cos(c*acos(-1.0_dp)*tt/L) * sin(acos(-1.0_dp) * x(i) / L)
        e = snapshots(j,i+1) - exact
        L2 = L2 + e*e
        Linf = max(Linf, abs(e))
     end do
     L2 = sqrt(h * L2)
     write(12,'(F12.6,A,F12.6,A,F12.6)') tt, ',', L2, ',', Linf
  end do
  close(12)

  timefile = trim(outdir) // '/timing.txt'
  open(unit=13, file=timefile, status='replace', action='write', iostat=ios)
  write(13,'(F12.6)') wall_time
  close(13)

  print *, 'Fortran: m=', m, ' snapshots=', sn-1, ' time=', wall_time

  deallocate(x,u0,v0,u_prev,u_curr,u_next,snapshots,times)

contains
  function itoa(i) result(s)
    integer, intent(in) :: i
    character(len=32) :: s
    write(s, '(I0)') i
  end function itoa

end program wave_fortran