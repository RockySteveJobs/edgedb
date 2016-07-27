##
# Copyright (c) 2015 MagicStack Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import collections

from edgedb.lang.common import ast

from . import ast as qlast
from . import codegen
from . import compiler
from . import decompiler
from . import parser


def inline_constants(edgeql_tree, values, types):
    flt = lambda n: isinstance(n, qlast.ConstantNode) and n.index in values
    constants = ast.find_children(edgeql_tree, flt)

    for constant in constants:
        value = values[constant.index]

        if (isinstance(value, collections.Container)
                and not isinstance(value, (str, bytes))):
            elements = [qlast.ConstantNode(value=i) for i in value]
            value = qlast.SequenceNode(elements=elements)

        constant.value = value


def normalize_tree(expr, schema, *, module_aliases=None, anchors=None,
                   inline_anchors=False):
    ir = compiler.compile_ast_to_ir(
        expr, schema, module_aliases=module_aliases, anchors=anchors)
    edgeql_tree = decompiler.decompile_ir(ir, inline_anchors=inline_anchors)

    source = codegen.generate_source(edgeql_tree, pretty=False)

    return ir, edgeql_tree, source


def normalize_expr(expr, schema, *, module_aliases=None, anchors=None,
                   inline_anchors=False):
    tree = parser.parse(expr, module_aliases)
    _, _, expr = normalize_tree(
        tree, schema, module_aliases=module_aliases, anchors=anchors,
        inline_anchors=inline_anchors)

    return expr