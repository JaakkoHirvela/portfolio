#!/usr/bin/env python3
#

from simple_semantics_check import run_simple_semantic_checks
from semantics_common import visit_tree, SymbolData, SemData

# Define semantic check functions


# Collect variables to the symbol table
def add_vars(node, semdata):
  nodetype = node.nodetype
  if nodetype == 'variable_def':
    var_name = node.value
    if var_name in semdata.symtbl:
      definition_node = semdata.symtbl[var_name].defnode
      # Variable is already in the symbol table
      return "Error, redefined variable '" + var_name + "' (earlier definition on line "+str(definition_node.lineno)+")"
    else:
      # Add variable to symbol table
      symdata = SymbolData('var', node)
      semdata.symtbl[var_name] = symdata
      node.symdata = symdata  # Add a link to the symbol data to AST node for execution

  elif nodetype == 'formal_arg':
    arg_name = node.value
    if arg_name in semdata.symtbl:
      definition_node = semdata.symtbl[arg_name].defnode
      return "Error, multiple arguments with the same name '" + arg_name + "'"
    else:
      symdata = SymbolData('arg', node)
      semdata.symtbl[arg_name] = symdata
      node.symdata = symdata

  elif nodetype == 'var':
    var_name = node.value
    if var_name not in semdata.symtbl:
      return "Error, undefined variable '" + var_name + "'"
    else:
      # Add symbol data link to variable's AST node (for execution)
      node.symdata = semdata.symtbl[var_name]

def add_functions_and_procedures(node, semdata):
  nodetype = node.nodetype
  if nodetype == 'function_def' or nodetype == 'procedure_def':
    name = node.value
    if name in semdata.symtbl:
      definition_node = semdata.symtbl[name].defnode
      return "Error, redefined '" + name + "' (earlier definition on line " + str(definition_node.lineno)+")"
    else:
      symtype = 'func' if nodetype == 'function_def' else 'proc'
      symdata = SymbolData(symtype, node)
      semdata.symtbl[name] = symdata
      node.symdata = symdata
  
  elif nodetype == 'func_call' or nodetype == 'proc_call':
    name = node.value
    if name not in semdata.symtbl:       
      if name == 'Today': # Today() is a built-in function
        return None
      else:
        return "Error, call to undefined function/procedure '" + name + "'"
    else:
      definition_node = semdata.symtbl[name].defnode
      if len(definition_node.children_formals) != len(node.children_args):
        return "Error, function '" + name + "' needs " + str(len(definition_node.children_formals)) + " parameter(s) but is called with " + str(len(node.children_args))
      else:
        # Link to definition for execution
        node.symdata = semdata.symtbl[name]

def check_procs_before(node, semdata):
  nodetype = node.nodetype
  if nodetype == 'print_statement' or nodetype == 'return_statement' or nodetype == 'expr': # TODO: Check these better
    semdata.inside_expr += 1
    return None
  elif nodetype == 'proc_call':
    name = node.value
    definition_node = semdata.symtbl[name].defnode
    if semdata.inside_expr:
      if definition_node.type == 'void':
        return "Error, a procedure without return type can only be called as a statement"
    elif definition_node.type != 'void':
      return "Error, a procedure with return type can only be called inside an expression"


def check_procs_after(node, semdata):
  nodetype = node.nodetype
  if nodetype == 'print_statement' or nodetype == 'return_statement' or nodetype == 'expr': # TODO: Check these better
    semdata.inside_expr -= 1
    return None

# Simple symbol table printer for debugging
def print_symbol_table(semdata, title):
  '''Print the symbol table in semantic data

     Parameters:
     semdata: A SemData data structure containing semantic data
     title: String printed at the beginning
'''
  print(title)
  for name, data in semdata.symtbl.items():
    print(name, ":")
    for attr, value in vars(data).items():
      printvalue = value
      if hasattr(value, "nodetype"):  # If the value seems to be a ASTnode
        printvalue = value.nodetype
        if hasattr(value, "lineno"):
          printvalue = printvalue + ", line " + str(value.lineno)
      print("  ", attr, "=", printvalue)


def semantic_checks(tree, semdata):
  '''run all semantic checks'''
  # First run simple semantic checks implemented previously
  run_simple_semantic_checks(tree, semdata)
  # Gather variables and check their usage:
  visit_tree(tree, add_vars, None, semdata)
  # Gather and check function definitions:
  visit_tree(tree, add_functions_and_procedures, None, semdata)
  semdata.inside_expr = 0
  visit_tree(tree, check_procs_before, check_procs_after, semdata)

  # print_symbol_table(semdata, "Symbol table before:")  # Just for debugging


