import ply.yacc as yacc
from lexer.lexer import build_lexer, tokens



class ParserSyntaxError(Exception):
    pass



def node(kind, *children):
    return (kind, *children)



def p_program(p):
    """
    Program : ProgramUnitSeq
    """
    p[0] = node("program", p[1])



def p_program_unit_seq_single(p):
    """
    ProgramUnitSeq : ProgramUnit
    """
    p[0] = [p[1]]



def p_program_unit_seq_many(p):
    """
    ProgramUnitSeq : ProgramUnitSeq ProgramUnit
    """
    p[0] = p[1] + [p[2]]



def p_program_unit_main(p):
    """
    ProgramUnit : MainProgram
    """
    p[0] = p[1]



def p_program_unit_function(p):
    """
    ProgramUnit : FunctionSubprogram
    """
    p[0] = p[1]



def p_program_unit_subroutine(p):
    """
    ProgramUnit : SubroutineSubprogram
    """
    p[0] = p[1]



def p_main_program(p):
    """
    MainProgram : PROGRAM ID MainBody END
    """
    p[0] = node("main_program", node("name", p[2]), p[3])



def p_function_subprogram(p):
    """
    FunctionSubprogram : TypeSpec FUNCTION ID '(' OptParamList ')' SubprogramBody END
    """
    p[0] = node("function_subprogram", node("type", p[1]), node("name", p[3]), node("params", p[5]), p[7])



def p_subroutine_subprogram(p):
    """
    SubroutineSubprogram : SUBROUTINE ID '(' OptParamList ')' SubprogramBody END
    """
    p[0] = node("subroutine_subprogram", node("name", p[2]), node("params", p[4]), p[6])



def p_main_body_decl_exec(p):
    """
    MainBody : DeclPart ExecPart
    """
    p[0] = node("body", node("decls", p[1]), node("stmts", p[2]))



def p_main_body_exec(p):
    """
    MainBody : ExecPart
    """
    p[0] = node("body", node("decls", []), node("stmts", p[1]))



def p_subprogram_body_decl_exec(p):
    """
    SubprogramBody : DeclPart ExecPart
    """
    p[0] = node("body", node("decls", p[1]), node("stmts", p[2]))



def p_subprogram_body_exec(p):
    """
    SubprogramBody : ExecPart
    """
    p[0] = node("body", node("decls", []), node("stmts", p[1]))



def p_decl_part_single(p):
    """
    DeclPart : DeclarationStmt
    """
    p[0] = [p[1]]



def p_decl_part_many(p):
    """
    DeclPart : DeclPart DeclarationStmt
    """
    p[0] = p[1] + [p[2]]



def p_exec_part_single(p):
    """
    ExecPart : ExecutableStmt
    """
    p[0] = [p[1]]



def p_exec_part_many(p):
    """
    ExecPart : ExecPart ExecutableStmt
    """
    p[0] = p[1] + [p[2]]



def p_executable_stmt_labeled(p):
    """
    ExecutableStmt : LabeledExecutableStmt
    """
    p[0] = p[1]



def p_executable_stmt_unlabeled(p):
    """
    ExecutableStmt : UnlabeledExecutableStmt
    """
    p[0] = p[1]



def p_labeled_executable_stmt(p):
    """
    LabeledExecutableStmt : LABEL UnlabeledExecutableStmt
    """
    p[0] = node("labeled_stmt", node("label", p[1]), p[2])



def p_unlabeled_executable_stmt_assignment(p):
    """
    UnlabeledExecutableStmt : AssignmentStmt
    """
    p[0] = p[1]



def p_unlabeled_executable_stmt_if(p):
    """
    UnlabeledExecutableStmt : IfStmt
    """
    p[0] = p[1]



def p_unlabeled_executable_stmt_do(p):
    """
    UnlabeledExecutableStmt : DoStmt
    """
    p[0] = p[1]



def p_unlabeled_executable_stmt_goto(p):
    """
    UnlabeledExecutableStmt : GotoStmt
    """
    p[0] = p[1]



def p_unlabeled_executable_stmt_continue(p):
    """
    UnlabeledExecutableStmt : ContinueStmt
    """
    p[0] = p[1]



def p_unlabeled_executable_stmt_stop(p):
    """
    UnlabeledExecutableStmt : StopStmt
    """
    p[0] = p[1]



def p_unlabeled_executable_stmt_read(p):
    """
    UnlabeledExecutableStmt : ReadStmt
    """
    p[0] = p[1]



