"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


from os import path

from lark import Lark
from lark.exceptions import UnexpectedToken

from .evaluation import CommonEvaluator, ControlFlowEvaluator
from .exceptions import (
    ImproperlyConfigured,
    TagNotFound,
    TagupSyntaxError,
)
from .stack import TagStack


class TrimMixin:
    trim_chars = ' \t\n\r'

    def postprocess_block_node(self, node):
        return node.strip(self.trim_chars)


class StaticTagMixin:
    tags = None

    def __init__(self, *args, **kwargs):
        if TagDictMixin in self.__class__.__bases__:
            raise ImproperlyConfigured(
                'StaticTagMixin and TagDictMixin are mutually exclusive'
            )

        super().__init__(*args, **kwargs)
        if self.tags is None:
            raise ImproperlyConfigured(
                '{cls} must define {cls}.tags'.format(
                    cls=self.__class__.__name__
                )
            )

    def get_tag(self, name):
        result = self.tags[name]

        return result


class TagDictMixin:
    def __init__(self, tags=dict(), *args, **kwargs):
        if StaticTagMixin in self.__class__.__bases__:
            raise ImproperlyConfigured(
                'TagDictMixin and StaticTagMixin are mutually exclusive'
            )

        super().__init__(*args, **kwargs)
        self.tags = tags.copy()

    def get_tag(self, name):
        return self.tags[name]

    def __getitem__(self, key):
        return self.tags[key]

    def __setitem__(self, key, value):
        self.tags[key] = value

    def __delitem__(self, key):
        del self.tags[key]


class BaseRenderer:
    def __init__(self, max_depth=8):
        self.tag_stack = TagStack(max_depth)
        self.global_named_args = dict()

    def render_markup(self, markup, named_args=dict(), pos_args=list()):
        ast = self.parse_markup(markup)
        result = self.evaluate_ast(ast, named_args, pos_args)

        return result

    def get_tag(self, name):
        raise ImproperlyConfigured(
            '{cls} must define {cls}.get_tag()'.format(
                cls=self.__class__.__name__
            )
        )

    def render_tag(self, name, named_args, pos_args, line, column):
        try:
            tag_markup = self.get_tag(name)
        except ImproperlyConfigured as err:
            raise err
        except Exception:
            trace = self.tag_stack.stack_trace(name, line, column)
            raise TagNotFound(
                str(trace),
                tag_stack_trace=trace
            )

        self.tag_stack.push(name, line, column)
        try:
            result = self.render_markup(tag_markup, named_args, pos_args)
        finally:
            self.tag_stack.pop()

        return result

    def set_globals(self, global_named_args):
        self.global_named_args = global_named_args

    def parse_markup(self, markup):
        try:
            result = self.get_parser().parse(markup)
        except UnexpectedToken as err:
            trace = self.tag_stack.stack_trace(
                token if (token := str(err.token)) else 'END',
                err.line,
                err.column
            )
            raise TagupSyntaxError(
                str(trace),
                tag_stack_trace=trace
            )

        return result

    def evaluate_ast(self, ast, named_args, pos_args):
        combined_named_args = {**self.global_named_args, **named_args}

        cf_eval = ControlFlowEvaluator(
            named_args=combined_named_args,
            pos_args=pos_args,
            hook_manager=self,
        )
        intermediate = cf_eval.traverse(ast)

        if hasattr(self, 'prefetch_tags'):
            if tag_names := self.discover_tags(intermediate):
                self.prefetch_tags(tag_names)

        c_eval = CommonEvaluator(
            named_args=combined_named_args,
            pos_args=pos_args,
            hook_manager=self,
            renderer=self,
        )
        result = c_eval.traverse(intermediate)

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
