import ply.lex as lex
from datetime import date

reserved = {'VAR', 'IS', 'IF', 'THEN', 
    'ELSE', 'ENDIF', 
    'WHILE', 'DO', 'ENDWHILE',
    'PROCEDURE', 'FUNCTION', 
    'RETURN', 'PRINT', 'END'
}

tokens = ('ASSIGN', 
    'LPAREN', 'RPAREN',
    'LSQUARE', 'RSQUARE', 
    'LCURLY', 'RCURLY', 
    'APOSTROPHE', 'SEMICOLON', 
    'COMMA', 'DOT',
    'EQ', 'LT', 'PLUS', 'MINUS',
    'MULT', 'DIV' , 
    'STRING', 'DATE_LITERAL', 
    'INT_LITERAL', 'IDENT', 
    'FUNC_IDENT', 'PROC_IDENT'
) + tuple(reserved)

t_ASSIGN = r':='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSQUARE = r'\['
t_RSQUARE = r'\]'
t_LCURLY = r'\{'
t_RCURLY = r'\}'
t_APOSTROPHE = r'\''
t_SEMICOLON = r';'
t_COMMA = r','
t_DOT = r'\.'
t_EQ = r'='
t_LT = r'<'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'\/'

def t_STRING(t):
    r'"[^"]*"' # Any number of characters inside quotation marks.
    t.value = t.value[1:-1] # Crop the quotation marks
    return t
 
def t_DATE_LITERAL(t):
    r'\d{4}-\d{2}-\d{2}' # e.g. 2018-09-27
    try: 
        t.value = date.fromisoformat(str(t.value))
        return t
    except:
        raise Exception("Incorrect date at line {}: {}".format(t.lexer.lineno, t.value))
    
def t_INT_LITERAL(t):
    r'-?\d+' # optional minus followed by at least one number
    t.value = int(t.value)
    if (t.value >= 2**42):
       raise Exception("Line {}: Integer value must be less than 2**42".format(t.lexer.lineno))
    else:
        return t

def t_IDENT(t):
    r'[a-z][\w]+' # Starts with lowercase and must be followed by at least character in set [a-zA-Z0-9_]
    return t

def t_FUNC_IDENT(t):
    r'[A-Z][a-z0-9_]+' # Starts with uppercase
    return t

def t_PROC_IDENT(t):
    r'[A-Z]{2,}' # At least 2 characters all uppercase
    if t.value in reserved:
        t.type = t.value
    return t

def t_comment(t):
    r'\#%[^%]*[^#]*%\#'
    pass

def t_whitespace(t):
    r'\s+'
    t.lexer.lineno += t.value.count("\n")
    pass

def t_error(t):
    raise Exception("Illegal character '{}' at line {}".format(t.value[0], t.lexer.lineno))

lexer = lex.lex() # debug=1 for extra info

if __name__ == '__main__':
    import argparse, codecs
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--who', action='store_true', help='who wrote this' )
    group.add_argument('-f', '--file', help='filename to process')

    ns = parser.parse_args()
    if ns.who == True:
        # identify who wrote this
        print( 'Jaakko Hirvelä' )
    elif ns.file is None:
        # user didn't provide input filename
        parser.print_help()
    else:
        with codecs.open( ns.file, 'r', encoding='utf-8' ) as INFILE:
            data = INFILE.read() 
        lexer.input( data )
        while True:            
            try:
                token = lexer.token()
                if token is None:
                    break
                print( token )
            except Exception as e:
                print("\nError:", e)
                break