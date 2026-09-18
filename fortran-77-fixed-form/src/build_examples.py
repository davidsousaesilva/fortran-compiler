from pathlib import Path
from main import compile_file


def main():
    examples_dir = Path("../examples")

    for input_file in examples_dir.glob("*.f"):
        output_file = input_file.with_suffix(".vm")

        print(f"Compilar {input_file} -> {output_file}")
        exit_code = compile_file(input_file, output_file)

        if exit_code != 0:
            print(f"Falhou: {input_file}")


if __name__ == "__main__":
    main()