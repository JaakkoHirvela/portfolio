import ply.yacc as yacc
import ply.lex as lex
import lexer
import tree_print


tokens = lexer.tokens


class ASTnode:
    def __init__(self, typestr):
        self.nodetype = typestr


def p_program(p):
    '''program : opt_definitions statement_list
               | statement_list'''
    p[0] = ASTnode("program")
    if len(p) == 3:
        p[0].children_definitions = p[1]
        p[0].children_statements = p[2]
    else:
        p[0].children_statements = p[1]
        p[0].children_definitions = []
    p[0].lineno = p.lineno(1)


def p_empty(p):
    '''empty : '''
    pass


def p_statement_list(p):
    '''statement_list : statement SEMICOLON
                      | statement_list statement SEMICOLON'''
    if len(p) == 3:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])


def p_definitions(p):
    '''definitions : function_definition
                   | procedure_definition
                   | variable_definition'''
    p[0] = p[1]


def p_opt_definitions(p):
    '''opt_definitions : empty
                       | definitions
                       | opt_definitions definitions'''
    if len(p) == 2:
        if p[1] == None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])


def p_variable_definition(p):
    '''variable_definition : VAR IDENT IS expression'''
    p[0] = ASTnode("variable_def")
    p[0].value = p[2]
    p[0].child_expression = p[4]
    p[0].lineno = p.lineno(1)


def p_opt_variable_defs(p):
    '''opt_variable_defs : empty
                         | variable_definition_list'''
    if p[1] == None:
        p[0] = []
    else:
        p[0] = p[1]


def p_variable_definition_list(p):
    '''variable_definition_list : variable_definition
                                | variable_definition_list variable_definition'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])


def p_function_definition(p):
    '''function_definition : FUNCTION FUNC_IDENT LCURLY opt_formals RCURLY RETURN IDENT opt_variable_defs IS rvalue END FUNCTION'''
    p[0] = ASTnode("function_def")
    p[0].value = p[2]
    p[0].children_formals = p[4]
    p[0].children_variable_defs = p[8]
    p[0].type = p[7]
    p[0].child_body = p[10]
    p[0].lineno = p.lineno(1)


def p_procedure_definition(p):
    '''procedure_definition : PROCEDURE PROC_IDENT LCURLY opt_formals RCURLY RETURN IDENT opt_variable_defs IS statement_list END PROCEDURE
                            | PROCEDURE PROC_IDENT LCURLY opt_formals RCURLY opt_variable_defs IS statement_list END PROCEDURE'''
    p[0] = ASTnode("procedure_def")
    p[0].value = p[2]
    p[0].children_formals = p[4]
    if len(p) == 11:
        p[0].type = "void"  # i.e. no return type
        p[0].children_var_defs = p[6]
        p[0].children_statements = p[8]
    else:
        p[0].type = p[7]
        p[0].children_var_defs = p[8]
        p[0].children_statements = p[10]
    p[0].lineno = p.lineno(1)


def p_formals(p):
    '''formals : formal_arg
               | formals COMMA formal_arg'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])


def p_opt_formals1(p):
    '''opt_formals : formals'''
    p[0] = p[1]


def p_opt_formals2(p):
    '''opt_formals : empty'''
    p[0] = []


def p_formal_arg(p):
    '''formal_arg : IDENT LSQUARE IDENT RSQUARE'''
    p[0] = ASTnode("formal_arg")
    p[0].value = p[1]
    p[0].type = p[3]
    p[0].lineno = p.lineno(1)


def p_procedure_call(p):
    '''procedure_call : PROC_IDENT LPAREN arguments RPAREN
                      | PROC_IDENT LPAREN RPAREN'''
    p[0] = ASTnode("proc_call")
    p[0].lineno = p.lineno(1)
    p[0].value = p[1]
    if len(p) == 5:
        p[0].children_args = p[3]
    else:
        p[0].children_args = []


def p_arguments(p):
    '''arguments : expression
                 | arguments COMMA expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])


def p_assignment(p):
    '''assignment : lvalue ASSIGN rvalue'''
    p[0] = ASTnode("assign")
    p[0].child_lvalue = p[1]
    p[0].child_rvalue = p[3]


def p_lvalue(p):
    '''lvalue : IDENT
              | IDENT DOT IDENT'''
    p[0] = ASTnode("var")
    p[0].value = p[1]
    p[0].lineno = p.lineno(1)
    if len(p) == 4:
        p[0].child_write_attr = ASTnode("write_attribute")
        p[0].child_write_attr.lineno = p[0].lineno
        p[0].child_write_attr.value = p[3]


def p_rvalue(p):
    '''rvalue : expression
              | if_expression'''
    p[0] = p[1]


def p_print_statement(p):
    '''print_statement : PRINT print_list'''
    p[0] = ASTnode("print_statement")
    p[0].lineno = p.lineno(1)
    p[0].children_print_items = p[2]


def p_print_item1(p):
    '''print_item : expression'''
    p[0] = p[1]


def p_print_item2(p):
    '''print_item : STRING'''
    p[0] = ASTnode("string_literal")
    p[0].value = p[1]


def p_print_list(p):
    '''print_list : print_item
                  | print_list COMMA print_item'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])


