# Fortran 77 Compiler

A compiler for a subset of Fortran 77 (fixed-form, ANSI X3.9-1978), built for the Language Processing course at the University of Minho. Source code is compiled into instructions for the [EWVM virtual machine](https://ewvm.epl.di.uminho.pt/).

## Pipeline

Lexer &rarr; Parser &rarr; Semantic analysis &rarr; Code generation, producing EWVM (`.vm`) output from Fortran 77 (`.f`) source files.

## Tech stack

Python.

## Run locally

```bash
python src/main.py <source-file.f>
```

Example programs are available under `fortran-77-fixed-form/examples`.

## Team

- David Sousa e Silva
- João Rafael Martins da Costa
- Tomás Barroso Ramalhete
