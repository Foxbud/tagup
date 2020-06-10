"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


from copy import deepcopy

from lark import Token, Tree

from .traversal import (
    DiscardNode,
    PostOrderTraverser,
    PreOrderTraverser
)


class ContextMixin:
    def __init__(self, named_args, pos_args, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.named_args = named_args
        self.pos_args = pos_args


class CommonEvaluator(ContextMixin, PostOrderTraverser):
    escape_sequences = {
        'o': '[',
        'c': ']',
        's': '\\',
    }

    def __init__(self, renderer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renderer = renderer

    def escape_sequence(self, node):
        sequence = node.children[0]

        return self.escape_sequences[sequence]

    def named_substitution(self, node):
        name = node.children[0].strip()
        value = self.named_args[name]

        return value

    def positional_substitution(self, node):
        position = node.children[0].strip()
        arg_num = int(position) - 1
        value = self.pos_args[arg_num]

        return value

    def block(self, node):
        children = node.children

        return ''.join(children)

    def named_argument(self, node):
        name = node.children[0].strip()
        value = node.children[1]

        return (name, value)

    def positional_argument(self, node):
        value = node.children[0]

        return (value,)

    def tag(self, node):
        children = node.children
        name = children[0]
        named_args = dict()
        pos_args = list()
        for arg in children[1:]:
            if len(arg) == 2:
                named_args[arg[0]] = arg[1]
            else:
                pos_args.append(arg[0])

        result = self.renderer.render_tag(
            name=name,
            named_args=named_args,
            pos_args=pos_args,
            line=name.line,
            column=name.column
        )

        return result


class ControlFlowEvaluator(ContextMixin, PreOrderTraverser):
    def named_test(self, node):
        children = node.children
        name = children[0]
        else_clause = len(children) == 3
        if name in self.named_args:
            result = children[1].children[0]
        elif else_clause:
            result = children[2].children[0]
        else:
            raise DiscardNode()

        return result

    def positional_test(self, node):
        children = node.children
        arg_num = int(children[0]) - 1
        else_clause = len(children) == 3
        if len(self.pos_args) > arg_num:
            result = children[1].children[0]
        elif else_clause:
            result = children[2].children[0]
        else:
            raise DiscardNode()

        return result

    def positional_loop(self, node):
        children = node.children
        else_clause = len(children) == 2
        if len(self.pos_args) > 0:
            statement = children[0].children[0]
            result = Tree(data='block', children=list())
            for arg in self.pos_args:
                new_statement = deepcopy(statement)
                sub_args = new_statement.find_data('loop_item')
                for sub_arg in sub_args:
                    sub_arg.data = 'block'
                    sub_arg.children = [
                        Token('STRING', arg),
                    ]
                result.children.append(new_statement)
        elif else_clause:
            result = children[1].children[0]
        else:
            raise DiscardNode()

        return result
