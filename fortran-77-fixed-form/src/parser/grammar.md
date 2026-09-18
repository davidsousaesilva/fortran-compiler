# Gramática e arquitectura do parser para o subconjunto de Fortran 77

Este documento descreve a gramática adoptada para o parser do projecto e as decisões arquitecturais que a sustentam.

O parser reconhece o subconjunto de Fortran 77 pedido no projecto, incluindo programa principal, declarações de tipos, expressões aritméticas, relacionais e lógicas, controlo de fluxo `IF ... THEN ... ELSE ... ENDIF`, ciclos `DO` com label, `GOTO`, `READ`, `PRINT`, arrays, `FUNCTION` e `SUBROUTINE`.

A precedência das expressões é resolvida pela própria estrutura da gramática, sem usar tabelas auxiliares de precedência. A validação semântica é feita pelo próprio parser nas acções das produções, em conjunto com a construção da AST e a tabela de símbolos.

---

## Decisões arquitecturais

### Sintaxe e semântica

A gramática reconhece estruturas sintácticas; o parser trata a construção da AST e a validação semântica no próprio processo.  
Isto aplica-se à distinção entre variáveis, parâmetros, chamadas de função e acesso a elementos, que depende da informação semântica e não apenas da forma textual.

### Precedência por níveis

A hierarquia das expressões é organizada em níveis: `OrExpr`, `AndExpr`, `NotExpr`, `RelExpr`, `AddExpr`, `MulExpr`, `PowExpr`, `UnaryExpr` e `Primary`.  
Esta decomposição resolve precedência e associatividade de forma directa e compatível com LALR.

### Listas recursivas

As listas de declarações, instruções e argumentos usam recursão à esquerda, o que é apropriado para parsers LR/LALR e mantém o parse estável.  
O padrão aparece em `ProgramUnitSeq`, `DeclPart`, `ExecPart`, `DeclaratorList`, `ReadList`, `PrintList`, `ArgList` e blocos de instruções.

### Designators

`Designator` representa um identificador simples ou uma forma indexada/chamada `ID(...)`.  
A distinção entre variável, array e função é resolvida semanticamente, com base na tabela de símbolos.

### Entrada e saída

`PRINT` e `READ` usam listas de itens.  
As strings ficam no nível de `Primary`, evitando ambiguidades e reduzindo reduções duplicadas.

### Ciclos `DO`

O ciclo `DO` usa o label numérico que o lexer devolve como `INT_CONST`, enquanto o label de fecho da linha continua a ser reconhecido como `LABEL`.  
A validação de correspondência entre referências e labels é semântica.

---

## Gramática completa

```text
ProgramUnit -> MainProgram | FunctionSubprogram | SubroutineSubprogram

MainProgram -> PROGRAM ID MainBody END
FunctionSubprogram -> TypeSpec FUNCTION ID '(' OptParamList ')' SubprogramBody END
SubroutineSubprogram -> SUBROUTINE ID '(' OptParamList ')' SubprogramBody END

MainBody -> DeclPart ExecPart | ExecPart
SubprogramBody -> DeclPart ExecPart | ExecPart

DeclPart -> DeclarationStmt | DeclPart DeclarationStmt
ExecPart -> ExecutableStmt | ExecPart ExecutableStmt

ExecutableStmt -> LabeledExecutableStmt | UnlabeledExecutableStmt
LabeledExecutableStmt -> LABEL UnlabeledExecutableStmt

UnlabeledExecutableStmt -> AssignmentStmt | IfStmt | DoStmt | GotoStmt | ContinueStmt | StopStmt | ReadStmt | PrintStmt | ReturnStmt | CallStmt

DeclarationStmt -> TypeSpec DeclaratorList
TypeSpec -> INTEGER | REAL | LOGICAL
DeclaratorList -> Declarator | DeclaratorList ',' Declarator
Declarator -> ID | ID '(' INT_CONST ')'

OptParamList -> ParamList | Empty
ParamList -> ID | ParamList ',' ID

AssignmentStmt -> Designator '=' Expr

IfStmt -> IF '(' Expr ')' THEN ThenBlock ENDIF | IF '(' Expr ')' THEN ThenBlock ELSE ElseBlock ENDIF
ThenBlock -> ExecutableStmt | ThenBlock ExecutableStmt
ElseBlock -> ExecutableStmt | ElseBlock ExecutableStmt

DoStmt -> DO INT_CONST ID '=' Expr ',' Expr DoRangeTail DoBody
DoRangeTail -> ',' Expr | Empty
DoBody -> LABEL CONTINUE | DoInnerBlock LABEL CONTINUE
DoInnerBlock -> DoInnerStmt | DoInnerBlock DoInnerStmt
DoInnerStmt -> AssignmentStmt | IfStmt | DoStmt | GotoStmt | ContinueStmt | StopStmt | ReadStmt | PrintStmt | ReturnStmt | CallStmt

GotoStmt -> GOTO INT_CONST
ContinueStmt -> CONTINUE
StopStmt -> STOP
ReturnStmt -> RETURN
CallStmt -> CALL ID '(' OptArgList ')'

ReadStmt -> READ TIMES ',' ReadList
ReadList -> ReadItem | ReadList ',' ReadItem
ReadItem -> Designator

PrintStmt -> PRINT TIMES ',' PrintList
PrintList -> PrintItem | PrintList ',' PrintItem
PrintItem -> Expr

Designator -> ID | ID '(' OptArgList ')'
OptArgList -> ArgList | Empty
ArgList -> Expr | ArgList ',' Expr

Expr -> OrExpr
OrExpr -> AndExpr | OrExpr OR AndExpr
AndExpr -> NotExpr | AndExpr AND NotExpr
NotExpr -> RelExpr | NOT NotExpr
RelExpr -> AddExpr | AddExpr RelOp AddExpr
RelOp -> LT | LE | EQ | NE | GT | GE
AddExpr -> MulExpr | AddExpr '+' MulExpr | AddExpr '-' MulExpr
MulExpr -> PowExpr | MulExpr TIMES PowExpr | MulExpr '/' PowExpr
PowExpr -> UnaryExpr | Primary POWER PowExpr
UnaryExpr -> Primary | '+' UnaryExpr | '-' UnaryExpr

Primary -> INT_CONST | REAL_CONST | TRUE | FALSE | STRING_CONST | Designator | '(' Expr ')'
Empty ->
```

---

## Próximos passos

### 1. Construir a AST

Cada produção relevante deve devolver um nó AST adequado, em vez de apenas reconhecer a estrutura.  
Isto inclui programa, subprogramas, declarações, instruções, expressões e designators.

### 2. Implementar tabela de símbolos

A tabela de símbolos deve registar identificadores, tipo, categoria, aridade, parâmetros, informação de inicialização e contexto de escopo.  
É aqui que se resolvem as diferenças entre variável, array, função e subrotina.

### 3. Validar semântica

Durante o parsing devem ser verificados erros como declarações duplicadas, uso de variáveis não declaradas, uso antes de inicialização, incompatibilidades de tipos e chamadas com número incorrecto de argumentos.

### 4. Tratar escopos de subprogramas

Como o enunciado inclui `FUNCTION` e `SUBROUTINE`, o parser deve suportar novos níveis de escopo e encapsular correctamente parâmetros e variáveis locais.

### 5. Ligar ao pipeline final

No fim, o parser deve produzir uma AST válida e, ao mesmo tempo, confirmar a validade semântica suficiente para servir como base do resto do projecto.  
A gramática não precisa de ser mexida estruturalmente para isso.
