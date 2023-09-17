#!/usr/bin/env python3
#

from semantics_common import visit_tree

WRITABLE_ATTRIBUTES = ["day", "month", "year"]
READABLE_ATTRIBUTES = ["day", "month", "year", "weekday", "weeknum"]
ALLOWED_TYPES = ["int", "date"]


# Define semantic check functions
def check_attributes(node, semdata):
    nodetype = node.nodetype
    if nodetype == 'write_attribute':
        if node.value not in WRITABLE_ATTRIBUTES:
            return "'{}' is not a writable attribute".format(node.value)
    if nodetype == 'read_attribute':
        if node.value not in READABLE_ATTRIBUTES:
            return "'{}' is not a readable attribute".format(node.value)
    else:
        return None


def check_return_and_param_types(node, semdata):
    nodetype = node.nodetype
    if nodetype == 'procedure_def' and node.type != 'void' and node.type not in ALLOWED_TYPES:
        return "Return type of a procedure must be either 'int' or 'date'"
    if nodetype == 'function_def' and node.type not in ALLOWED_TYPES:
        return "Return type of a function must be either 'int' or 'date'"
    if nodetype == 'formal_arg' and node.type not in ALLOWED_TYPES:
        return "Parameter type must be either 'int' or 'date'"
    else:
        return None


def count_while_and_if_level_before(node, semdata):
    nodetype = node.nodetype
    if nodetype == 'while loop':
        semdata.nested_whiles += 1
        return None

    if nodetype == 'if_statement':
        semdata.nested_ifs += 1
        return None

    if nodetype == 'return_statement':
        if semdata.nested_ifs > 0 or semdata.nested_whiles > 0:
            return "A return statement cannot appear inside a while or if statement"
        else:
            return None


def count_while_and_if_level_after(node, semdata):
    nodetype = node.nodetype
    if nodetype == 'while loop':
        semdata.nested_whiles -= 1
        return None

    if nodetype == 'if_statement':
        semdata.nested_ifs -= 1
        return None


def check_proc_defs(node, semdata):
    nodetype = node.nodetype
    if nodetype == 'procedure_def':
        for statement in node.children_statements:
            if statement.nodetype == 'return_statement' and node.type == 'void':
                return "The return statement can only appear inside a procedure definition that has a return type."
            else:
                return None


def semantic_checks(tree, semdata):
    '''run simple semantic checks'''
    semdata.nested_ifs = 0
    semdata.nested_whiles = 0
    visit_tree(tree, check_attributes, None, semdata)
    visit_tree(tree, check_return_and_param_types, None, semdata)
    visit_tree(tree, count_while_and_if_level_before,
               count_while_and_if_level_after, semdata)
    visit_tree(tree, check_proc_defs, None, semdata)


def run_simple_semantic_checks(tree, semdata):
    semantic_checks(tree, semdata)