from dataclasses import dataclass, fields
from typing import Callable, List, Dict, Union, NamedTuple, Iterable

Action = Callable[[], None]
Check = Callable[[], bool]
UserConfirm = Callable[[str], None]
Procedure = str


class Conditional(NamedTuple):
    condition: str
    met: Procedure
    fail: Procedure


Statement = Union[Procedure, Conditional]


@dataclass
class Exec:
    procedure: str
    index: int


@dataclass
class SimpleCommands:
    skip: Action
    step: Action
    left: Action
    right: Action
    pick: Action
    put: Action


@dataclass
class Conditions:
    ifwall: Check
    ifmark: Check


class Program:
    _tokens_expected = {"define": 2, "run": 2}

    def __init__(
        self,
        lines: Iterable[str],
        commands: SimpleCommands,
        conditions: Conditions,
        confirm,
    ):
        self.main = None
        self.current = None
        self.stack: List[Exec] = []
        self.procedures: Dict[Procedure, List[Procedure]] = {}
        self._commands: SimpleCommands = commands
        self._conditions: Conditions = conditions
        for k in fields(self._conditions):
            self._tokens_expected[k.name] = 3
        self._confirm = confirm
        self._proc_to_check: Dict[Procedure, List[int]] = {}
        for lineno, line in enumerate(lines, 1):
            self._parse_line(lineno, line)
        self._check_procedures()

    def _add_to_check(self, lineno: int, *args):
        for name in args:
            if hasattr(self._commands, name):
                continue
            self._proc_to_check.setdefault(name, []).append(lineno)

    def _parse_line(self, lineno: int, line: str):
        # discard comments
        line = line.partition("#")[0]

        tokens = line.lower().split()
        if not tokens:  # empty line
            return

        if len(tokens) != Program._tokens_expected.get(tokens[0], 1):
            raise RuntimeError(f"line {lineno}: wrong number of tokens")

        if self.current is None:
            self._parse_decl(lineno, tokens)
        else:
            self._parse_command(lineno, tokens)

    def _parse_decl(self, lineno, decl):
        if decl[0] == "define":
            if decl[1] in self.procedures:
                raise RuntimeError(f"line {lineno}: multiple definitions of {decl[1]}")

            self.current = []
            self.procedures[decl[1]] = self.current
        elif decl[0] == "run":
            if self.main:
                raise RuntimeError("line {}: multiple RUN declarations".format(lineno))
            self._add_to_check(lineno, decl[1])
            self.main = decl[1]
        else:
            raise RuntimeError(f"line {lineno}: unknown declaration {decl[0]}")

    def _parse_command(self, lineno, command):
        if command[0] == "end":
            if not self.current:
                raise RuntimeError("line {}: procedure cannot be empty".format(lineno))

            self.current = None
        elif hasattr(self._conditions, command[0]):
            self._add_to_check(lineno, *command[1:])
            self.current.append(Conditional(*command))
        else:  # procedure call
            self._add_to_check(lineno, command[0])
            self.current.append(command[0])

    def _check_procedures(self):
        for name, lines in self._proc_to_check.items():
            if name not in self.procedures:
                raise RuntimeError(
                    f"Procedure '{name}' not defined on lines "
                    f"{', '.join(map(str, lines))}"
                )
        del self._proc_to_check

    def run(self):
        if self.main is None:
            raise RuntimeError("no RUN declaration")

        # use explicit call stack to avoid Python stack overflow
        self.stack.append(Exec(self.main, 0))

        while self.stack:
            top = self.stack[-1]
            procedure_list = self.procedures[top.procedure]
            command = procedure_list[top.index]
            if self._confirm is not None:
                com_str = command if isinstance(command, str) else ' '.join(command)
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

    def _exec(self, command):
        if isinstance(command, Conditional):
            self._exec(command[1 if getattr(self._conditions, command[0])() else 2])
        elif hasattr(self._commands, command):
            getattr(self._commands, command)()
        else:  # procedure call
            if command not in self.procedures:
                raise RuntimeError("procedure not found: " + command)

            self.stack.append(Exec(command, 0))