def p_unlabeled_executable_stmt_print(p):
    """
    UnlabeledExecutableStmt : PrintStmt
    """
    p[0] = p[1]



def p_unlabeled_executable_stmt_return(p):
    """
    UnlabeledExecutableStmt : ReturnStmt
    """
    p[0] = p[1]



def p_unlabeled_executable_stmt_call(p):
    """
    UnlabeledExecutableStmt : CallStmt
    """
    p[0] = p[1]



def p_declaration_stmt(p):
    """
    DeclarationStmt : TypeSpec DeclaratorList
    """
    p[0] = node("declaration", node("type", p[1]), node("decls", p[2]))



def p_type_spec_integer(p):
    """
    TypeSpec : INTEGER
    """
    p[0] = "integer"



def p_type_spec_real(p):
    """
    TypeSpec : REAL
    """
    p[0] = "real"



def p_type_spec_logical(p):
    """
    TypeSpec : LOGICAL
    """
    p[0] = "logical"



def p_declarator_list_single(p):
    """
    DeclaratorList : Declarator
    """
    p[0] = [p[1]]



def p_declarator_list_many(p):
    """
    DeclaratorList : DeclaratorList ',' Declarator
    """
    p[0] = p[1] + [p[3]]



def p_declarator_id(p):
    """
    Declarator : ID
    """
    p[0] = node("scalar_decl", p[1])



def p_declarator_array(p):
    """
    Declarator : ID '(' INT_CONST ')'
    """
    p[0] = node("array_decl", p[1], p[3])



def p_opt_param_list_params(p):
    """
    OptParamList : ParamList
    """
    p[0] = p[1]



def p_opt_param_list_empty(p):
    """
    OptParamList : Empty
    """
    p[0] = []



def p_param_list_single(p):
    """
    ParamList : ID
    """
    p[0] = [p[1]]



def p_param_list_many(p):
    """
    ParamList : ParamList ',' ID
    """
    p[0] = p[1] + [p[3]]



def p_assignment_stmt(p):
    """
    AssignmentStmt : Designator '=' Expr
    """
    p[0] = node("assignment", node("target", p[1]), node("value", p[3]))



def p_if_stmt_no_else(p):
    """
    IfStmt : IF '(' Expr ')' THEN ThenBlock ENDIF
    """
    p[0] = node("if", node("cond", p[3]), node("then", p[6]))



def p_if_stmt_else(p):
    """
    IfStmt : IF '(' Expr ')' THEN ThenBlock ELSE ElseBlock ENDIF
    """
    p[0] = node("if", node("cond", p[3]), node("then", p[6]), node("else", p[8]))



def p_then_block_single(p):
    """
    ThenBlock : ExecutableStmt
    """
    p[0] = [p[1]]



def p_then_block_many(p):
    """
    ThenBlock : ThenBlock ExecutableStmt
    """
    p[0] = p[1] + [p[2]]



def p_else_block_single(p):
    """
    ElseBlock : ExecutableStmt
    """
    p[0] = [p[1]]



def p_else_block_many(p):
    """
    ElseBlock : ElseBlock ExecutableStmt
    """
    p[0] = p[1] + [p[2]]



def p_do_stmt(p):
    """
    DoStmt : DO INT_CONST ID '=' Expr ',' Expr DoRangeTail DoBody
    """
    items = [
        node("label", p[2]),
        node("var", p[3]),
        node("start", p[5]),
        node("end", p[7]),
    ]
    if p[8] is not None:
        items.append(node("step", p[8]))
    items.append(node("body", p[9]))
    p[0] = node("do", *items)



def p_do_range_tail_step(p):
    """
    DoRangeTail : ',' Expr
    """
    p[0] = p[2]



def p_do_range_tail_empty(p):
    """
    DoRangeTail : Empty
    """
    p[0] = None



def p_do_body_only_end(p):
    """
    DoBody : LABEL CONTINUE
    """
    p[0] = node("do_body", node("end_label", p[1]), [])


def p_do_body_block_end(p):
    """
    DoBody : DoInnerBlock LABEL CONTINUE
    """
    p[0] = node("do_body", node("end_label", p[2]), p[1])



def p_do_inner_block_single(p):
    """
    DoInnerBlock : DoInnerStmt
    """
    p[0] = [p[1]]



def p_do_inner_block_many(p):
    """
    DoInnerBlock : DoInnerBlock DoInnerStmt
    """
    p[0] = p[1] + [p[2]]



