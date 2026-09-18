from parser.parser_syntax import parse
from semantic.semantic_analyzer import SemanticAnalyzer


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
}


INVALID_TESTS = {
    "undeclared_variable": r"""      PROGRAM BAD
      X = 1
      END""",

    "duplicate_variable": r"""      PROGRAM BAD
      INTEGER X
      INTEGER X
      X = 1
      END""",

    "type_error_assignment": r"""      PROGRAM BAD
      INTEGER X
      X = .TRUE.
      END""",

    "if_condition_not_logical": r"""      PROGRAM BAD
      INTEGER X
      X = 1
      IF (X) THEN
         PRINT *, 'BAD'
      ENDIF
      END""",

    "goto_missing_label": r"""      PROGRAM BAD
      INTEGER X
      X = 1
      GOTO 99
      END""",

    "array_without_index": r"""      PROGRAM BAD
      INTEGER A(5)
      PRINT *, A
      END""",

    "array_index_not_integer": r"""      PROGRAM BAD
      INTEGER A(5)
      REAL X
      X = 1.2
      PRINT *, A(X)
      END""",

    "mod_wrong_type": r"""      PROGRAM BAD
      REAL X
      INTEGER Y
      X = 2.5
      Y = MOD(X, 2)
      END""",
}


def run_semantic_test(name, code, should_pass=True):
    print(f"--- {name} ---")

    try:
        ast = parse(code)

        analyzer = SemanticAnalyzer()
        ok = analyzer.analyze(ast)

        if should_pass:
            if ok:
                print("OK: semântica válida")
            else:
                print("FAILED: erros semânticos inesperados")
                for error in analyzer.errors:
                    print("  ", error)

        else:
            if not ok:
                print("OK: erro semântico detetado")
                for error in analyzer.errors:
                    print("  ", error)
            else:
                print("FAILED: devia ter falhado semanticamente")

    except Exception as e:
        print("EXCEPTION:", e)

    print()


def main():
    print("========== VALID SEMANTIC TESTS ==========")
    for name, code in VALID_TESTS.items():
        run_semantic_test(name, code, should_pass=True)

    print("========== INVALID SEMANTIC TESTS ==========")
    for name, code in INVALID_TESTS.items():
        run_semantic_test(name, code, should_pass=False)


if __name__ == "__main__":
    main()