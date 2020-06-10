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


class TagStackTrace:
    def __init__(self, entries):
        self._entries = deepcopy(entries)

    def __getitem(self, key):
        return self._entries[key]

    def __str__(self):
        return (
            f'ROOT{":" if self._entries else ""}'
            + ':'.join(str(e) for e in self._entries)
        )


class TagStack:
    def __init__(self, max_depth):
        self._capacity = max_depth
        self._entries = []

    def push(self, tag_name, line, column):
        self._entries.append(StackEntry(tag_name, line, column))
        if len(self._entries) > self._capacity:
            err = TagStackOverflow(
                str(trace := self.stack_trace()),
                stack_trace=trace
            )
            self._entries.pop()
            raise err

    def pop(self):
        if not self._entries:
            raise TagStackUnderflow(
                'pop from empty stack',
                stack_trace=self.stack_trace()
            )
        else:
            self._entries.pop()

    def stack_trace(self):
        return TagStackTrace(self._entries)
