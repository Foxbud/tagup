"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


from unittest import TestCase
from unittest.mock import MagicMock

from tagup import BaseRenderer, TagDictMixin
from tagup.exceptions import (
    NamedArgumentNotFound,
    PositionalArgumentNotFound,
    TagNotFound,
    TagStackOverflow,
    TagupSyntaxError,
)


class RenderingTestCase(TestCase):
    class TestRenderer(BaseRenderer):
        tags = {
            'const': 'constant value',
            'positional-sub': '<sub>[\\\\1]</sub>',
            'named-sub': '<sub>[\\\\arg]</sub>',
            'positional-test': (
                '[\\if 1\\argument was passed]'
            ),
            'positional-test-default': (
                'argument [\\if 1\\was\\wasn\'t] passed'
            ),
            'named-test': (
                '[\\if arg\\argument was passed]'
            ),
            'named-test-default': (
                'argument [\\if arg\\was\\wasn\'t] passed'
            ),
            'positional-loop': (
                '<outer>'
                '[\\loop <inner>[\\item]</inner>]'
                '</outer>'
            ),
            'positional-loop-default': (
                '<outer>'
                '[\\loop <inner>[\\item]</inner>\\no arguments]'
                '</outer>'
            ),
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

    def test_positional_test(self):
        with self.subTest('false w/o default'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[positional-test arg\\\\named arg value]'
                ),
                ''
            )
        with self.subTest('true w/o default'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[positional-test argument value\\arg\\\\named arg value]'
                ),
                'argument was passed'
            )
        with self.subTest('false w/ default'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[positional-test-default arg\\\\named arg value]'
                ),
                'argument wasn\'t passed'
            )
        with self.subTest('true w/ default'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[positional-test-default'
                    '\\argument value\\arg\\\\named arg value]'
                ),
                'argument was passed'
            )

    def test_named_test(self):
        with self.subTest('false w/o default'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[named-test argument value]'
                ),
                ''
            )
        with self.subTest('true w/o default'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[positional-test arg\\\\named arg value\\argument value]'
                ),
                'argument was passed'
            )
        with self.subTest('false w/ default'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[named-test-default argument value]'
                ),
                'argument wasn\'t passed'
            )
        with self.subTest('true w/ default'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[named-test-default'
                    '\\arg\\\\named arg value\\argument value]'
                ),
                'argument was passed'
            )

    def test_positional_loop(self):
        with self.subTest('0 items w/o default'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[positional-loop]'
                ),
                '<outer></outer>'
            )
        with self.subTest('3 items w/o default'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[positional-loop arg 1\\arg 2\\arg 3]'
                ),
                '<outer>'
                '<inner>arg 1</inner>'
                '<inner>arg 2</inner>'
                '<inner>arg 3</inner>'
                '</outer>'
            )
        with self.subTest('0 items w/ default'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[positional-loop-default]'
                ),
                '<outer>no arguments</outer>'
            )
        with self.subTest('3 items w/ default'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[positional-loop-default arg 1\\arg 2\\arg 3]'
                ),
                '<outer>'
                '<inner>arg 1</inner>'
                '<inner>arg 2</inner>'
                '<inner>arg 3</inner>'
                '</outer>'
            )


class TagFetchTestCase(TestCase):
    class UnimplementedFetchTestRenderer(BaseRenderer):
        pass

    class ImplementedFetchTestRenderer(BaseRenderer):
        tags = {
            'a': 'constant value',
        }

        def get_tag(self, name):
            return self.tags[name]

    def test_not_implemented_error(self):
        renderer = self.UnimplementedFetchTestRenderer()
        with self.assertRaises(NotImplementedError) as cm:
            renderer.render_markup('[const]')
        self.assertEqual(
            str(cm.exception),
            (
                'UnimplementedFetchTestRenderer must define '
                'UnimplementedFetchTestRenderer.get_tag()'
            )
        )

    def test_tag_not_found(self):
        renderer = self.ImplementedFetchTestRenderer()
        with self.assertRaises(TagNotFound) as cm:
            renderer.render_markup(
                '[const]'
            )
        self.assertEqual(
            str(cm.exception),
            'ROOT:1,2 -> '
            'const'
        )


class TagPrefetchTestCase(TestCase):
    class PrefetchTestRenderer(BaseRenderer):
        tags = {
            'a': 'constant value',
            'b': 'constant value',
            'c': 'constant value',
            'd': 'constant value',
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
            {'a', 'b', 'c'}
        )


class HookTestCase(TestCase):
    class PreprocessTestRenderer(BaseRenderer):
        def preprocess_block_node(self, node):
            node.children = ['pre']

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


class OverflowTestCase(TestCase):
    class TestRenderer(BaseRenderer):
        tags = {
            'const': 'constant value',
            'positional-sub': '<sub>[\\\\1]</sub>\n[const]',
            'wrapper': '<wrapper>[positional-sub [\\\\1]]</wrapper>',
        }

        def get_tag(self, name):
            return self.tags[name]

    def test_tag_stack_overflow(self):
        renderer = self.TestRenderer(max_depth=2)
        with self.subTest('valid'):
            self.assertEqual(
                renderer.render_markup(
                    '[positional-sub argument value]'
                ),
                '<sub>argument value</sub>\nconstant value'
            )
        with self.subTest('overflow'):
            with self.assertRaises(TagStackOverflow) as cm:
                renderer.render_markup(
                    '[wrapper argument value]'
                )
            self.assertEqual(
                str(cm.exception),
                (
                    'ROOT:1,2 -> '
                    'wrapper:1,11 -> '
                    'positional-sub:2,2 -> '
                    'const'
                )
            )
            # Ensure all tags were popped from stack.
            self.assertEqual(
                len(renderer.tag_stack._entries),
                0
            )


