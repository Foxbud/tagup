"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


from os import path
from lark import Lark, Tree

from .evaluation import CommonEvaluator, ControlFlowEvaluator


class Renderer:
	def __init__(
		self,
		get_tag_callback,
		cache_tag_ast_callback=None,
		trim_args=False
	):
		grammar = self._get_grammar()
		self._parser = Lark(grammar, parser='lalr')
		self._get_tag = get_tag_callback
		self._cache_tag_ast = cache_tag_ast_callback
		self._trim_args = trim_args

	def render_markup(self, markup, named_args=dict(), pos_args=list()):
		ast = self._parse_markup(markup)
		result = self._evaluate_ast(ast, named_args, pos_args)

		return result

	def _render_tag(self, name, named_args, pos_args):
		tag = self._get_tag(name)
		if isinstance(tag, Tree):
			ast = tag
		else:
			ast = self._parse_markup(tag)
			if self._cache_tag_ast is not None:
				self._cache_tag_ast(name, ast)

		return self._evaluate_ast(ast, named_args, pos_args)

	def _parse_markup(self, markup):
		return self._parser.parse(markup)

	def _evaluate_ast(self, ast, named_args, pos_args):
		intermediate = ControlFlowEvaluator(
			named_args=named_args,
			pos_args=pos_args,
		).traverse(ast)
		result = CommonEvaluator(
			named_args=named_args,
			pos_args=pos_args,
			renderer=self,
			trim_args=self._trim_args
		).traverse(intermediate)

		return result

	def _get_grammar(self):
		root_dir = path.dirname(path.abspath(__file__))
		grammar_file = path.join(root_dir, 'grammar.lark')
		with open(grammar_file) as f_in:
			return f_in.read()
