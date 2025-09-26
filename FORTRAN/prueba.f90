PROGRAM proyectil
    IMPLICIT NONE
    ! Usamos doble precisión
    REAL(KIND=8) :: g, V0, Vx, Vy, ang_deg, ang, t, x0, y0, x_t, y_t
    REAL(KIND=8) :: t_flight, t_peak, y_max, x_range, disc, sinang, cosang

    g = 9.81D0
    ! Pedir datos al usuario
    PRINT *, 'Ingrese la posicion inicial x0 (m):'
    READ  (*,*) x0
    PRINT *, 'Ingrese la posicion inicial y0 (m):'
    READ  (*,*) y0
    PRINT *, 'Ingrese la velocidad inicial V0 (m/s):'
    READ  (*,*) V0
    PRINT *, 'Ingrese el angulo de lanzamiento (grados):'
    READ  (*,*) ang_deg
    PRINT *, 'Ingrese el tiempo t (s) para evaluar la posicion:'
    READ  (*,*) t

    ! Convertir angulo a radianes
    ang = ang_deg * (ACOS(-1.0D0) / 180.0D0)
    sinang = SIN(ang)
    cosang = COS(ang)

    ! Componentes de velocidad
    Vx = V0 * cosang
    Vy = V0 * sinang

    ! Posicion en el tiempo t pedido por el usuario
    x_t = x0 + Vx * t
    y_t = y0 + Vy * t - 0.5D0 * g * t**2

    ! Calculo del tiempo total de vuelo: resolvemos la ecuacion para y(t)=0
    !  -0.5*g*T^2 + V0*sin(ang)*T + y0 = 0
    ! a = -0.5*g, b = V0*sinang, c = y0  => raiz positiva: (b + sqrt(b^2 + 2*g*y0)) / g
    disc = (V0 * sinang)**2 + 2.0D0 * g * y0
    IF (disc < 0.0D0) THEN
        ! Caso numericamente improbable si g>0 y y0 real; protegemos por si acaso
        PRINT *, 'Discriminante negativo: no hay solucion real para el tiempo de vuelo.'
        t_flight = -1.0D0
    ELSE
        t_flight = (V0 * sinang + SQRT(disc)) / g
    END IF

    ! Tiempo hasta la altura maxima y altura maxima
    t_peak = (V0 * sinang) / g
    y_max = y0 + (V0**2 * sinang**2) / (2.0D0 * g)

    ! Alcance horizontal (posición x cuando y = 0, usando t_flight)
    IF (t_flight > 0.0D0) THEN
        x_range = x0 + Vx * t_flight
    ELSE
        x_range = 0.0D0
    END IF

    ! Impresion de resultados
    PRINT *
    PRINT *, '--- RESULTADOS ---'
    PRINT '(A,F12.6)','Posicion inicial x0 = ', x0
    PRINT '(A,F12.6)','Posicion inicial y0 = ', y0
    PRINT '(A,F12.6)','Velocidad inicial V0 = ', V0
    PRINT '(A,F12.6)','Angulo = ', ang_deg, ' grados'
    PRINT *
    PRINT '(A,F12.6)','Posicion en t = ', t
    PRINT '(A,F12.6,A,F12.6)', '  x(t) = ', x_t, '  metros  y(t) = ', y_t
    IF (t_flight > 0.0D0) THEN
        PRINT '(A,F12.6)','Tiempo total de vuelo = ', t_flight, ' segundos'
        PRINT '(A,F12.6)','Alcance horizontal = ', x_range, ' metros'
    ELSE
        PRINT *, 'Tiempo total de vuelo no disponible.'
    END IF
    PRINT '(A,F12.6)','Tiempo hasta altura maxima = ', t_peak, ' s'
    PRINT '(A,F12.6)','Altura maxima = ', y_max, ' metros'
    PRINT *, '-------------------'

END PROGRAM proyectil
