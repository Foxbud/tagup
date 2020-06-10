"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


from unittest import TestCase

from tagup.exceptions import TagStackOverflow, TagStackUnderflow
from tagup.stack import TagStack


class TagStackTestCase(TestCase):
    def setUp(self):
        self.stack = TagStack(2)

    def test_push(self):
        with self.subTest('valid'):
            self.stack.push('a', 1, 2)
            self.stack.push('b', 2, 5)
            self.assertEqual(
                str(self.stack.stack_trace()),
                (
                    'ROOT:1,2 -> '
                    'a:2,5 -> '
                    'b'
                )
            )
        with self.subTest('overflow'):
            with self.assertRaises(
                TagStackOverflow,
                msg=(
                    'ROOT:1,2 -> '
                    'a:2,5 -> '
                    'b:4,18 -> '
                    'c'
                )
            ):
                self.stack.push('c', 3, 18)

    def test_pop(self):
        with self.subTest('valid'):
            self.stack.push('a', 1, 2)
            self.stack.push('b', 2, 5)
            self.assertEqual(
                str(self.stack.stack_trace()),
                (
                    'ROOT:1,2 -> '
                    'a:2,5 -> '
                    'b'
                )
            )
            self.stack.pop()
            self.assertEqual(
                str(self.stack.stack_trace()),
                (
                    'ROOT:1,2 -> '
                    'a'
                )
            )
            self.stack.pop()
            self.assertEqual(
                str(self.stack.stack_trace()),
                'ROOT'
            )
        with self.subTest('underflow'):
            with self.assertRaises(TagStackUnderflow):
                self.stack.pop()
