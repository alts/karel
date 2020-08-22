""" Parsers for Karel programs.

Currently there are these parsers:

  - :class:`MapParser`
  - ``get_parser`` for program options from user
  - :class:`Program` for parsing recursive non-Python Karel programs.

==============================================================================
                                   LICENSE
==============================================================================

The karel_robot package is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

The karel_robot package is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
the karel_robot package. If not, see `<https://www.gnu.org/licenses/>`_.
"""
from .map import MapParser
from .cli_arguments import get_parser
from .interpret import Program, Commands, Conditions

__all__ = [
    'MapParser',
    'get_parser',
    'Program',
    'Commands',
    'Conditions',
]
