"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


class TagupError(Exception):
    pass


class TagStackError(TagupError):
    def __init__(self, message, stack_trace):
        super().__init__(message)
        self.stack_trace = stack_trace


class TagStackUnderflow(TagStackError):
    pass


class TagStackOverflow(TagStackError):
    pass
