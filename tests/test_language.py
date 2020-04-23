"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


from unittest import TestCase
from unittest.mock import MagicMock

from tagup import BaseRenderer


class RenderingTestCase(TestCase):
	class TestRenderer(BaseRenderer):
		tags = {
			'const': 'constant value',
			'positional-sub': '<sub>[\\\\1]</sub>',
			'named-sub': '<sub>[\\\\arg]</sub>',
		}

		def get_tag(self, name):
			return self.tags[name]

	def setUp(self):
		self.renderer = self.TestRenderer()

	def test_plain_text(self):
		with self.subTest('inline'):
			self.assertEqual(
				self.renderer.render_markup(
					'plain text'
				),
				'plain text'
			)
		with self.subTest('multiline'):
			self.assertEqual(
				self.renderer.render_markup(
					'\nplain\n\ntext\n'
				),
				'\nplain\n\ntext\n'
			)

	def test_escape_sequence(self):
		with self.subTest('open'):
			self.assertEqual(
				self.renderer.render_markup(
					'[\\o]'
				),
				'['
			)
		with self.subTest('close'):
			self.assertEqual(
				self.renderer.render_markup(
					'[\\c]'
				),
				']'
			)
		with self.subTest('slash'):
			self.assertEqual(
				self.renderer.render_markup(
					'[\\s]'
				),
				'\\'
			)

	def test_constant_tag(self):
		with self.subTest('standalone'):
			self.assertEqual(
				self.renderer.render_markup(
					'[const]'
				),
				'constant value'
			)
		with self.subTest('embedded'):
			self.assertEqual(
				self.renderer.render_markup(
					'<outer>\n[const]</outer>'
				),
				'<outer>\nconstant value</outer>'
			)

	def test_positional_substitution(self):
		with self.subTest('separator'):
			self.assertEqual(
				self.renderer.render_markup(
					'[positional-sub\\argument value]'
				),
				'<sub>argument value</sub>'
			)
		with self.subTest('no separator'):
			self.assertEqual(
				self.renderer.render_markup(
					'[positional-sub argument value]'
				),
				'<sub>argument value</sub>'
			)
		with self.subTest('multiline separator'):
			self.assertEqual(
				self.renderer.render_markup(
					'[positional-sub\n\\\nargument value\n]'
				),
				'<sub>\nargument value\n</sub>'
			)
		with self.subTest('multiline no separator'):
			self.assertEqual(
				self.renderer.render_markup(
					'[positional-sub\nargument value\n]'
				),
				'<sub>argument value\n</sub>'
			)

	def test_named_substitution(self):
		with self.subTest('separator'):
			self.assertEqual(
				self.renderer.render_markup(
					'[named-sub\\arg\\\\argument value]'
				),
				'<sub>argument value</sub>'
			)
		with self.subTest('no separator'):
			self.assertEqual(
				self.renderer.render_markup(
					'[named-sub arg\\\\argument value]'
				),
				'<sub>argument value</sub>'
			)
		with self.subTest('multiline separator'):
			self.assertEqual(
				self.renderer.render_markup(
					'[named-sub\n\\\narg\n\\\\\nargument value\n]'
				),
				'<sub>\nargument value\n</sub>'
			)
		with self.subTest('multiline no separator'):
			self.assertEqual(
				self.renderer.render_markup(
					'[named-sub\narg\n\\\\\nargument value\n]'
				),
				'<sub>\nargument value\n</sub>'
			)


class TagFetchTestCase(TestCase):
	class UnimplementedFetchTestRenderer(BaseRenderer):
		pass

	def setUp(self):
		self.renderer = self.UnimplementedFetchTestRenderer()

	def test_unimplemented_error(self):
		with self.assertRaises(NotImplementedError):
			self.renderer.render_markup('[const]')


class TagPrefetchTestCase(TestCase):
	class PrefetchTestRenderer(BaseRenderer):
		tags = {
			'a': 'constant value',
			'b': 'constant value',
			'c': 'constant value',
		}

		def get_tag(self, name):
			return self.tags[name]

	def test_tag_prefetching(self):
		renderer = self.PrefetchTestRenderer()
		renderer.prefetch_tags = MagicMock()
		renderer.render_markup(
			'[a] [b] [b] [a] [c] [a] [c] [a]'
		)
		renderer.prefetch_tags.assert_called_with(
			{'a', 'b', 'c',}
		)


class HookTestCase(TestCase):
	class PreprocessTestRenderer(BaseRenderer):
		def preprocess_block_node(self, node):
			node.children = ['pre',]

			return node

	class PostprocessTestRenderer(BaseRenderer):
		def postprocess_block_node(self, node):
			return f'<post>{node}</post>'

	class ProcessTestRenderer(
		PreprocessTestRenderer,
		PostprocessTestRenderer,
	):
		pass

	def test_preprocess(self):
		renderer = self.PreprocessTestRenderer()
		self.assertEqual(
			renderer.render_markup(
				'value'
			),
			'pre'
		)

	def test_postprocess(self):
		renderer = self.PostprocessTestRenderer()
		self.assertEqual(
			renderer.render_markup(
				'value'
			),
			'<post>value</post>'
		)

	def test_pre_and_postprocess(self):
		renderer = self.ProcessTestRenderer()
		self.assertEqual(
			renderer.render_markup(
				'value'
			),
			'<post>pre</post>'
		)
