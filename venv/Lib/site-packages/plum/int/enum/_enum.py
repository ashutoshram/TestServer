# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Interpret bytes as integer enumerated constants."""

import enum

from ..._plum import getbytes
from .._int import Int
from ._enumtype import EnumType


class Enum(Int, enum.Enum, metaclass=EnumType):

    """Interpret bytes as integer enumerated constants.

    :param x: value
    :type x: number or str
    :param int base: base of x when x is ``str``

    """

    __strict_enum__ = True

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):
        nbytes = cls.__nbytes__

        try:
            try:
                value = cls(value)
            except ValueError:
                if cls.__strict_enum__:
                    raise

            chunk = value.to_bytes(nbytes, cls.__byteorder__, signed=cls.__signed__)

        except Exception:
            if dump:
                # use repr in case str or something that otherwise looks like an int
                dump.value = repr(value)
            raise

        if dump:
            dump.value = value
            dump.memory = chunk

        end = offset + nbytes
        buffer[offset:end] = chunk

        return end

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump):
        chunk, offset = getbytes(buffer, offset, cls.__nbytes__, dump)

        value = int.from_bytes(chunk, cls.__byteorder__, signed=cls.__signed__)

        try:
            value = cls(value)
        except ValueError:
            if cls.__strict_enum__:
                raise

        if dump:
            dump.value = value

        return value, offset

    def __repr__(self):
        # override so representation turns out in Python 3.6
        # e.g. <Sample.A: Int(1)> -> <Sample.A: 1>
        enum_repr = enum.IntEnum.__repr__(self)
        if '(' in enum_repr:  # pragma: no cover
            beg, _, int_repr, _ = enum_repr.replace('(', ' ').replace(')', ' ').split()
            enum_repr = f'{beg} {int_repr}>'
        return enum_repr
