# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Package metadata."""

__all__ = (
    '__title__',
    '__summary__',
    '__uri__',
    '__version_info__',
    '__version__',
    '__author__',
    '__maintainer__',
    '__email__',
    '__copyright__',
    '__license__',
)


class VersionInfo:

    """Package version information.

    Follow 'Semantic Versioning 2.0.0' (https://semver.org/) and
    PEP 440 (https://www.python.org/dev/peps/pep-0440/).

    :releaselevel: 'alpha', 'beta', 'rc' (release candidate), or 'final'
    :major: increment for backward incompatible API change
    :minor: increment for feature addition
    :micro: increment for patch
    :serial: build number (n/a for 'final')

    """

    releaselevel = 'final'
    major = 0
    minor = 3
    micro = 1
    serial = 0

    version = f'{major}.{minor}.{micro}'

    if releaselevel == 'alpha':
        version += 'a' + str(serial)
    elif releaselevel == 'beta':
        version += 'b' + str(serial)
    elif releaselevel == 'rc':
        version += 'rc' + str(serial)
    elif releaselevel == 'final':
        assert serial == 0
    else:
        raise RuntimeError('invalid releaselevel')


__title__ = 'plum-py'
__summary__ = 'Pack/Unpack Memory.'
__uri__ = 'https://plum-py.readthedocs.io/en/latest/index.html'
__version_info__ = VersionInfo  # pylint: disable=invalid-name
__version__ = VersionInfo.version
__author__ = 'Dan Gass'
__maintainer__ = 'Dan Gass'
__email__ = 'dan.gass@gmail.com'
__copyright__ = 'Copyright 2020 Daniel Mark Gass'
__license__ = 'MIT License; http://opensource.org/licenses/MIT'


del VersionInfo
