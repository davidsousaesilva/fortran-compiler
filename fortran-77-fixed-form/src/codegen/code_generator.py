class CodeGenerationError(Exception):
    pass


class CodeGenerator:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.current_scope = None
        self.current_scope_base = 0

        self.code = []
        self.label_counter = 0

        #Base global de cada scope
        self.scope_bases = {}

        # Estado atual quando estamos dentro de uma função
        self.current_function_name = None
        self.function_return_emitted = False

    # =========================================================
    # API principal
    # =========================================================

    def generate(self, ast):
        self.code = []
        self.visit(ast)
        return self.code

    def emit(self, instr):
        self.code.append(instr)

    def sanitize_label(self, text):
        return "".join(ch for ch in str(text).upper() if ch.isalnum())


    def new_label(self, prefix):
        self.label_counter += 1
        clean_prefix = self.sanitize_label(prefix)
        return f"{clean_prefix}{self.label_counter}"


    def function_label(self, name):
        return f"F{self.sanitize_label(name)}"


    def fortran_label(self, label):
        scope_name = self.sanitize_label(self.current_scope.name)
        return f"L{scope_name}{label}"


    def global_index(self, name):
        symbol = self.current_scope.lookup(name)

        if symbol.index is None:
            raise CodeGenerationError(f"Symbol '{name}' has no memory index")

        return self.current_scope_base + symbol.index


    def absolute_index(self, scope, symbol):
        base = self.scope_bases[scope.name.upper()]
        return base + symbol.index

    # =========================================================
    # Dispatcher
    # =========================================================

    def visit(self, node):
        if node is None:
            return

        if isinstance(node, list):
            for item in node:
                self.visit(item)
            return

        if not isinstance(node, tuple):
            return

        kind = node[0]
        method = getattr(self, f"visit_{kind}", None)

        if method is None:
            raise CodeGenerationError(f"No codegen rule for node kind '{kind}'")

        return method(node)

    # =========================================================
    # Programas
    # =========================================================

    def visit_program(self, node):
        _, units = node

        main_units = [u for u in units if u[0] == "main_program"]
        function_units = [u for u in units if u[0] == "function_subprogram"]
        subroutine_units = [u for u in units if u[0] == "subroutine_subprogram"]

        if len(main_units) != 1:
            raise CodeGenerationError("Expected exactly one main program")

        # Calcular bases globais de todos os scopes
        self.compute_scope_bases(units)

        total_size = sum(scope.next_index for scope in self.analyzer.scopes.values())

        if total_size > 0:
            self.emit(f"PUSHN {total_size}")

        # Gerar main primeiro
        self.visit(main_units[0])

        self.emit("STOP")

        # Gerar funções depois do STOP.
        # Podem ser chamadas via PUSHA label + CALL.
        for unit in function_units:
            self.visit(unit)

        # Subrotinas ficam preparadas (Não foi implementado)
        for unit in subroutine_units:
            self.visit(unit)

    def visit_main_program(self, node):
        _, name_node, body = node

        program_name = name_node[1].upper()

        self.current_scope = self.analyzer.scopes[program_name]
        self.current_scope_base = self.scope_bases[program_name]

        self.visit(body)

    def visit_function_subprogram(self, node):
        _, type_node, name_node, params_node, body = node

        function_name = name_node[1].upper()

        old_scope = self.current_scope
        old_base = self.current_scope_base
        old_function = self.current_function_name
        old_return_state = self.function_return_emitted

        self.current_scope = self.analyzer.scopes[function_name]
        self.current_scope_base = self.scope_bases[function_name]
        self.current_function_name = function_name
        self.function_return_emitted = False

        self.emit(f"{self.function_label(function_name)}:")

        self.visit(body)

        # Se a função não teve RETURN explícito,
        # devolve o valor guardado no nome da função.
        if not self.function_return_emitted:
            result_index = self.global_index(function_name)
            self.emit(f"PUSHG {result_index}")
            self.emit("RETURN")

        self.current_scope = old_scope
        self.current_scope_base = old_base
        self.current_function_name = old_function
        self.function_return_emitted = old_return_state

    def visit_subroutine_subprogram(self, node):
        raise CodeGenerationError("Subroutine code generation not implemented yet")

    def allocate_globals(self):
        total_size = self.current_scope.next_index

        for _ in range(total_size):
            self.emit("PUSHI 0")

    # =========================================================
    # Body / wrappers
    # =========================================================

    def visit_body(self, node):
        _, decls_node, stmts_node = node

        # Declarações não geram código diretamente.
        # A memória já foi reservada em allocate_globals().
        self.visit(stmts_node)

    def visit_decls(self, node):
        return

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
    # Statements
    # =========================================================

    def visit_labeled_stmt(self, node):
        _, label_node, stmt = node

        label = label_node[1]
        self.emit(f"{self.fortran_label(label)}:")

        self.visit(stmt)

    def visit_assignment(self, node):
        _, target_node, value_node = node

        target = target_node[1]
        value = value_node[1]

        if target[0] == "id":
            self.gen_expr(value)
            self.store_designator(target)
            return

        if target[0] == "call_or_index":
            # Para arrays, é mais seguro gerar primeiro o endereço,
            # depois o valor, e finalmente STORE.
            self.gen_address(target)
            self.gen_expr(value)
            self.emit("STORE 0")
            return

        raise CodeGenerationError(f"Invalid assignment target: {target}")

    def visit_if(self, node):
        cond_node = node[1]
        then_node = node[2]

        else_label = self.new_label("ELSE")
        end_label = self.new_label("ENDIF")

        cond_expr = cond_node[1]

        self.gen_expr(cond_expr)
        self.emit(f"JZ {else_label}")

        self.visit(then_node)
        self.emit(f"JUMP {end_label}")

        self.emit(f"{else_label}:")

        if len(node) == 4:
            else_node = node[3]
            self.visit(else_node)

        self.emit(f"{end_label}:")

    def visit_do(self, node):
        do_label = node[1][1]
        var_name = node[2][1]
        start_expr = node[3][1]
        end_expr = node[4][1]

        index = 5
        step_expr = None

        if node[index][0] == "step":
            step_expr = node[index][1]
            index += 1

        body_wrapper = node[index]
        body_node = body_wrapper[1]

        begin_label = self.new_label(f"DO{do_label}BEGIN")
        end_label = self.new_label(f"DO{do_label}END")

        var_symbol = self.current_scope.lookup(var_name)
        var_index = self.current_scope_base + var_symbol.index

        # i = start
        self.gen_expr(start_expr)
        self.emit(f"STOREG {var_index}")

        self.emit(f"{begin_label}:")

        # condição: i <= end
        self.emit(f"PUSHG {var_index}")
        self.gen_expr(end_expr)
        self.emit("INFEQ")
        self.emit(f"JZ {end_label}")

        # corpo
        self.gen_do_body(body_node)

        # incremento
        self.emit(f"PUSHG {var_index}")

        if step_expr is not None:
            self.gen_expr(step_expr)
        else:
            self.emit("PUSHI 1")

        self.emit("ADD")
        self.emit(f"STOREG {var_index}")

        self.emit(f"JUMP {begin_label}")
        self.emit(f"{end_label}:")

    def gen_do_body(self, body_node):
        if body_node[0] != "do_body":
            raise CodeGenerationError("Invalid DO body")

        # ("do_body", ("end_label", n), stmts)
        if len(body_node) == 3:
            stmts = body_node[2]
            self.visit(stmts)
            return

        # ("do_body", stmts)
        if len(body_node) == 2:
            stmts = body_node[1]
            self.visit(stmts)
            return

        raise CodeGenerationError("Invalid DO body structure")

    def visit_goto(self, node):
        _, target_node = node
        target = target_node[1]

        self.emit(f"JUMP {self.fortran_label(target)}")

    def visit_continue(self, node):
        # CONTINUE não faz nada.
        self.emit("NOP")

    def visit_stop(self, node):
        self.emit("STOP")

    def visit_return(self, node):
        if self.current_function_name is not None:
            result_index = self.global_index(self.current_function_name)
            self.emit(f"PUSHG {result_index}")
            self.emit("RETURN")
            self.function_return_emitted = True
            return

        self.emit("RETURN")

    def visit_read(self, node):
        _, items_node = node
        items = items_node[1]

        for item in items:
            item_type = self.analyzer.get_type(item)

            if item_type is None:
                item_type = self.infer_designator_type(item)

            # Caso 1: READ para variável escalar
            if item[0] == "id":
                self.emit("READ")

                if item_type == "integer":
                    self.emit("ATOI")
                elif item_type == "real":
                    self.emit("ATOF")
                elif item_type == "logical":
                    self.emit("ATOI")
                else:
                    raise CodeGenerationError(f"READ not supported for type {item_type}")

                self.store_designator(item)
                continue

            # Caso 2: READ para posição de array, exemplo NUMS(I)
            if item[0] == "call_or_index":
                # Primeiro calcular o endereço
                self.gen_address(item)

                # Depois ler o valor
                self.emit("READ")

                if item_type == "integer":
                    self.emit("ATOI")
                elif item_type == "real":
                    self.emit("ATOF")
                elif item_type == "logical":
                    self.emit("ATOI")
                else:
                    raise CodeGenerationError(f"READ not supported for type {item_type}")

                # Guardar valor no endereço calculado
                self.emit("STORE 0")
                continue

            raise CodeGenerationError(f"Invalid READ item: {item}")

    def visit_print(self, node):
        _, items_node = node
        items = items_node[1]

        for item in items:
            item_type = self.analyzer.get_type(item)

            if item_type is None:
                item_type = self.infer_expr_type(item)

            self.gen_expr(item)

            if item_type == "integer":
                self.emit("WRITEI")
            elif item_type == "real":
                self.emit("WRITEF")
            elif item_type == "logical":
                self.emit("WRITEI")
            elif item_type == "string":
                self.emit("WRITES")
            else:
                raise CodeGenerationError(f"PRINT not supported for type {item_type}")

        # newline simples
        self.emit('PUSHS "\\n"')
        self.emit("WRITES")

    def visit_call(self, node):
        raise CodeGenerationError("Subroutine CALL code generation not implemented yet")

    # =========================================================
    # Expressões
    # =========================================================

    def gen_expr(self, node):
        kind = node[0]

        if kind == "int":
            self.emit(f"PUSHI {node[1]}")
            return

        if kind == "real":
            self.emit(f"PUSHF {node[1]}")
            return

        if kind == "logical":
            self.emit("PUSHI 1" if node[1] else "PUSHI 0")
            return

        if kind == "string":
            self.emit(f'PUSHS "{self.clean_string(node[1])}"')
            return

        if kind == "id":
            symbol = self.current_scope.lookup(node[1])
            self.emit(f"PUSHG {self.current_scope_base + symbol.index}")
            return

        if kind == "call_or_index":
            name = node[1].upper()

            if name == "MOD":
                args = node[2]
                self.gen_expr(args[0])
                self.gen_expr(args[1])
                self.emit("MOD")
                return

            symbol = self.current_scope.lookup(name)

            if symbol.kind == "array":
                self.gen_address(node)
                self.emit("LOAD 0")
                return

            if symbol.kind == "function":
                self.gen_user_function_call(name, node[2])
                return

            raise CodeGenerationError(f"Invalid call/index expression: {node}")

        if kind == "binop":
            self.gen_binop(node)
            return

        if kind == "unop":
            self.gen_unop(node)
            return

        raise CodeGenerationError(f"Invalid expression node: {node}")

    def gen_user_function_call(self, name, args):
        function_name = name.upper()

        if function_name not in self.analyzer.scopes:
            raise CodeGenerationError(f"Unknown function scope '{function_name}'")

        function_scope = self.analyzer.scopes[function_name]
        function_base = self.scope_bases[function_name]

        function_symbol = self.analyzer.global_scope.lookup(function_name)
        param_names = function_symbol.params

        if len(args) != len(param_names):
            raise CodeGenerationError(
                f"Function '{function_name}' expects {len(param_names)} arguments, got {len(args)}"
            )

        # Copiar argumentos para as posições globais dos parâmetros
        for arg, param_name in zip(args, param_names):
            param_symbol = function_scope.lookup(param_name)

            self.gen_expr(arg)
            self.emit(f"STOREG {function_base + param_symbol.index}")

        # Chamar função
        self.emit(f"PUSHA {self.function_label(function_name)}")
        self.emit("CALL")



    def gen_binop(self, node):
        _, op, left, right = node

        result_type = self.analyzer.get_type(node)

        self.gen_expr(left)
        self.gen_expr(right)

        if op == "+":
            self.emit("FADD" if result_type == "real" else "ADD")
        elif op == "-":
            self.emit("FSUB" if result_type == "real" else "SUB")
        elif op == "*":
            self.emit("FMUL" if result_type == "real" else "MUL")
        elif op == "/":
            self.emit("FDIV" if result_type == "real" else "DIV")
        elif op == "**":
            raise CodeGenerationError("POWER operator code generation not implemented yet")

        elif op == ".LT.":
            self.emit("FINF" if self.is_real_comparison(left, right) else "INF")
        elif op == ".LE.":
            self.emit("FINFEQ" if self.is_real_comparison(left, right) else "INFEQ")
        elif op == ".GT.":
            self.emit("FSUP" if self.is_real_comparison(left, right) else "SUP")
        elif op == ".GE.":
            self.emit("FSUPEQ" if self.is_real_comparison(left, right) else "SUPEQ")
        elif op == ".EQ.":
            self.emit("EQUAL")
        elif op == ".NE.":
            self.emit("EQUAL")
            self.emit("NOT")
        elif op == ".AND.":
            self.emit("MUL")
        elif op == ".OR.":
            self.emit("ADD")
            self.emit("PUSHI 0")
            self.emit("SUP")
        else:
            raise CodeGenerationError(f"Unknown binary operator {op}")

    def gen_unop(self, node):
        _, op, expr = node

        expr_type = self.analyzer.get_type(node)

        if op == "+":
            self.gen_expr(expr)
            return

        if op == "-":
            if expr_type == "real":
                self.emit("PUSHF 0.0")
                self.gen_expr(expr)
                self.emit("FSUB")
            else:
                self.emit("PUSHI 0")
                self.gen_expr(expr)
                self.emit("SUB")
            return

        if op == ".NOT.":
            self.gen_expr(expr)
            self.emit("NOT")
            return

        raise CodeGenerationError(f"Unknown unary operator {op}")

    # =========================================================
    # Designators / memória
    # =========================================================

    def store_designator(self, node):
        kind = node[0]

        if kind == "id":
            symbol = self.current_scope.lookup(node[1])
            self.emit(f"STOREG {self.current_scope_base + symbol.index}")
            return

        raise CodeGenerationError(
            "store_designator should only be used for scalar variables; arrays need address first"
        )

    def gen_address(self, node):
        if node[0] != "call_or_index":
            raise CodeGenerationError(f"Cannot generate address for {node}")

        _, name, args = node

        symbol = self.current_scope.lookup(name)

        if symbol.kind != "array":
            raise CodeGenerationError(f"'{name}' is not an array")

        if len(args) != 1:
            raise CodeGenerationError(f"Array '{name}' expects one index")

        self.emit("PUSHGP")
        self.emit(f"PUSHI {self.current_scope_base + symbol.index}")

        self.gen_expr(args[0])
        self.emit("PUSHI 1")
        self.emit("SUB")

        self.emit("ADD")
        self.emit("PADD")

    # =========================================================
    # Tipos auxiliares
    # =========================================================

    def infer_expr_type(self, node):
        type_ = self.analyzer.get_type(node)

        if type_ is not None:
            return type_

        kind = node[0]

        if kind == "id" or kind == "call_or_index":
            return self.infer_designator_type(node)

        if kind == "int":
            return "integer"

        if kind == "real":
            return "real"

        if kind == "logical":
            return "logical"

        if kind == "string":
            return "string"

        raise CodeGenerationError(f"Cannot infer type for node {node}")

    def infer_designator_type(self, node):
        if node[0] == "id":
            symbol = self.current_scope.lookup(node[1])
            return symbol.type

        if node[0] == "call_or_index":
            name = node[1].upper()

            if name == "MOD":
                return "integer"

            symbol = self.current_scope.lookup(name)

            if symbol.kind == "array":
                return symbol.type

            if symbol.kind == "function":
                return symbol.return_type

        raise CodeGenerationError(f"Cannot infer designator type for {node}")

    def is_real_comparison(self, left, right):
        left_type = self.infer_expr_type(left)
        right_type = self.infer_expr_type(right)

        return left_type == "real" or right_type == "real"

    def clean_string(self, value):
        # Entrada vem como "'Ola ''Mundo'''"
        # Queremos: Ola 'Mundo'
        if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
            value = value[1:-1]

        value = value.replace("''", "'")
        value = value.replace("\\", "\\\\")
        value = value.replace('"', '\\"')

        return value
    
    def compute_scope_bases(self, units):
        base = 0

        for unit in units:
            if unit[0] == "main_program":
                name = unit[1][1].upper()

            elif unit[0] == "function_subprogram":
                name = unit[2][1].upper()

            elif unit[0] == "subroutine_subprogram":
                name = unit[1][1].upper()

            else:
                continue

            scope = self.analyzer.scopes[name]
            self.scope_bases[name] = base
            base += scope.next_index