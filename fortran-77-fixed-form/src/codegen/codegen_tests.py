from parser.parser_syntax import parse
from semantic.semantic_analyzer import SemanticAnalyzer
from codegen.code_generator import CodeGenerator


TESTS = {
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


def run_codegen_test(name, code):
    print(f"--- {name} ---")

    ast = parse(code)

    analyzer = SemanticAnalyzer()
    ok = analyzer.analyze(ast)

    if not ok:
        print("Semantic errors:")
        for error in analyzer.errors:
            print("  ", error)
        print()
        return

    generator = CodeGenerator(analyzer)
    vm_code = generator.generate(ast)

    print("\n".join(vm_code))
    print()


def main():
    for name, code in TESTS.items():
        run_codegen_test(name, code)


if __name__ == "__main__":
    main()