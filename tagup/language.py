"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


from os import path
from lark import Lark, Tree

from .evaluation import CommonEvaluator, ControlFlowEvaluator
from .stack import TagStack


class BaseRenderer:
    def __init__(self, max_depth=8):
        self.tag_stack = TagStack(max_depth)
        self.global_named_args = dict()

    def render_markup(self, markup, named_args=dict(), pos_args=list()):
        ast = self.parse_markup(markup)
        result = self.evaluate_ast(ast, named_args, pos_args)

        return result

    def get_tag(self, name):
        raise NotImplementedError

    def render_tag(self, name, named_args, pos_args, line, column):
        self.tag_stack.push(name, line, column)

        try:
            tag_markup = self.get_tag(name)
            result = self.render_markup(tag_markup, named_args, pos_args)
        finally:
            self.tag_stack.pop()

        return result

    def set_globals(self, global_named_args):
        self.global_named_args = global_named_args

    def parse_markup(self, markup):
        return self.get_parser().parse(markup)

    def evaluate_ast(self, ast, named_args, pos_args):
        combined_named_args = {**self.global_named_args, **named_args}

        intermediate = ControlFlowEvaluator(
            named_args=combined_named_args,
            pos_args=pos_args,
            hook_manager=self,
        ).traverse(ast)

        if hasattr(self, 'prefetch_tags'):
            if tag_names := self.discover_tags(intermediate):
                self.prefetch_tags(tag_names)

        result = CommonEvaluator(
            named_args=combined_named_args,
            pos_args=pos_args,
            hook_manager=self,
            renderer=self,
        ).traverse(intermediate)

        return result

    def discover_tags(self, ast):
        tag_nodes = ast.find_data('tag')

        return {
            node.children[0]
            for node
            in tag_nodes
        }

    def get_grammar(self):
        try:
            grammar = self.grammar
        except AttributeError:
            grammar_filepath = path.join(
                path.dirname(path.abspath(__file__)),
                'grammar.lark'
            )
            with open(grammar_filepath) as f_in:
                grammar = self.grammar = f_in.read()

        return grammar

    def get_parser(self):
        try:
            parser = self.parser
        except AttributeError:
            parser = self.parser = Lark(self.get_grammar(), parser='lalr')

        return parser
