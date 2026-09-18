import re
import ply.lex as lex



tokens = (
    'PROGRAM', 'INTEGER', 'REAL', 'LOGICAL',
    'IF', 'THEN', 'ELSE', 'DO', 'GOTO',
    'ENDIF', 'END', 'CONTINUE', 'STOP',
    'READ', 'PRINT',
    'FUNCTION', 'SUBROUTINE', 'RETURN', 'CALL',
    'TRUE', 'FALSE',
    'AND', 'OR', 'NOT',
    'LT', 'LE', 'EQ', 'NE', 'GT', 'GE',
    'ID', 'LABEL',
    'INT_CONST', 'REAL_CONST', 'STRING_CONST',
    'TIMES', 'POWER',
)


literals = ('(', ')', ',', '=', ':', '+', '-', '/')



states = (
    ('PREFIX', 'exclusive'),
    ('CODE', 'exclusive'),
)



def _col(lexer, lexpos):
    return lexpos - lexer.line_start + 1



def _err(lexer, lexpos, ch, msg, state):
    col = _col(lexer, lexpos)
    print(f"Line {lexer.lineno}, column {col}: {msg}. Found: {repr(ch)}. State: {state}")



# -------------------------------------------------
# INITIAL
# -------------------------------------------------


def t_INITIAL_newline(t):
    r'\n'
    t.lexer.lineno += 1



def t_INITIAL_startline(t):
    r'.'
    t.lexer.line_start = t.lexpos
    t.lexer.begin('PREFIX')
    t.lexer.lexpos -= 1



def t_INITIAL_error(t):
    _err(
        t.lexer,
        t.lexpos,
        t.value[0],
        "invalid character at the start of a line",
        "INITIAL"
    )
    t.lexer.skip(1)



# -------------------------------------------------
# PREFIX
# -------------------------------------------------


def t_PREFIX_comment(t):
    r'[Cc\*][^\n]*'
    col = _col(t.lexer, t.lexpos)
    if col == 1:
        t.lexer.begin('INITIAL')
    else:
        _err(
            t.lexer,
            t.lexpos,
            t.value[0],
            "invalid comment marker; in Fortran 77 fixed-form, 'C', 'c', or '*' may only start a comment in column 1",
            "PREFIX"
        )
        t.lexer.skip(1)



def t_PREFIX_LABEL(t):
    r'[ ]{0,4}[0-9]{1,5}'
    col = _col(t.lexer, t.lexpos)
    if col == 1:
        t.value = int(t.value.strip())
        return t



def t_PREFIX_spaces(t):
    r'[ ]+'
    col1 = _col(t.lexer, t.lexpos)
    col2 = col1 + len(t.value) - 1


    if col2 <= 5:
        pass
    elif col1 <= 6 <= col2:
        t.lexer.begin('CODE')
    else:
        t.lexer.begin('CODE')
        t.lexer.lexpos -= len(t.value)



def t_PREFIX_continuation(t):
    r'[^ \n]'
    col = _col(t.lexer, t.lexpos)


    if col == 6:
        t.lexer.begin('CODE')
    elif 1 <= col <= 5:
        _err(
            t.lexer,
            t.lexpos,
            t.value[0],
            "invalid character in columns 1-5; this field may only contain blanks, a numeric label, or a comment marker in column 1",
            "PREFIX"
        )
        t.lexer.skip(1)
    else:
        t.lexer.begin('CODE')
        t.lexer.lexpos -= 1



def t_PREFIX_newline(t):
    r'\n'
    t.lexer.lineno += 1
    t.lexer.begin('INITIAL')



def t_PREFIX_error(t):
    _err(
        t.lexer,
        t.lexpos,
        t.value[0],
        "invalid character in line prefix",
        "PREFIX"
    )
    t.lexer.skip(1)



# -------------------------------------------------
# CODE
# -------------------------------------------------


t_CODE_POWER = r'\*\*'
t_CODE_TIMES = r'\*'


t_CODE_LT = r'\.LT\.'
t_CODE_LE = r'\.LE\.'
t_CODE_EQ = r'\.EQ\.'
t_CODE_NE = r'\.NE\.'
t_CODE_GT = r'\.GT\.'
t_CODE_GE = r'\.GE\.'


t_CODE_AND = r'\.AND\.'
t_CODE_OR  = r'\.OR\.'
t_CODE_NOT = r'\.NOT\.'



def t_CODE_PROGRAM(t):
    r'PROGRAM'
    return t



def t_CODE_INTEGER(t):
    r'INTEGER'
    return t



def t_CODE_REAL(t):
    r'REAL'
    return t



def t_CODE_LOGICAL(t):
    r'LOGICAL'
    return t



def t_CODE_IF(t):
    r'IF'
    return t



def t_CODE_THEN(t):
    r'THEN'
    return t



def t_CODE_ELSE(t):
    r'ELSE'
    return t



def t_CODE_DO(t):
    r'DO'
    return t



def t_CODE_GOTO(t):
    r'GOTO'
    return t



def t_CODE_ENDIF(t):
    r'ENDIF'
    return t



def t_CODE_END(t):
    r'END'
    return t



def t_CODE_CONTINUE(t):
    r'CONTINUE'
    return t



def t_CODE_STOP(t):
    r'STOP'
    return t



def t_CODE_READ(t):
    r'READ'
    return t



def t_CODE_PRINT(t):
    r'PRINT'
    return t



def t_CODE_FUNCTION(t):
    r'FUNCTION'
    return t



def t_CODE_SUBROUTINE(t):
    r'SUBROUTINE'
    return t



def t_CODE_RETURN(t):
    r'RETURN'
    return t



def t_CODE_CALL(t):
    r'CALL'
    return t



def t_CODE_TRUE(t):
    r'\.TRUE\.'
    return t



def t_CODE_FALSE(t):
    r'\.FALSE\.'
    return t



def t_CODE_REAL_CONST(t):
    r'(\d+\.\d*|\d*\.\d+)([Ee][+-]?\d+)?'
    t.value = float(t.value)
    return t



def t_CODE_INT_CONST(t):
    r'\d+'
    t.value = int(t.value)
    return t



def t_CODE_STRING_CONST(t):
    r"'([^']|'')*'"
    return t



def t_CODE_ID(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    return t



t_CODE_ignore = ' \t'



def t_CODE_newline(t):
    r'\n'
    t.lexer.lineno += 1
    t.lexer.begin('INITIAL')



def t_CODE_error(t):
    _err(
        t.lexer,
        t.lexpos,
        t.value[0],
        "illegal character in code area; it does not match any supported token, literal, or operator",
        "CODE"
    )
    t.lexer.skip(1)



def build_lexer():
    lexer = lex.lex(reflags=re.IGNORECASE)
    lexer.begin('INITIAL')
    lexer.line_start = 0
    lexer.lineno = 1
    return lexer