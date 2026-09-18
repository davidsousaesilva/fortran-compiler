import argparse
import sys
from pathlib import Path

from parser.parser_syntax import parse, dump_ast
from semantic.semantic_analyzer import SemanticAnalyzer
from codegen.code_generator import CodeGenerator


def compile_file(input_path, output_path=None, show_ast=False):
    input_path = Path(input_path)

    if not input_path.exists():
        print(f"Erro: ficheiro não encontrado: {input_path}", file=sys.stderr)
        return 1

    source_code = input_path.read_text(encoding="utf-8")

    try:
        ast = parse(source_code)

        if show_ast:
            print("========== AST ==========")
            dump_ast(ast)
            print()

        analyzer = SemanticAnalyzer()
        ok = analyzer.analyze(ast)

        if not ok:
            print("Erro semântico:", file=sys.stderr)
            for error in analyzer.errors:
                print(f"  - {error}", file=sys.stderr)
            return 1

        generator = CodeGenerator(analyzer)
        vm_code = generator.generate(ast)

        vm_text = "\n".join(vm_code) + "\n"

        if output_path is None:
            print(vm_text, end="")
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(vm_text, encoding="utf-8")
            print(f"Código VM gerado em: {output_path}")

        return 0

    except Exception as e:
        print(f"Erro durante a compilação: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Compilador Fortran 77 fixed-form para código da máquina virtual."
    )

    parser.add_argument(
        "input",
        help="Ficheiro Fortran 77 de entrada."
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Ficheiro de saída com código VM. Se omitido, escreve para stdout."
    )

    parser.add_argument(
        "--ast",
        action="store_true",
        help="Mostra a AST gerada pelo parser."
    )

    args = parser.parse_args()

    exit_code = compile_file(
        input_path=args.input,
        output_path=args.output,
        show_ast=args.ast
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()