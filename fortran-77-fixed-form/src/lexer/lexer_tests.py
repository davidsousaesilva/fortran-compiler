from lexer import build_lexer


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


LEXER_INVALID_TESTS = {
    "letters_in_columns_1_5": r"""  ABC
      PROGRAM TESTE
      END""",

    "comment_wrong_column_2": r""" C ESTE COMENTARIO ESTA NA COLUNA 2
      PROGRAM TESTE
      END""",

    "comment_wrong_column_4": r"""   *COMENTARIO NA COLUNA 4
      END""",

    "code_starts_too_early": r"""    PRINT *, 'OLA'
      END""",

    "continuation_in_wrong_column_4": r"""    X  PRINT *, 'OLA'
      END""",

    "illegal_symbol": r"""      PROGRAM BAD
      A = 3 @ 4
      END""",

    "unterminated_string": r"""      PROGRAM BADSTR
      PRINT *, 'isto nao fecha
      END""",

    "mixed_prefix_error": r"""   1A STOP
      END""",

    "text_after_bad_prefix": r"""  AB12 PRINT *, 'ERRO'
      END""",
}


def tokenize(text):
    lexer = build_lexer()
    lexer.input(text)
    return [(tok.type, tok.value, tok.lineno, tok.lexpos) for tok in lexer]


def show_tokens(name, text):
    print(f"--- {name} ---")
    for token in tokenize(text):
        print(token)
    print()


def run_suite(title, tests):
    print(f"========== {title} ==========")
    for name, text in tests.items():
        show_tokens(name, text)


def main():
    run_suite("VALID PROGRAMS", VALID_TESTS)
    # run_suite("INVALID PROGRAMS", LEXER_INVALID_TESTS)


if __name__ == "__main__":
    main()