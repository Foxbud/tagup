![Travis (.org) branch](https://img.shields.io/travis/Foxbud/tagup/master?label=master&style=flat-square)
&nbsp;
![Codecov branch](https://img.shields.io/codecov/c/github/Foxbud/tagup/master?style=flat-square)

# tagup

**tagup** is a Python module which provides a reference implementation of the [Tagup Language](https://fairburn.dev/tagup/).

This module currently implements [version 1.0.0](https://fairburn.dev/tagup/1.0.0/) of the Tagup Language.

## Quick Start

```python
from tagup import BaseRenderer, TagDictMixin


class TagupRenderer(TagDictMixin, BaseRenderer):
    pass


renderer = TagupRenderer(
    # Optional initial markup tags.
    tags={
        'bold': r'<span style="font-weight: bold">[\\1]</span>',
    }
)

# Manipulate tags using dictionary syntax.
renderer['link'] = (
    r'<a href="[\\1]" [\if target\target="_[\\target]"]>'
    r'[bold [\if 2\[\\2]\[\\1]]]'
    r'</a>'
)

html = renderer.render_markup(
    r'Click [link target\\blank\[\\url]\here] to visit [link\[\\url]]',
    # Provide optional named (and positional) arguments.
    named_args={'url': 'http://example.com'}
)
print(html)
```

## Changelog

**v0.2.3.dev**

- Added "StaticTagMixin" and "TagDictMixin" for "BaseRenderer."
- Added new errors "ImproperlyConfigured," "NamedArgumentMissing," "PositionalArgumentMissing," "TagNotFound" and "TagupSyntaxError."
- Renamed "stack_trace" to "tag_stack_trace" for all custom errors.
- Fixed bug in getitem method of "TagStackTrace."

**v0.2.2**

- Added support for global named arguments.
- Added max tag depth enforcement.
- Fixed bug that prevented the positional loop from functioning when not provided an optional default value.

**v0.2.1**

- Added tag prefetching.

**v0.2.0**

- Renamed "Renderer" to "BaseRenderer."
- Refactored "BaseRenderer" to use method overriding for "get_tag" instead of providing "get_tag_callback" to constructor.
- Removed "cache_tag_ast_callback" from "BaseRenderer" constructor.
- Removed "trim_args" from "BaseRenderer" constructor.
- Added a node pre and post processing hook system.
- Added test cases.
- Various internal optimizations.

**v0.1.3**

- Fixed bug where the "trim_args" option didn't properly remove leading and trailing whitespace in some situations.

**v0.1.2**

- Fixed bug where code called "trim()" rather than "strip()."

**v0.1.1**

- Added non-standard option to trim whitespace from arguments before tag evaluation.
- Fixed bug where whitespace was considered when specifying a name/position for argument substitution.

**v0.1.0**

- Initial release.
