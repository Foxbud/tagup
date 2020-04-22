"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


from os import path
from lark import Lark, Tree

from .evaluation import CommonEvaluator, ControlFlowEvaluator


class BaseRenderer:
	def render_markup(self, markup, named_args=dict(), pos_args=list()):
		ast = self.parse_markup(markup)
		result = self.evaluate_ast(ast, named_args, pos_args)

		return result

	def get_tag(self, name):
		raise NotImplementedError

	def render_tag(self, name, named_args, pos_args):
		tag_markup = self.get_tag(name)

		return self.render_markup(tag_markup, named_args, pos_args)

	def parse_markup(self, markup):
		return self.get_parser().parse(markup)

	def evaluate_ast(self, ast, named_args, pos_args):
		intermediate = ControlFlowEvaluator(
			named_args=named_args,
			pos_args=pos_args,
			hook_manager=self,
		).traverse(ast)
		result = CommonEvaluator(
			named_args=named_args,
			pos_args=pos_args,
			hook_manager=self,
			renderer=self,
		).traverse(intermediate)

		return result

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
