# -*- coding: utf-8 -*-
"""
topchem.exceptions
~~~~~~~~~~~~~~~~~~

Custom exceptions to provide more relevant information on package errors
"""

from typing import List, Optional, Tuple


class TopchemParserError(Exception):
    """
    Exception to represent generic parser error, showing context
    and explanation of what went wrong
    """

    def __init__(
        self,
        stream: str,
        pos_in_stream: int,
        line: int,
        column: int,
        parser_type: str,
        file_name: str = "",
        expected: Optional[List[str]] = None,
    ):
        self.stream = stream
        self.pos_in_stream = pos_in_stream
        self.line = line
        self.column = column
        self.parser_type = parser_type
        self.file_name = file_name
        self.expected = [] if expected is None else expected

    def get_context(self, span: int = 60) -> Tuple[str, str]:
        """Read the input stream around the failed position and return
        an erroneouus line with pointer

        :param span: how much to read backward and forward to the position
        :return: tuple with context line and a space padded pointer
        """
        assert self.pos_in_stream is not None
        pos = self.pos_in_stream
        start = max(pos - span, 0)
        end = pos + span
        before = self.stream[start:pos].rsplit("\n", 1)[-1]
        after = self.stream[pos:end].split("\n", 1)[0]
        context_line = before + after
        pointer = " " * len(before.expandtabs()) + "^~~~"
        return context_line, pointer

    def __str__(self):
        message = [
            f"{self.parser_type} error while reading {self.file_name} "
            f"at line {self.line}, column {self.column}:"
        ]

        context_line, pointer = self.get_context()
        line_label = f"{self.line}: "
        message.append(line_label + context_line)
        message.append(" " * len(line_label) + pointer)

        if self.expected:
            message.append("Expected input:")
            for entry in self.expected:
                message.append("- " + entry)

        return "\n".join(message)