class GlobalTestCase(TestCase):
    class TestRenderer(BaseRenderer):
        tags = {
            'global': (
                '<inner>'
                '[\\if global-arg\\[\\\\global-arg]]'
                '[\\if local-arg\\[\\\\local-arg]]'
                '</inner>'
            ),
            'wrapper': '<wrapper>[global]</wrapper>[\\\\local-arg]',
        }

        def get_tag(self, name):
            return self.tags[name]

    def test_global_named_arguments(self):
        renderer = self.TestRenderer()
        renderer.set_globals({'global-arg': 'global value'})
        self.assertEqual(
            renderer.render_markup(
                '[wrapper local-arg\\\\local value]'
            ),
            '<wrapper><inner>global value</inner></wrapper>local value'
        )


class TagDictMixinTestCase(TestCase):
    class TestRenderer(TagDictMixin, BaseRenderer):
        pass

    def setUp(self):
        self.renderer = self.TestRenderer(
            {
                'wrapper': '<wrapper>[\\\\1]</wrapper>',
            },
            max_depth=1
        )

    def test_get_tag(self):
        with self.subTest('valid'):
            self.assertEqual(
                self.renderer.render_markup(
                    '[wrapper argument value]'
                ),
                '<wrapper>argument value</wrapper>'
            )
        with self.subTest('bad tag'):
            with self.assertRaises(TagNotFound):
                self.renderer.render_markup(
                    '[bad-tag]'
                )

    def test_dict_operations(self):
        with self.subTest('get'):
            self.assertEqual(
                self.renderer['wrapper'],
                '<wrapper>[\\\\1]</wrapper>'
            )
            with self.assertRaises(KeyError):
                self.renderer['bad-tag']
        with self.subTest('set'):
            self.renderer['new-tag'] = 'constant value'
            self.assertEqual(
                self.renderer['new-tag'],
                'constant value'
            )
            self.assertEqual(
                self.renderer['wrapper'],
                '<wrapper>[\\\\1]</wrapper>'
            )
        with self.subTest('delete'):
            del self.renderer['new-tag']
            with self.assertRaises(KeyError):
                self.renderer['new-tag']
            with self.assertRaises(KeyError):
                del self.renderer['new-tag']

    def test_max_depth(self):
        self.renderer['outer'] = '<outer>[wrapper argument value]</outer>'
        with self.assertRaises(TagStackOverflow):
            self.renderer.render_markup(
                '[outer]'
            )


class BadSyntaxTestCase(TestCase):
    class TestRenderer(BaseRenderer):
        tags = {
            'bad-builtin': '[\\bad]',
            'missing-args': '[\\if]',
            'unclosed-builtin': '[\\o',
        }

        def get_tag(self, name):
            return self.tags[name]

    def setUp(self):
        self.renderer = self.TestRenderer()

    def test_bad_buildin(self):
        with self.assertRaises(TagupSyntaxError) as cm:
            self.renderer.render_markup(
                '[bad-builtin]'
            )
        self.assertEqual(
            str(cm.exception),
            'ROOT:1,2 -> '
            'bad-builtin:1,4 -> '
            'ad'
        )

    def test_missing_arguments(self):
        with self.assertRaises(TagupSyntaxError) as cm:
            self.renderer.render_markup(
                '[missing-args]'
            )
        self.assertEqual(
            str(cm.exception),
            'ROOT:1,2 -> '
            'missing-args:1,5 -> '
            ']'
        )

    def test_unclosed_builtin(self):
        with self.assertRaises(TagupSyntaxError) as cm:
            self.renderer.render_markup(
                '[unclosed-builtin]'
            )
        self.assertEqual(
            str(cm.exception),
            'ROOT:1,2 -> '
            'unclosed-builtin:1,3 -> '
            'END'
        )


class ArgsNotFoundTestCase(TestCase):
    class TestRenderer(BaseRenderer):
        tags = {
            'named-arg-not-found': '[\\\\bad-arg]',
            'pos-arg-not-found': '[\\\\1]',
        }

        def get_tag(self, name):
            return self.tags[name]

    def setUp(self):
        self.renderer = self.TestRenderer()

    def test_named_argument_not_found(self):
        with self.assertRaises(NamedArgumentNotFound) as cm:
            self.renderer.render_markup(
                '[named-arg-not-found]'
            )
        self.assertEqual(
            str(cm.exception),
            'ROOT:1,2 -> '
            'named-arg-not-found:1,4 -> '
            'bad-arg'
        )

    def test_positional_argument_not_found(self):
        with self.assertRaises(PositionalArgumentNotFound) as cm:
            self.renderer.render_markup(
                '[pos-arg-not-found]'
            )
        self.assertEqual(
            str(cm.exception),
            'ROOT:1,2 -> '
            'pos-arg-not-found:1,4 -> '
            '1'
        )
