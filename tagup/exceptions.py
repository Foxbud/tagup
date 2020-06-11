"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


# Base.

class TagupError(Exception):
    def __init__(self, message, tag_stack_trace):
        super().__init__(message)
        self.tag_stack_trace = tag_stack_trace


# Standalone.

class TagNotFound(TagupError):
    pass


# Syntax.

class TagupSyntaxError(TagupError):
    pass


class NoSuchBuiltin(TagupSyntaxError):
    pass


# Stack.

class TagStackError(TagupError):
    pass


class TagStackUnderflow(TagStackError):
    pass


class TagStackOverflow(TagStackError):
    pass
