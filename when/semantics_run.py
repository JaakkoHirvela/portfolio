#!/usr/bin/env python3
#

from datetime import datetime
from datetime import timedelta
from main import ASTnode

def run_program(tree, semdata):
  # Initialize all variables to zero
  for symdata in semdata.symtbl.values():
    if symdata.symtype == 'var':
      symdata.value = 0
  eval_node(tree, semdata) # Do the actual execution

def raise_error(message, lineno=0):
  print("Line " + str(lineno) + ": Error: " + message)
  raise SystemExit

def eval_arithmetics(node, semdata):
  operation = node.value
  l_value = eval_node(node.child_left_expr, semdata)
  r_value = eval_node(node.child_right_expr, semdata)
  if type(l_value) is str and type(r_value) is int:
    l_value = datetime.strptime(l_value, "%Y-%m-%d")
    if operation == '+': # date + days(int)
      result = l_value + timedelta(days=r_value)
    elif operation == '-': # date - days(int)
      result = l_value - timedelta(days=r_value)
    else:
      raise_error("operation '" + operation + "' is undefined for an operation between a date and an integer", node.lineno)

    result = result.strftime("%Y-%m-%d")
  elif type(l_value) is str and type(r_value) is str:
    l_value = datetime.strptime(l_value, "%Y-%m-%d")
    r_value = datetime.strptime(r_value, "%Y-%m-%d")
    if operation == '-': # Date - date = diff. in days (int)
      diff = l_value - r_value
      result = int(diff.days)
    else:
      raise_error("operation '" + operation + "' is undefined for an operation between two dates", node.lineno)
  elif type(l_value) is int and type(r_value) is int:
    if operation == '*':
      result = l_value * r_value
    elif operation == '+':
      result = l_value + r_value
    elif operation == '-':
      result = l_value - r_value
    elif operation == '/':
      result = l_value // r_value
  else: # TODO: check already in semantics_check
    raise_error("undefined arithmetic operation between type " + type(l_value) + " and " + type(r_value), node.lineno)

  return result

def read_var_attribute(read_attr, parent_value, node):
  parent_value = datetime.strptime(parent_value, "%Y-%m-%d")
  if read_attr == 'year':
    return parent_value.year
  elif read_attr == 'month':
    return parent_value.month
  elif read_attr == 'day':
    return parent_value.day
  elif read_attr == 'weekday':
    return parent_value.weekday()
  elif read_attr == 'weeknum':
    return parent_value.isocalendar()[1]
  else: # This branch should never be taken as these are checked already in simple_semantics_check.py
    raise_error("'" + read_attr + "' is not a readable attribute of a 'date' object", node.lineno)

def write_var_attribute(var, write_attr, new_value, semdata):
  date = datetime.strptime(eval_node(var ,semdata), "%Y-%m-%d")
  if write_attr == 'year':
    modified_date = datetime.strftime(date.replace(year=new_value), "%Y-%m-%d")
  elif write_attr == 'month':
    modified_date = datetime.strftime(date.replace(month=new_value), "%Y-%m-%d")
  elif write_attr == 'day':
    modified_date = datetime.strftime(date.replace(day=new_value), "%Y-%m-%d")
  else: # This should be checked in sematic checks
    raise_error("'" + write_attr.value + "' is not a writable attribute of a 'date' object", var.lineno)
  var.symdata.value = modified_date


def eval_node(node, semdata):
  symtbl = semdata.symtbl
  nodetype = node.nodetype
  if nodetype == 'program':
    # Execute each definition in program
    for i in node.children_definitions:
      eval_node(i, semdata)
    for i in node.children_statements:
      eval_node(i, semdata)
    return None
  elif nodetype == 'variable_def':
    # Execute the expression
    expr_value = eval_node(node.child_expression, semdata)
    # Change the value of the variable in symbol data
    node.symdata.value = expr_value
    return None
  elif nodetype == 'date_literal':
    return str(node.value)
  elif nodetype == 'string_literal':
    return node.value
  elif nodetype == 'var':
    # Return the value of the variable in symtbl as result
    parent_value = node.symdata.value
    if hasattr(node, "child_read_attr"):
      read_attr = node.child_read_attr.value
      return read_var_attribute(read_attr, parent_value, node)
    else:
      return parent_value
  elif nodetype == 'int_literal':
    return node.value
  elif nodetype == 'operation':
    return eval_arithmetics(node, semdata)
  elif nodetype == 'assign':
    r_value = eval_node(node.child_rvalue, semdata)
    if hasattr(node.child_lvalue, "child_write_attr"): # Change a single attribute
      write_attr = node.child_lvalue.child_write_attr.value # year, month or day
      write_var_attribute(node.child_lvalue, write_attr, r_value, semdata)
    else:
      l_value = symtbl[node.child_lvalue.value]
      l_value.value = r_value
    return None
  elif nodetype == 'print_statement':
    for item in node.children_print_items:
      print(eval_node(item, semdata), end=" ")
    print()
  elif nodetype == 'if_statement':
    condition = eval_node(node.child_condition, semdata)
    if condition:
      eval_node(node.children_if_branch[0], semdata) # TODO: Why a list?
    else:
      eval_node(node.children_else_branch[0], semdata)
  elif nodetype == 'while_loop':
    while eval_node(node.child_condition, semdata):
      for child in node.children_body:
        eval_node(child, semdata)
    return None
  elif nodetype == 'comparison':
    left_expr = eval_node(node.child_left_expr, semdata)
    right_expr = eval_node(node.child_right_expr, semdata)
    comparison_type = node.value
    if comparison_type == '=':
      return 1 if left_expr == right_expr else 0
    elif comparison_type == '<':
      return 1 if left_expr < right_expr else 0
    else:
      raise_error("undefined comparison type '" + comparison_type + "'", node.lineno)
  elif nodetype == 'func_call':
    func_name = node.value
    if func_name == 'Today':
      node = ASTnode('date_literal')
      today = datetime.today()
      node.value = today.strftime("%Y-%m-%d")
      return eval_node(node, semdata)
    else:
      raise_error("TODO: Functions", node.lineno) # TODO
  else:
    print("Error, unknown node of type " + nodetype)
    return None