def p_statement1(p):
    '''statement : procedure_call
                 | assignment
                 | print_statement
                 | RETURN expression'''
    if len(p) == 2:  # pass
        p[0] = p[1]
    if len(p) == 3:  # Return statement
        p[0] = ASTnode("return_statement")
        p[0].lineno = p.lineno(1)
        p[0].child_expr = p[2]


def p_statement2(p):
    '''statement : WHILE expression DO statement_list ENDWHILE'''
    p[0] = ASTnode("while_loop")
    p[0].child_condition = p[2]
    p[0].children_body = p[4]


def p_statement3(p):
    '''statement : IF expression THEN statement_list ELSE statement_list ENDIF
                 | IF expression THEN statement_list ENDIF'''
    p[0] = ASTnode("if_statement")
    p[0].child_condition = p[2]
    p[0].children_if_branch = p[4]
    if len(p) == 8:
        p[0].children_else_branch = p[6]
    else:
        p[0].children_else_branch = []


def p_expression(p):
    '''expression : simple_expr
                  | expression EQ simple_expr
                  | expression LT simple_expr'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ASTnode("comparison")
        p[0].child_left_expr = p[1]
        p[0].value = p[2]
        p[0].child_right_expr = p[3]


def p_simple_expr1(p):
    '''simple_expr : term'''
    p[0] = p[1]


def p_simple_expr2(p):
    '''simple_expr : simple_expr PLUS term
                   | simple_expr MINUS term'''
    p[0] = ASTnode("operation")
    p[0].lineno = p[1].lineno if hasattr(p[1], "lineno") else 0
    p[0].child_left_expr = p[1]
    p[0].value = p[2]
    p[0].child_right_expr = p[3]


def p_term1(p):
    '''term : factor'''
    p[0] = p[1]


def p_term2(p):
    '''term : term MULT factor
            | term DIV factor'''
    p[0] = ASTnode("operation")
    p[0].lineno = p[1].lineno
    p[0].child_left_expr = p[1]
    p[0].value = p[2]
    p[0].child_right_expr = p[3]


def p_factor(p):
    '''factor : atom
              | MINUS atom
              | PLUS atom'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]
        p[0].value = p[1]


def p_atom1(p):
    '''atom : LPAREN expression RPAREN
            | function_call
            | procedure_call'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]


def p_atom2(p):
    '''atom : IDENT
            | IDENT APOSTROPHE IDENT'''
    p[0] = ASTnode("var")
    p[0].value = p[1]
    p[0].lineno = p.lineno(1)
    if len(p) > 2:
        p[0].child_read_attr = ASTnode("read_attribute")
        p[0].child_read_attr.lineno = p[0].lineno
        p[0].child_read_attr.value = p[3]


def p_atom3(p):
    '''atom : INT_LITERAL'''
    p[0] = ASTnode("int_literal")
    p[0].value = p[1]
    p[0].lineno = p.lineno(1)


def p_atom4(p):
    '''atom : DATE_LITERAL'''
    p[0] = ASTnode("date_literal")
    p[0].value = p[1]
    p[0].lineno = p.lineno(1)


def p_function_call(p):
    '''function_call : FUNC_IDENT LPAREN arguments RPAREN
                     | FUNC_IDENT LPAREN RPAREN'''
    p[0] = ASTnode("func_call")
    p[0].value = p[1]
    p[0].lineno = p.lineno(1)
    if len(p) == 5:
        p[0].children_args = p[3]
    else:
        p[0].children_args = []


def p_if_expression(p):
    '''if_expression : IF expression THEN expression ELSE expression ENDIF'''
    p[0] = ASTnode("if_expression")
    p[0].child_condition = p[2]
    p[0].child_if_body = p[4]
    p[0].child_else_body = p[6]
    p[0].lineno = p.lineno(1)


def p_error(p):
    if (p is None):
        print("Unexpected end of input")
    else:
        print("{}:Syntax Error (token: '{}')".format(p.lineno, p.value))

    raise SystemExit


parser = yacc.yacc()

if __name__ == '__main__':
    import argparse
    import codecs
    argParser = argparse.ArgumentParser()
    argParser.add_argument(
        '-t', '--treetype', help='type of output tree (unicode/ascii/dot)')

    argParser.add_argument('-d', '--debug', action='store_true', help='debug?')

    group = argParser.add_mutually_exclusive_group()
    group.add_argument('--who', action='store_true', help='who wrote this')
    group.add_argument('-f', '--file', help='filename to process')
    ns = argParser.parse_args()

    Debug = True if ns.debug else False

    outFormat = "unicode"
    if ns.treetype:
        outFormat = ns.treetype
    if ns.who == True:
        # identify who wrote this
        print('Jaakko Hirvelä')
    elif ns.file is None:
        # user didn't provide input filename
        argParser.print_help()
    else:
        data = codecs.open(ns.file, encoding='utf-8').read()
        syntax_tree = parser.parse(data, lexer=lexer.lexer, debug=Debug)
        tree_print.treeprint(syntax_tree, outFormat)
        if syntax_tree is None:
            print('syntax OK')

        from symtbl_semantics_check import semantic_checks
        from symtbl_semantics_check import print_symbol_table
        from semantics_run import run_program
        from semantics_common import SemData

        semdata = SemData()
        semantic_checks(syntax_tree, semdata)
        run_program(syntax_tree, semdata)
        # print_symbol_table(semdata, 'Symbol table after:')