def p_do_inner_stmt_assignment(p):
    """
    DoInnerStmt : AssignmentStmt
    """
    p[0] = p[1]



def p_do_inner_stmt_if(p):
    """
    DoInnerStmt : IfStmt
    """
    p[0] = p[1]



def p_do_inner_stmt_do(p):
    """
    DoInnerStmt : DoStmt
    """
    p[0] = p[1]



def p_do_inner_stmt_goto(p):
    """
    DoInnerStmt : GotoStmt
    """
    p[0] = p[1]



def p_do_inner_stmt_continue(p):
    """
    DoInnerStmt : ContinueStmt
    """
    p[0] = p[1]



def p_do_inner_stmt_stop(p):
    """
    DoInnerStmt : StopStmt
    """
    p[0] = p[1]



def p_do_inner_stmt_read(p):
    """
    DoInnerStmt : ReadStmt
    """
    p[0] = p[1]



def p_do_inner_stmt_print(p):
    """
    DoInnerStmt : PrintStmt
    """
    p[0] = p[1]



def p_do_inner_stmt_return(p):
    """
    DoInnerStmt : ReturnStmt
    """
    p[0] = p[1]



def p_do_inner_stmt_call(p):
    """
    DoInnerStmt : CallStmt
    """
    p[0] = p[1]



def p_goto_stmt(p):
    """
    GotoStmt : GOTO INT_CONST
    """
    p[0] = node("goto", node("target", p[2]))



def p_continue_stmt(p):
    """
    ContinueStmt : CONTINUE
    """
    p[0] = node("continue")



def p_stop_stmt(p):
    """
    StopStmt : STOP
    """
    p[0] = node("stop")



def p_return_stmt(p):
    """
    ReturnStmt : RETURN
    """
    p[0] = node("return")



def p_call_stmt(p):
    """
    CallStmt : CALL ID '(' OptArgList ')'
    """
    p[0] = node("call", node("name", p[2]), node("args", p[4]))



def p_read_stmt(p):
    """
    ReadStmt : READ TIMES ',' ReadList
    """
    p[0] = node("read", node("items", p[4]))



def p_read_list_single(p):
    """
    ReadList : ReadItem
    """
    p[0] = [p[1]]



def p_read_list_many(p):
    """
    ReadList : ReadList ',' ReadItem
    """
    p[0] = p[1] + [p[3]]



def p_read_item(p):
    """
    ReadItem : Designator
    """
    p[0] = p[1]



def p_print_stmt(p):
    """
    PrintStmt : PRINT TIMES ',' PrintList
    """
    p[0] = node("print", node("items", p[4]))



def p_print_list_single(p):
    """
    PrintList : PrintItem
    """
    p[0] = [p[1]]



def p_print_list_many(p):
    """
    PrintList : PrintList ',' PrintItem
    """
    p[0] = p[1] + [p[3]]



def p_print_item_expr(p):
    """
    PrintItem : Expr
    """
    p[0] = p[1]



def p_designator_id(p):
    """
    Designator : ID
    """
    p[0] = node("id", p[1])



def p_designator_index_or_call(p):
    """
    Designator : ID '(' OptArgList ')'
    """
    p[0] = node("call_or_index", p[1], p[3])



def p_opt_arg_list_args(p):
    """
    OptArgList : ArgList
    """
    p[0] = p[1]



def p_opt_arg_list_empty(p):
    """
    OptArgList : Empty
    """
    p[0] = []



def p_arg_list_single(p):
    """
    ArgList : Expr
    """
    p[0] = [p[1]]



def p_arg_list_many(p):
    """
    ArgList : ArgList ',' Expr
    """
    p[0] = p[1] + [p[3]]



def p_expr(p):
    """
    Expr : OrExpr
    """
    p[0] = p[1]



def p_or_expr_base(p):
    """
    OrExpr : AndExpr
    """
    p[0] = p[1]



def p_or_expr_rec(p):
    """
    OrExpr : OrExpr OR AndExpr
    """
    p[0] = node("binop", p[2], p[1], p[3])



def p_and_expr_base(p):
    """
    AndExpr : NotExpr
    """
    p[0] = p[1]



def p_and_expr_rec(p):
    """
    AndExpr : AndExpr AND NotExpr
    """
    p[0] = node("binop", p[2], p[1], p[3])



def p_not_expr_base(p):
    """
    NotExpr : RelExpr
    """
    p[0] = p[1]



