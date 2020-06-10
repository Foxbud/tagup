"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


from copy import deepcopy

from .exceptions import TagStackOverflow, TagStackUnderflow


class StackEntry:
    def __init__(self, tag_name, line=None, column=None):
        self.tag_name = tag_name
        self.line = line
        self.column = column

    def __str__(self):
        if self.line is None or self.column is None:
            return f'{self.tag_name}'
        else:
            return f'{self.line},{self.column} -> {self.tag_name}'


class TagStack:
    ROOT_ENTRY = StackEntry('ROOT')

    def __init__(self, max_depth):
        self._capacity = max_depth + 1
        self._tags = [self.ROOT_ENTRY]

    def push(self, tag_name, line, column):
        self._tags.append(StackEntry(tag_name, line, column))
        if len(self._tags) > self._capacity:
            err = TagStackOverflow(
                str(self),
                self._get_stack_trace()
            )
            self._tags.pop()
            raise err

    def pop(self):
        if self._tags[-1] is self.ROOT_ENTRY:
            raise TagStackUnderflow(
                'pop from empty stack',
                self._get_stack_trace()
            )
        else:
            self._tags.pop()

    def _get_stack_trace(self):
        return deepcopy(self._tags)

    def __str__(self):
        return ':'.join(str(e) for e in self._tags)
