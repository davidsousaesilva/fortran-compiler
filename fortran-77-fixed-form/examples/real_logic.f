      PROGRAM TESTREAL
      REAL X, Y
      LOGICAL OK

      X = 3.14
      Y = 2.0E+3
      OK = .TRUE.

      IF (OK .AND. X .LT. Y) THEN
         PRINT *, 'VALIDO'
      ELSE
         PRINT *, 'INVALIDO'
      ENDIF

      END