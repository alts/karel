""" Parse and run recursive Karel programs.


"""
from dataclasses import dataclass, fields
from typing import Callable, List, Dict, Union, NamedTuple, Iterable, Optional, TypeVar

Action = Callable[[], None]
""" Action that can be called when command is run. """

Check = Callable[[], bool]
""" Check that can be performed when conditional is run. """

UserConfirm = Callable[[str], None]
""" Function that shows message to user and waits for response. """

Procedure = str
""" Procedure identification - currently its name. """


class Conditional(NamedTuple):
    """ Ternary operator 'IfThenElse' in this order. """

    condition: str
    met: Procedure
    fail: Procedure


Statement = Union[Procedure, Conditional]
""" Statements are procedure/command names and conditional statements.

They compose the body of procedure definition.
"""


@dataclass
class Exec:
    """ Name of executed procedure and position in its list of statements. """

    procedure: str
    index: int


@dataclass
class Commands:
    """ Command names and associated action to be executed. """

    skip: Action
    move: Action
    left: Action
    right: Action
    pick: Action
    put: Action


T_Commands = TypeVar("T_Commands", bound=Commands)


@dataclass
class Conditions:
    """ Check names available to program with associated functions returning bool.

    Attributes:
        ifwall: run on e.g. 'IFWALL SKIP MOVE'
        ifmark: run on e.g. 'IFMARK PICK MAIN'
    """

    ifwall: Check
    ifmark: Check


T_Conditions = TypeVar("T_Conditions", bound=Conditions)


class Program:
    """ Parse and run Karel the Robot recursive non Python programs.

    Attributes:
        main: Name of the procedure that will be first run.
        stack: Explicit stack of procedures to be executed, see run function.
        procedures: Defined procedures and their bodies.
    """

    _tokens_expected = {"define": 2, "run": 2}

    def __init__(
        self,
        lines: Iterable[str],
        commands: T_Commands,
        conditions: T_Conditions,
        confirm: Optional[UserConfirm] = None,
    ):
        self.main: Optional[Procedure] = None
        """ Name of the procedure that will be first run. """

        # Try to avoid Python stack overflow
        self.stack: List[Exec] = []
        """ Explicit stack of procedures to be executed, see run function. """

        self.procedures: Dict[Procedure, List[Statement]] = {}
        """ Defined procedures and their bodies."""

        self._commands: T_Commands = commands
        """ Commands that can be parsed and run. """

        self._conditions: T_Conditions = conditions
        """ Check names available to program with functions returning bool. """

        for k in fields(self._conditions):
            self._tokens_expected[k.name] = 3

        self._confirm: Optional[UserConfirm] = confirm
        """ Optionally ask user to confirm next command. """

        self._proc_to_check: Dict[Procedure, List[int]] = {}
        """ Temporarily store procedure names for later check. """

        self._current: Optional[List[Statement]] = None
        """ The currently defined procedure (temporary). """

        for lineno, line in enumerate(lines, start=1):
            self._parse_line(lineno, line)

        if self._current is not None:
            raise RuntimeError("Last defined procedure not ENDed.")

        del self._current  # No need for this after parsing

        self._check_procedures()
        del self._proc_to_check

    def _add_to_check(self, lineno: int, *names: str) -> None:
        """ Check name(s) later, commands are skipped immediately.

        Args:
            lineno: line number of the checked names
            *names: to be checked later
        """
        for name in names:
            if hasattr(self._commands, name):
                continue
            self._proc_to_check.setdefault(name, []).append(lineno)

    def _parse_line(self, lineno: int, line: str) -> None:
        """ Parse single line, discarding comments, whitespace and letter case.

        Raises:
            RuntimeError: on incorrect line or program structure
        """
        # discard comments and tokenize
        tokens: List[str] = line.partition("#")[0].lower().split()
        if not tokens:  # empty line
            return

        if len(tokens) != Program._tokens_expected.get(tokens[0], 1):
            raise RuntimeError(f"line {lineno}: wrong number of tokens")

        if self._current is None:
            self._parse_decl(lineno, tokens)
        elif tokens[0] == "define":
            raise RuntimeError(
                f"line {lineno}: last procedure not ENDed before DEFINE."
            )
        else:
            self._parse_statement(lineno, tokens)

    def _parse_decl(self, lineno: int, declaration: List[str]) -> None:
        """ Parse lines like 'DEFINE MAIN' and 'RUN MAIN'.

        Raises:
            RuntimeError: on redefinition of procedure or main procedure,
                          also on unrecognized declaration
        """
        if declaration[0] == "define":
            if declaration[1] in self.procedures:
                raise RuntimeError(
                    f"line {lineno}: multiple definitions of {declaration[1]}"
                )

            self._current = []
            self.procedures[declaration[1]] = self._current
        elif declaration[0] == "run":
            if self.main:
                raise RuntimeError(f"line {lineno}: multiple RUN declarations")
            self._add_to_check(lineno, declaration[1])
            self.main = declaration[1]
        else:
            raise RuntimeError(f"line {lineno}: unknown declaration {declaration[0]}")

    def _parse_statement(self, lineno: int, command: List[str]) -> None:
        """ Parse statements and check procedure name later.

        Statements accepted:
          - ``'MOVE'`` and other :class:`Commands`.
          - ``('IFWALL','PASS','MOVE')`` starting with :class:`Conditions`.
          - ``'END'`` of the defined procedure.
        """
        assert self._current is not None
        if command[0] == "end":
            if not self._current:
                raise RuntimeError(
                    f"line {lineno}: procedure cannot be empty, use SKIP."
                )
            self._current = None
        elif hasattr(self._conditions, command[0]):
            self._add_to_check(lineno, *command[1:])
            self._current.append(Conditional(*command))
        else:  # procedure call
            self._add_to_check(lineno, command[0])
            self._current.append(command[0])

    def _check_procedures(self) -> None:
        """ Check all the procedure names encountered.

        Raises:
            RuntimeError: on undefined procedure
        """
        for name, lines in self._proc_to_check.items():
            if name not in self.procedures:
                raise RuntimeError(
                    f"Procedure '{name}' not defined on lines "
                    f"{', '.join(map(str, lines))}"
                )

    def run(self) -> None:
        """ Start program from the procedure set with ``'RUN'``/``self.main``. """
        if self.main is None:
            raise RuntimeError("no RUN declaration")

        self.stack.append(Exec(self.main, 0))

        while self.stack:
            top = self.stack[-1]
            procedure_list = self.procedures[top.procedure]
            command = procedure_list[top.index]
            if self._confirm is not None:
                com_str = command if isinstance(command, str) else " ".join(command)
                self._confirm(
                    f"[{top.procedure.upper()}:{top.index},"
                    f"stack size:{len(self.stack)}] "
                    f"{com_str.upper()} "
                )
            top.index += 1  # advance program counter

            # optimisation: tail recursion (pop early)
            if top.index == len(procedure_list):
                self.stack.pop()

            self._exec(command)

    def _exec(self, command: Statement) -> None:
        """ Execute one statement, e.g. ``'MOVE'`` or ``'IFWALL PASS MAIN'``.

        Args:
            command: Either a procedure/command name or conditional statement
        """
        if isinstance(command, Conditional):
            self._exec(command[1 if getattr(self._conditions, command[0])() else 2])
        elif hasattr(self._commands, command):
            getattr(self._commands, command)()
        else:  # procedure call
            if command not in self.procedures:
                raise RuntimeError("procedure not found: " + command)

            self.stack.append(Exec(command, 0))
