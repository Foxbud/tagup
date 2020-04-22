import unittest

from tagup import BaseRenderer


class RenderingTestCase(unittest.TestCase):
	class TestRenderer(BaseRenderer):
		tags = {
			'const': 'constant value',
			'positional-sub': '<sub>[\\\\1]</sub>',
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


class HookTestCase(unittest.TestCase):
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
		self.renderer = self.PreprocessTestRenderer()
		self.assertEqual(
			self.renderer.render_markup(
				'value'
			),
			'pre'
		)

	def test_postprocess(self):
		self.renderer = self.PostprocessTestRenderer()
		self.assertEqual(
			self.renderer.render_markup(
				'value'
			),
			'<post>value</post>'
		)

	def test_pre_and_postprocess(self):
		self.renderer = self.ProcessTestRenderer()
		self.assertEqual(
			self.renderer.render_markup(
				'value'
			),
			'<post>pre</post>'
		)
