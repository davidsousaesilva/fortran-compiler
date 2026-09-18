from parser.parser_syntax import parse, dump_ast

VALID_TESTS = {
    "hello": r"""      PROGRAM HELLO
      PRINT *, 'Ola, Mundo!'
      END""",

    "fatorial": r"""      PROGRAM FATORIAL
      INTEGER N, I, FAT
      PRINT *, 'Introduza um numero inteiro positivo:'
      READ *, N
      FAT = 1
      DO 10 I = 1, N
         FAT = FAT * I
   10 CONTINUE
      PRINT *, 'Fatorial de ', N, ': ', FAT
      END""",

    "primo": r"""      PROGRAM PRIMO
      INTEGER NUM, I
      LOGICAL ISPRIM
      PRINT *, 'Introduza um numero inteiro positivo:'
      READ *, NUM
      ISPRIM = .TRUE.
      I = 2
  20  IF (I .LE. (NUM/2) .AND. ISPRIM) THEN
         IF (MOD(NUM, I) .EQ. 0) THEN
            ISPRIM = .FALSE.
         ENDIF
         I = I + 1
         GOTO 20
      ENDIF
      IF (ISPRIM) THEN
         PRINT *, NUM, ' e um numero primo'
      ELSE
         PRINT *, NUM, ' nao e um numero primo'
      ENDIF
      END""",

    "somaarr": r"""      PROGRAM SOMAARR
      INTEGER NUMS(5)
      INTEGER I, SOMA
      SOMA = 0
      PRINT *, 'Introduza 5 numeros inteiros:'
      DO 30 I = 1, 5
         READ *, NUMS(I)
         SOMA = SOMA + NUMS(I)
   30 CONTINUE
      PRINT *, 'A soma dos numeros e: ', SOMA
      END""",

    "conversor": r"""      PROGRAM CONVERSOR
      INTEGER NUM, BASE, RESULT, CONVRT

      PRINT *, 'INTRODUZA UM NUMERO DECIMAL INTEIRO:'
      READ *, NUM

      DO 10 BASE = 2, 9
         RESULT = CONVRT(NUM, BASE)
         PRINT *, 'BASE ', BASE, ': ', RESULT
   10 CONTINUE

      END

      INTEGER FUNCTION CONVRT(N, B)
      INTEGER N, B, QUOT, REM, POT, VAL
      VAL = 0
      POT = 1
      QUOT = N
   20 IF (QUOT .GT. 0) THEN
         REM = MOD(QUOT, B)
         VAL = VAL + (REM * POT)
         QUOT = QUOT / B
         POT = POT * 10
         GOTO 20
      ENDIF
      CONVRT = VAL
      RETURN
      END""",

    "real_and_logic": r"""      PROGRAM TESTREAL
      REAL X, Y
      LOGICAL OK
      X = 3.14
      Y = 2.0E+3
      OK = .TRUE.
      IF (OK .AND. X .LT. Y) THEN
         PRINT *, 'VALIDO'
      ENDIF
      END""",

    "lowercase_caseinsensitive": r"""      program mini
      integer x
      x = 10
      print *, 'ok'
      end""",

    "string_with_doubled_quote": r"""      PROGRAM STR
      PRINT *, 'Ola ''Mundo'''
      END""",
}


INVALID_TESTS = {
    "missing_end": r"""      PROGRAM BAD
      INTEGER X
      X = 1""",

    "bad_assignment": r"""      PROGRAM BAD
      INTEGER X
      X = 
      END""",

    "bad_if": r"""      PROGRAM BAD
      INTEGER X
      IF (X .LT. 10) THEN
         PRINT *, 'OK'
      END""",

    "bad_do": r"""      PROGRAM BAD
      INTEGER I
      DO 10 I = 1
   10 CONTINUE
      END""",
}

def run_suite(title, tests, show_tree=True):
    print(f"========== {title} ==========")
    for name, text in tests.items():
        print(f"--- {name} ---")
        try:
            ast = parse(text)
            print("OK")
            if show_tree:
                dump_ast(ast)
        except Exception as e:
            print("Parsing failed:", e)
        print()


def main():
    run_suite("VALID PROGRAMS", VALID_TESTS, show_tree=True)
    run_suite("INVALID PROGRAMS", INVALID_TESTS, show_tree=False)


if __name__ == "__main__":
    main()