def p_not_expr_not(p):
    """
    NotExpr : NOT NotExpr
    """
    p[0] = node("unop", p[1], p[2])



def p_rel_expr_base(p):
    """
    RelExpr : AddExpr
    """
    p[0] = p[1]



def p_rel_expr_relop(p):
    """
    RelExpr : AddExpr RelOp AddExpr
    """
    p[0] = node("binop", p[2], p[1], p[3])



def p_relop_lt(p):
    """
    RelOp : LT
    """
    p[0] = ".LT."



def p_relop_le(p):
    """
    RelOp : LE
    """
    p[0] = ".LE."



def p_relop_eq(p):
    """
    RelOp : EQ
    """
    p[0] = ".EQ."



def p_relop_ne(p):
    """
    RelOp : NE
    """
    p[0] = ".NE."



def p_relop_gt(p):
    """
    RelOp : GT
    """
    p[0] = ".GT."



def p_relop_ge(p):
    """
    RelOp : GE
    """
    p[0] = ".GE."



def p_add_expr_base(p):
    """
    AddExpr : MulExpr
    """
    p[0] = p[1]



def p_add_expr_plus(p):
    """
    AddExpr : AddExpr '+' MulExpr
    """
    p[0] = node("binop", "+", p[1], p[3])



def p_add_expr_minus(p):
    """
    AddExpr : AddExpr '-' MulExpr
    """
    p[0] = node("binop", "-", p[1], p[3])



def p_mul_expr_base(p):
    """
    MulExpr : PowExpr
    """
    p[0] = p[1]



def p_mul_expr_times(p):
    """
    MulExpr : MulExpr TIMES PowExpr
    """
    p[0] = node("binop", "*", p[1], p[3])



def p_mul_expr_div(p):
    """
    MulExpr : MulExpr '/' PowExpr
    """
    p[0] = node("binop", "/", p[1], p[3])



def p_pow_expr_base(p):
    """
    PowExpr : UnaryExpr
    """
    p[0] = p[1]



def p_pow_expr_power(p):
    """
    PowExpr : Primary POWER PowExpr
    """
    p[0] = node("binop", "**", p[1], p[3])



def p_unary_expr_primary(p):
    """
    UnaryExpr : Primary
    """
    p[0] = p[1]



def p_unary_expr_plus(p):
    """
    UnaryExpr : '+' UnaryExpr
    """
    p[0] = node("unop", "+", p[2])



def p_unary_expr_minus(p):
    """
    UnaryExpr : '-' UnaryExpr
    """
    p[0] = node("unop", "-", p[2])



def p_primary_int(p):
    """
    Primary : INT_CONST
    """
    p[0] = node("int", p[1])



def p_primary_real(p):
    """
    Primary : REAL_CONST
    """
    p[0] = node("real", p[1])



def p_primary_true(p):
    """
    Primary : TRUE
    """
    p[0] = node("logical", True)



def p_primary_false(p):
    """
    Primary : FALSE
    """
    p[0] = node("logical", False)



def p_primary_string(p):
    """
    Primary : STRING_CONST
    """
    p[0] = node("string", p[1])



def p_primary_designator(p):
    """
    Primary : Designator
    """
    p[0] = p[1]



def p_primary_group(p):
    """
    Primary : '(' Expr ')'
    """
    p[0] = p[2]



def p_empty(p):
    """
    Empty :
    """
    pass



def p_error(t):
    raise ParserSyntaxError(f"Unexpected token: {t.type if t else '$'}")



parser = yacc.yacc(write_tables=False, debug=True)



def parse(text):
    lexer = build_lexer()
    return parser.parse(text, lexer=lexer)



def dump_ast(node, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "


    if node is None:
        return


    if isinstance(node, list):
        for i, item in enumerate(node):
            dump_ast(item, prefix, i == len(node) - 1)
        return


    if not isinstance(node, tuple):
        print(prefix + connector + str(node))
        return


    kind = node[0]
    children = list(node[1:])


    if len(children) == 1 and not isinstance(children[0], (tuple, list)):
        print(prefix + connector + f"{kind}: {children[0]}")
        return


    if len(children) == 2 and all(not isinstance(c, (tuple, list)) for c in children):
        print(prefix + connector + f"{kind}: {children[0]}, {children[1]}")
        return


    print(prefix + connector + str(kind))
    new_prefix = prefix + ("    " if is_last else "│   ")


    for i, child in enumerate(children):
        if child is None:
            continue
        dump_ast(child, new_prefix, i == len(children) - 1)