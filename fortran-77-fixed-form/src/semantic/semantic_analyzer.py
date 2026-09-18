from semantic.symbol_table import Scope, SemanticError


class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope

        self.scopes = {}

        self.errors = []

        # Labels definidos e GOTOs encontrados
        self.labels = set()
        self.gotos = []

        # Anotações de tipo:
        # id(node) -> tipo
        self.types = {}

        # Funções built-in suportadas
        self.builtins = {
            "MOD": {
                "params": ["integer", "integer"],
                "return_type": "integer",
            }
        }

    # =========================================================
    # API principal
    # =========================================================

    def analyze(self, ast):
        try:
            self.visit(ast)

            for label in self.gotos:
                if label not in self.labels:
                    raise SemanticError(f"GOTO references undefined label {label}")

            return True

        except SemanticError as e:
            self.errors.append(str(e))
            return False

    # =========================================================
    # Helpers
    # =========================================================

    def annotate(self, node, type_):
        self.types[id(node)] = type_
        return type_

    def get_type(self, node):
        return self.types.get(id(node))

    def expect_type(self, actual, expected, context):
        if actual != expected:
            raise SemanticError(
                f"Type error in {context}: expected {expected}, got {actual}"
            )

    def is_numeric(self, type_):
        return type_ in ("integer", "real")

    def numeric_result_type(self, left_type, right_type):
        if not self.is_numeric(left_type) or not self.is_numeric(right_type):
            raise SemanticError(
                f"Arithmetic operator requires numeric operands, got {left_type} and {right_type}"
            )

        if left_type == "real" or right_type == "real":
            return "real"

        return "integer"

    def compatible_assignment(self, target_type, value_type):
        if target_type == value_type:
            return True

        # Promoção simples: INTEGER pode ser atribuído a REAL
        if target_type == "real" and value_type == "integer":
            return True

        return False

    # =========================================================
    # Dispatcher genérico
    # =========================================================

    def visit(self, node):
        if node is None:
            return None

        if isinstance(node, list):
            for item in node:
                self.visit(item)
            return None

        if not isinstance(node, tuple):
            return None

        kind = node[0]
        method = getattr(self, f"visit_{kind}", None)

        if method is None:
            raise SemanticError(f"No semantic rule for node kind '{kind}'")

        return method(node)

    # =========================================================
    # Programas e subprogramas
    # =========================================================

    def visit_program(self, node):
        _, units = node

        # Primeira passagem:
        # declarar funções e subrotinas globais antes de analisar o corpo
        for unit in units:
            if unit[0] == "function_subprogram":
                self.predeclare_function(unit)
            elif unit[0] == "subroutine_subprogram":
                self.predeclare_subroutine(unit)

        # Segunda passagem:
        # validar todos os program units
        for unit in units:
            self.visit(unit)

    def predeclare_function(self, node):
        _, type_node, name_node, params_node, body = node

        return_type = type_node[1]
        name = name_node[1]
        params = params_node[1]

        self.global_scope.declare(
            name,
            return_type,
            kind="function",
            initialized=True,
            params=[p.upper() for p in params],
            return_type=return_type,
        )

    def predeclare_subroutine(self, node):
        _, name_node, params_node, body = node

        name = name_node[1]
        params = params_node[1]

        self.global_scope.declare(
            name,
            "subroutine",
            kind="subroutine",
            initialized=True,
            params=[p.upper() for p in params],
            return_type=None,
        )

    def visit_main_program(self, node):
        _, name_node, body = node

        program_name = name_node[1].upper()

        old_scope = self.current_scope
        self.current_scope = Scope(program_name, parent=self.global_scope)

        self.scopes[program_name] = self.current_scope

        self.visit(body)

        self.current_scope = old_scope

    def visit_function_subprogram(self, node):
        _, type_node, name_node, params_node, body = node

        function_name = name_node[1].upper()
        return_type = type_node[1]
        params = params_node[1]
        

        old_scope = self.current_scope
        self.current_scope = Scope(function_name, parent=self.global_scope)
        
        self.scopes[function_name] = self.current_scope

        # Em Fortran, o nome da função é usado como variável de retorno
        self.current_scope.declare(
            function_name,
            return_type,
            kind="function_result",
            initialized=False,
        )

        # Parâmetros começam com tipo unknown.
        # Depois são tipados pelas declarações INTEGER N, B, etc.
        for param in params:
            self.current_scope.declare(
                param,
                "unknown",
                kind="parameter",
                initialized=True,
            )

        self.visit(body)

        result_symbol = self.current_scope.lookup(function_name)

        if not result_symbol.initialized:
            raise SemanticError(
                f"Function '{function_name}' does not assign a return value to its own name"
            )

        self.current_scope = old_scope

    def visit_subroutine_subprogram(self, node):
        _, name_node, params_node, body = node

        subroutine_name = name_node[1].upper()
        params = params_node[1]

        old_scope = self.current_scope
        self.current_scope = Scope(subroutine_name, parent=self.global_scope)

        self.scopes[subroutine_name] = self.current_scope

        for param in params:
            self.current_scope.declare(
                param,
                "unknown",
                kind="parameter",
                initialized=True,
            )

        self.visit(body)

        self.current_scope = old_scope

    # =========================================================
    # Body, declarations, statement wrappers
    # =========================================================

    def visit_body(self, node):
        _, decls_node, stmts_node = node

        self.visit(decls_node)
        self.visit(stmts_node)

    def visit_decls(self, node):
        _, decls = node
        self.visit(decls)

    def visit_stmts(self, node):
        _, stmts = node
        self.visit(stmts)

    def visit_then(self, node):
        _, stmts = node
        self.visit(stmts)

    def visit_else(self, node):
        _, stmts = node
        self.visit(stmts)

    # =========================================================
    # Declarações
    # =========================================================

    def visit_declaration(self, node):
        _, type_node, decls_node = node

        type_ = type_node[1]
        decls = decls_node[1]

        for decl in decls:
            if decl[0] == "scalar_decl":
                self.handle_scalar_declaration(decl, type_)

            elif decl[0] == "array_decl":
                self.handle_array_declaration(decl, type_)

            else:
                raise SemanticError(f"Unknown declaration node: {decl}")

    def handle_scalar_declaration(self, decl, type_):
        _, name = decl
        key = name.upper()

        # Caso especial 1:
        # parâmetro de função/subrotina já declarado como unknown.
        if self.current_scope.exists_local(key):
            symbol = self.current_scope.symbols[key]

            if symbol.kind == "parameter" and symbol.type == "unknown":
                symbol.type = type_
                return

            raise SemanticError(f"Identifier '{name}' already declared")

        # Caso especial 2:
        # declaração local do tipo de uma função externa.
        #
        # Exemplo:
        #   INTEGER CONVRT
        #   RESULT = CONVRT(NUM, BASE)
        #
        # e depois:
        #   INTEGER FUNCTION CONVRT(N, B)
        #
        # Neste caso, CONVRT não deve ser tratado como variável local,
        # mas como referência à função global já pré-declarada.
        try:
            global_symbol = self.global_scope.lookup(key)

            if global_symbol.kind == "function":
                if global_symbol.return_type != type_:
                    raise SemanticError(
                        f"Function '{name}' declared as {type_}, but defined as {global_symbol.return_type}"
                    )

                self.current_scope.declare(
                    name,
                    type_,
                    kind="function",
                    initialized=True,
                    params=global_symbol.params,
                    return_type=global_symbol.return_type,
                )
                return

        except SemanticError:
            # Se não existir no global scope, segue como variável normal.
            pass

        self.current_scope.declare(
            name,
            type_,
            kind="variable",
            initialized=False,
        )

    def handle_array_declaration(self, decl, type_):
        _, name, size = decl

        if size <= 0:
            raise SemanticError(f"Array '{name}' must have positive size")

        self.current_scope.declare(
            name,
            type_,
            kind="array",
            initialized=False,
            size=size,
        )

    # =========================================================
    # Statements
    # =========================================================

    def visit_labeled_stmt(self, node):
        _, label_node, stmt = node

        label = label_node[1]

        if label in self.labels:
            raise SemanticError(f"Duplicate label {label}")

        self.labels.add(label)

        self.visit(stmt)

    def visit_assignment(self, node):
        _, target_node, value_node = node

        target = target_node[1]
        value = value_node[1]

        target_type = self.eval_designator(target, as_target=True)
        value_type = self.eval_expr(value)

        if not self.compatible_assignment(target_type, value_type):
            raise SemanticError(
                f"Cannot assign expression of type {value_type} to target of type {target_type}"
            )

        self.mark_initialized(target)

    def visit_if(self, node):
        cond_node = node[1]
        then_node = node[2]

        cond_expr = cond_node[1]
        cond_type = self.eval_expr(cond_expr)

        self.expect_type(cond_type, "logical", "IF condition")

        self.visit(then_node)

        if len(node) == 4:
            else_node = node[3]
            self.visit(else_node)

    def visit_do(self, node):
        # Formato esperado:
        # ("do",
        #   ("label", n),
        #   ("var", i),
        #   ("start", expr),
        #   ("end", expr),
        #   opcional ("step", expr),
        #   ("body", do_body)
        # )

        label = node[1][1]
        var_name = node[2][1]
        start_expr = node[3][1]
        end_expr = node[4][1]

        index = 5
        step_expr = None

        if node[index][0] == "step":
            step_expr = node[index][1]
            index += 1

        body_node = node[index][1]

        var_symbol = self.current_scope.lookup(var_name)

        self.expect_type(var_symbol.type, "integer", "DO variable")

        start_type = self.eval_expr(start_expr)
        end_type = self.eval_expr(end_expr)

        self.expect_type(start_type, "integer", "DO start expression")
        self.expect_type(end_type, "integer", "DO end expression")

        if step_expr is not None:
            step_type = self.eval_expr(step_expr)
            self.expect_type(step_type, "integer", "DO step expression")

        var_symbol.initialized = True

        self.validate_do_body(label, body_node)

    def validate_do_body(self, do_label, body_node):
        if body_node[0] != "do_body":
            raise SemanticError("Invalid DO body")
        
        # ("do_body", ("end_label", n), stmts)
        if len(body_node) == 3 and isinstance(body_node[1], tuple):
            end_label_node = body_node[1]
            inner_stmts = body_node[2]

            if end_label_node[0] != "end_label":
                raise SemanticError("Invalid DO end label node")

            end_label = end_label_node[1]

            if end_label != do_label:
                raise SemanticError(
                    f"DO label mismatch: DO uses label {do_label}, but loop ends at label {end_label}"
                )

            if end_label in self.labels:
                raise SemanticError(f"Duplicate label {end_label}")

            self.labels.add(end_label)
            self.visit(inner_stmts)
            return

        # ("do_body", stmts)
        if len(body_node) == 2:
            inner_stmts = body_node[1]
            self.visit(inner_stmts)
            return

        raise SemanticError("Invalid DO body structure")

    def visit_goto(self, node):
        _, target_node = node
        label = target_node[1]

        self.gotos.append(label)

    def visit_continue(self, node):
        return None

    def visit_stop(self, node):
        return None

    def visit_return(self, node):
        return None

    def visit_call(self, node):
        _, name_node, args_node = node

        name = name_node[1].upper()
        args = args_node[1]

        symbol = self.current_scope.lookup(name)

        if symbol.kind != "subroutine":
            raise SemanticError(
                f"CALL expects a subroutine, but '{name}' is {symbol.kind}"
            )

        if len(args) != len(symbol.params):
            raise SemanticError(
                f"Subroutine '{name}' expects {len(symbol.params)} arguments, got {len(args)}"
            )

        for arg in args:
            self.eval_expr(arg)

    def visit_read(self, node):
        _, items_node = node
        items = items_node[1]

        for item in items:
            self.eval_designator(item, as_target=True)
            self.mark_initialized(item)

    def visit_print(self, node):
        _, items_node = node
        items = items_node[1]

        for item in items:
            self.eval_expr(item)

    # =========================================================
    # Expressões
    # =========================================================

    def eval_expr(self, node):
        kind = node[0]

        if kind == "int":
            return self.annotate(node, "integer")

        if kind == "real":
            return self.annotate(node, "real")

        if kind == "logical":
            return self.annotate(node, "logical")

        if kind == "string":
            return self.annotate(node, "string")

        if kind == "id":
            return self.eval_designator(node, as_target=False)

        if kind == "call_or_index":
            return self.eval_designator(node, as_target=False)

        if kind == "binop":
            return self.eval_binop(node)

        if kind == "unop":
            return self.eval_unop(node)

        raise SemanticError(f"Invalid expression node: {node}")

    def eval_binop(self, node):
        _, op, left, right = node

        left_type = self.eval_expr(left)
        right_type = self.eval_expr(right)

        if op in ("+", "-", "*", "/", "**"):
            result_type = self.numeric_result_type(left_type, right_type)
            return self.annotate(node, result_type)

        if op in (".LT.", ".LE.", ".GT.", ".GE."):
            self.numeric_result_type(left_type, right_type)
            return self.annotate(node, "logical")

        if op in (".EQ.", ".NE."):
            if left_type == right_type:
                return self.annotate(node, "logical")

            if self.is_numeric(left_type) and self.is_numeric(right_type):
                return self.annotate(node, "logical")

            raise SemanticError(
                f"Cannot compare values of type {left_type} and {right_type}"
            )

        if op in (".AND.", ".OR."):
            self.expect_type(left_type, "logical", f"left operand of {op}")
            self.expect_type(right_type, "logical", f"right operand of {op}")
            return self.annotate(node, "logical")

        raise SemanticError(f"Unknown binary operator {op}")

    def eval_unop(self, node):
        _, op, expr = node

        expr_type = self.eval_expr(expr)

        if op in ("+", "-"):
            if not self.is_numeric(expr_type):
                raise SemanticError(
                    f"Unary operator {op} requires numeric expression, got {expr_type}"
                )

            return self.annotate(node, expr_type)

        if op == ".NOT.":
            self.expect_type(expr_type, "logical", "NOT expression")
            return self.annotate(node, "logical")

        raise SemanticError(f"Unknown unary operator {op}")

    # =========================================================
    # Designators: variáveis, arrays, funções
    # =========================================================

    def eval_designator(self, node, as_target=False):
        kind = node[0]

        if kind == "id":
            return self.eval_id(node, as_target=as_target)

        if kind == "call_or_index":
            return self.eval_call_or_index(node, as_target=as_target)

        raise SemanticError(f"Invalid designator: {node}")

    def eval_id(self, node, as_target=False):
        _, name = node

        symbol = self.current_scope.lookup(name)

        if symbol.kind == "array":
            raise SemanticError(f"Array '{name}' used without index")

        if symbol.kind == "function":
            raise SemanticError(f"Function '{name}' used without arguments")

        if not as_target and not symbol.initialized:
            raise SemanticError(f"Variable '{name}' used before initialization")

        return self.annotate(node, symbol.type)

    def eval_call_or_index(self, node, as_target=False):
        _, name, args = node

        key = name.upper()

        # Built-in function, por exemplo MOD(NUM, I)
        if key in self.builtins:
            if as_target:
                raise SemanticError(f"Function call '{name}' cannot be assignment target")

            return self.eval_builtin_call(node)

        symbol = self.current_scope.lookup(key)

        if symbol.kind == "array":
            return self.eval_array_access(node, symbol, as_target=as_target)

        if symbol.kind == "function":
            if as_target:
                raise SemanticError(f"Function call '{name}' cannot be assignment target")

            return self.eval_user_function_call(node, symbol)

        raise SemanticError(f"Identifier '{name}' is not callable or indexable")

    def eval_builtin_call(self, node):
        _, name, args = node

        key = name.upper()
        info = self.builtins[key]

        expected_params = info["params"]

        if len(args) != len(expected_params):
            raise SemanticError(
                f"Function '{name}' expects {len(expected_params)} arguments, got {len(args)}"
            )

        for arg, expected_type in zip(args, expected_params):
            actual_type = self.eval_expr(arg)
            self.expect_type(actual_type, expected_type, f"argument of {name}")

        return self.annotate(node, info["return_type"])

    def eval_user_function_call(self, node, symbol):
        _, name, args = node

        if len(args) != len(symbol.params):
            raise SemanticError(
                f"Function '{name}' expects {len(symbol.params)} arguments, got {len(args)}"
            )

        for arg in args:
            self.eval_expr(arg)

        return self.annotate(node, symbol.return_type)

    def eval_array_access(self, node, symbol, as_target=False):
        _, name, args = node

        if len(args) != 1:
            raise SemanticError(f"Array '{name}' expects exactly one index")

        index_type = self.eval_expr(args[0])

        self.expect_type(index_type, "integer", f"index of array {name}")

        return self.annotate(node, symbol.type)

    def mark_initialized(self, node):
        kind = node[0]

        if kind == "id":
            _, name = node
            symbol = self.current_scope.lookup(name)
            symbol.initialized = True
            return

        if kind == "call_or_index":
            _, name, args = node
            symbol = self.current_scope.lookup(name)

            if symbol.kind != "array":
                raise SemanticError(f"Cannot assign to '{name}'")

            symbol.initialized = True
            return

        raise SemanticError(f"Invalid assignment target: {node}")