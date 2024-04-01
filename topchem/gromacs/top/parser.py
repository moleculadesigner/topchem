# -*- coding: utf-8 -*-
"""
tochem.gromacs.top.ast
~~~~~~~~~~~~~~

A module with Lark parser grammar. Allows to read and produce
unpreprocessed topology syntax tree.

The tree hierarchy can be desribed with this scheme:
+ topology
  + line_comment
    COMMENT_TOKEN
  + <pp_directive>
    DIRECTIVE_CONTENT_TOKENS
  + section_header
    SECTION_NAME_TOKEN
  + entry
    ENTRY_TOKENS

This structure can be produced into non-validated unpreprocessed
Topology object or into the preprocessed topology with data validation.
"""

from pathlib import Path

from lark import Lark, Tree
from lark.exceptions import UnexpectedInput

from ...exceptions import TopchemParserError

TERMINALS_EXPLAINED = {
    "SIGNED_INT": "Integer with optional sign: `1234`, `-1234`",
    "SIGNED_FLOAT": "Float, may be in sientific format: `.1`, `-1.`, `0.2e+05`",
    "CNAME": "C-style identifier: `A1`, `_undersored_0`",
    "ID": "Allowed non-number identifier (atom names/types and so on): `-N1*+'`",
    "_IGNORE": (
        r"Non-linebreaking spaces: space, tab; "
        r"escaped newline: `\\s*\r?\n`; empty lines: `\s+\r?\n`"
    ),
    "_INCLUDE": "`#include`",
    "_DEFINE": "`#define`",
    "_UNDEF": "`#undef`",
    "_IFDEF": "`#ifdef`",
    "_IFNDEF": "`#ifndef`",
    "_ELSE": "`#else`",
    "_ENDIF": "`#endif`",
    "PATH": r"Any string, may be interpreted as posix path: `a`, `/a`, `/// \\/.\//`",
    "PPCOMMENT": "Preprocessor comment: `//comment`, `/*comment*/`",
    "COMMENT": "Topology comment: `;comment`",
    "_NEWLINE": r"New line: `\r?\n`",
    "LSQB": "Left square bracket: `[`",
    "RSQB": "Right square bracket: `]`",
}
""" Explanation of grammar teminals for better error handling """


def _explain_terminal(terminal: str) -> str:
    """Provide human readable explanation of grammar teminals"""

    explanation = TERMINALS_EXPLAINED.get(terminal)
    if explanation is None:
        explanation = terminal

    return explanation


_top_parser = Lark.open("gromacs_topology.lark", rel_to=__file__, start="topology", parser="lalr")
""" Lark parser instance to read topology file """


def parse_topology(path: Path | str) -> Tree:
    """
    Read topology file (*.top or *.itp) and produce topology syntax tree

    :param path: Path object or path string to topology to read
    :return: Lark Tree with topology content
    """
    parser_type = "Lark Toopology Parser"
    path = Path(path)
    content = path.read_text() + "\n"  # In case of topology not ended with empty line

    try:
        tree = _top_parser.parse(content)
    except UnexpectedInput as uin:
        if hasattr(uin, "expected"):
            expected = [_explain_terminal(terminal) for terminal in uin.expected]
        elif hasattr(uin, "allowed"):
            expected = [_explain_terminal(terminal) for terminal in uin.allowed]
        else:
            expected = None

        if uin.pos_in_stream is None:
            pos_in_stream = -1
        else:
            pos_in_stream = uin.pos_in_stream

        parser_error = TopchemParserError(
            stream=content,
            pos_in_stream=pos_in_stream,
            line=uin.line,
            column=uin.column,
            parser_type=parser_type,
            file_name=path.as_posix(),
            expected=expected,
        )
        raise parser_error from uin
    return tree
