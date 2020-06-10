"""
This file is part of the tagup Python module which is released under MIT.
See file LICENSE for full license details.
"""


from pkg_resources import get_distribution, DistributionNotFound

from .language import BaseRenderer


# Set version number.
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    pass
