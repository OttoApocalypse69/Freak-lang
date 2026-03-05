from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional


class TokenType(Enum):
    # Literals
    INT_LIT = "INT_LIT"
    FLOAT_LIT = "FLOAT_LIT"
    STRING_LIT = "STRING_LIT"
    BOOL_LIT = "BOOL_LIT"  # true false yes no hai iie

    # Keywords — variables and functions
    PILOT = "pilot"
    TASK = "task"
    GIVE_BACK = "give back"
    SAY = "say"
    SHAPE = "shape"
    IMPL = "impl"
    FOR_KW = "for"  # 'for' in 'for each'
    EACH = "each"
    IN = "in"
    DOCTRINE = "doctrine"
    LAUNCH = "launch"
    USE = "use"
    AS = "as"

    # Keywords — control flow
    IF = "if"
    ELSE = "else"
    WHEN = "when"
    REPEAT = "repeat"
    TIMES = "times"
    UNTIL = "until"
    DONE = "done"
    CONTINUE = "continue"
    BREAK = "break"

    # Keywords — error handling
    CHECK = "check"
    RESULT_KW = "result"
    GOT = "got"
    NOBODY = "nobody"
    SOME = "some"
    OK = "ok"
    ERR = "err"
    OR_ELSE = "or else"

    # Keywords — memory
    LEND = "lend"
    MUT = "mut"
    MOVE = "move"
    COPY = "copy"
    TRUST_ME = "trust me"

    # Keywords — anime
    PILOT_KW = "pilot"  # same as PILOT — variable keyword
    TRAINING_ARC = "training arc"
    SESSIONS = "sessions"
    MAX = "max"
    FORESHADOW = "foreshadow"
    PAYOFF = "payoff"
    ROUTE_KW = "route"
    KNOWING = "knowing this will hurt"
    SADLY = "sadly"
    FOR_SCIENCE = "for science"
    ON_MY_HONOR = "on my honor as"
    DEUS_EX_MACHINA = "deus_ex_machina"
    ISEKAI = "isekai"
    EVENTUALLY = "eventually"
    BRINGING_BACK = "bringing back"

    # Operators
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    PERCENT = "%"
    STAR_STAR = "**"
    EQ_EQ = "=="
    BANG_EQ = "!="
    LT = "<"
    GT = ">"
    LT_EQ = "<="
    GT_EQ = ">="
    AND = "and"
    OR = "or"
    NOT = "not"
    PIPE = "|>"
    QUESTION = "?"
    BANG = "!"
    ARROW = "->"
    FAT_ARROW = "=>"
    PLUS_ULTRA = "PLUS ULTRA"
    NAKAMA = "NAKAMA"
    FINAL_FORM = "FINAL FORM"
    TSUNDERE = "TSUNDERE"

    # Delimiters
    LBRACE = "{"
    RBRACE = "}"
    LPAREN = "("
    RPAREN = ")"
    LBRACKET = "["
    RBRACKET = "]"
    COMMA = ","
    COLON = ":"
    SEMICOLON = ";"
    DOT = "."
    COLON_COLON = "::"
    PIPE_SINGLE = "|"  # for closure args |x|
    AT = "@"

    # Assignment
    EQ = "="
    PLUS_EQ = "+="
    MINUS_EQ = "-="
    STAR_EQ = "*="
    SLASH_EQ = "/="

    # Special
    IDENT = "IDENT"
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    UNDERSCORE = "_"


BOOL_KEYWORDS = {
    "true": True,
    "false": False,
    "yes": True,
    "no": False,
    "hai": True,
    "iie": False,
}


@dataclass
class Token:
    type: TokenType
    lexeme: str
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:  # pragma: no cover - for debugging
        return f"Token({self.type}, {self.lexeme!r}, {self.value!r}, {self.line}:{self.column})"


class LexerError(Exception):
    pass


class Lexer:
    """
    FREAK Lite lexer: turns source text into a flat list of tokens.

    First target program:

        pilot x = 42 and say "Hello, {x}!"
    """

    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line, self.column))
        return self.tokens

    # Core scanning -----------------------------------------------------

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        ch = self.source[self.current]
        self.current += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def _add_token(self, type_: TokenType, literal: Any = None) -> None:
        text = self.source[self.start : self.current]
        self.tokens.append(
            Token(type_, text, literal, self.line, self.column - len(text))
        )

    def _scan_token(self) -> None:
        c = self._advance()

        # Whitespace
        if c in " \t\r":
            return

        if c == "\n":
            self._add_token(TokenType.NEWLINE)
            return

        # Comments
        if c == "-" and self._match("-"):
            while self._peek() != "\n" and not self._is_at_end():
                self._advance()
            return

        # Single-character tokens and simple two-character combos
        if c == "(":
            self._add_token(TokenType.LPAREN)
            return
        if c == ")":
            self._add_token(TokenType.RPAREN)
            return
        if c == "{":
            self._add_token(TokenType.LBRACE)
            return
        if c == "}":
            self._add_token(TokenType.RBRACE)
            return
        if c == "[":
            self._add_token(TokenType.LBRACKET)
            return
        if c == "]":
            self._add_token(TokenType.RBRACKET)
            return
        if c == ",":
            self._add_token(TokenType.COMMA)
            return
        if c == ":":
            if self._match(":"):
                self._add_token(TokenType.COLON_COLON)
            else:
                self._add_token(TokenType.COLON)
            return
        if c == ";":
            # Semicolons are optional and ignored.
            return
        if c == ".":
            self._add_token(TokenType.DOT)
            return
        if c == "@":
            self._add_token(TokenType.AT)
            return
        if c == "|":
            if self._match(">"):
                self._add_token(TokenType.PIPE)
            else:
                self._add_token(TokenType.PIPE_SINGLE)
            return

        if c == "!":
            if self._match("="):
                self._add_token(TokenType.BANG_EQ)
            else:
                self._add_token(TokenType.BANG)
            return

        if c == "?":
            self._add_token(TokenType.QUESTION)
            return

        if c == "=":
            if self._match("="):
                self._add_token(TokenType.EQ_EQ)
            elif self._match(">"):
                self._add_token(TokenType.FAT_ARROW)
            else:
                self._add_token(TokenType.EQ)
            return

        if c == ">":
            if self._match("="):
                self._add_token(TokenType.GT_EQ)
            else:
                self._add_token(TokenType.GT)
            return

        if c == "<":
            if self._match("="):
                self._add_token(TokenType.LT_EQ)
            else:
                self._add_token(TokenType.LT)
            return

        if c == "+":
            if self._match("="):
                self._add_token(TokenType.PLUS_EQ)
            else:
                self._add_token(TokenType.PLUS)
            return

        if c == "-":
            if self._match("="):
                self._add_token(TokenType.MINUS_EQ)
            elif self._match(">"):
                self._add_token(TokenType.ARROW)
            else:
                self._add_token(TokenType.MINUS)
            return

        if c == "*":
            if self._match("*"):
                self._add_token(TokenType.STAR_STAR)
            elif self._match("="):
                self._add_token(TokenType.STAR_EQ)
            else:
                self._add_token(TokenType.STAR)
            return

        if c == "/":
            if self._match("="):
                self._add_token(TokenType.SLASH_EQ)
            else:
                self._add_token(TokenType.SLASH)
            return

        if c == "%":
            self._add_token(TokenType.PERCENT)
            return

        # Literals
        if c.isdigit():
            self._number(c)
            return

        if c == '"':
            self._string()
            return

        # Identifiers and keywords / multi-word tokens
        if self._is_identifier_start(c):
            self._identifier_or_keyword(c)
            return

        raise LexerError(
            f"Unexpected character {c!r} at line {self.line}, column {self.column}"
        )

    # Identifier / keyword handling -------------------------------------

    def _is_identifier_start(self, c: str) -> bool:
        return c.isalpha() or c == "_"

    def _is_identifier_part(self, c: str) -> bool:
        return c.isalnum() or c == "_"

    def _identifier_or_keyword(self, first_char: str) -> None:
        # We already consumed first_char; continue while identifier chars.
        while self._is_identifier_part(self._peek()):
            self._advance()

        lexeme = self.source[self.start : self.current]
        lower = lexeme.lower()

        # Bool literals
        if lower in BOOL_KEYWORDS:
            self._add_token(TokenType.BOOL_LIT, BOOL_KEYWORDS[lower])
            return

        # Multi-word tokens that begin with this word (greedy). This must be
        # checked *before* single-word keywords so that phrases like
        # "or else" are lexed as a single token when possible.
        multi = self._try_multi_word_keyword(lexeme)
        if multi is not None:
            self._add_token(*multi)
            return

        # Single-word keywords and operators that are alpha-based
        keyword_map = {
            "pilot": TokenType.PILOT,
            "task": TokenType.TASK,
            "say": TokenType.SAY,
            "shape": TokenType.SHAPE,
            "impl": TokenType.IMPL,
            "for": TokenType.FOR_KW,
            "each": TokenType.EACH,
            "in": TokenType.IN,
            "doctrine": TokenType.DOCTRINE,
            "launch": TokenType.LAUNCH,
            "use": TokenType.USE,
            "as": TokenType.AS,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "when": TokenType.WHEN,
            "repeat": TokenType.REPEAT,
            "times": TokenType.TIMES,
            "until": TokenType.UNTIL,
            "done": TokenType.DONE,
            "continue": TokenType.CONTINUE,
            "break": TokenType.BREAK,
            "check": TokenType.CHECK,
            "result": TokenType.RESULT_KW,
            "got": TokenType.GOT,
            "nobody": TokenType.NOBODY,
            "some": TokenType.SOME,
            "ok": TokenType.OK,
            "err": TokenType.ERR,
            "lend": TokenType.LEND,
            "mut": TokenType.MUT,
            "move": TokenType.MOVE,
            "copy": TokenType.COPY,
            "foreshadow": TokenType.FORESHADOW,
            "payoff": TokenType.PAYOFF,
            "route": TokenType.ROUTE_KW,
            "sadly": TokenType.SADLY,
            "sessions": TokenType.SESSIONS,
            "max": TokenType.MAX,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "not": TokenType.NOT,
            "_": TokenType.UNDERSCORE,
            "deus_ex_machina": TokenType.DEUS_EX_MACHINA,
            "isekai": TokenType.ISEKAI,
            "eventually": TokenType.EVENTUALLY,
            # Upper-case anime operators (case-sensitive)
            "NAKAMA": TokenType.NAKAMA,
            "TSUNDERE": TokenType.TSUNDERE,
        }

        # Preserve original case for lexeme, but match keywords in a mostly
        # case-insensitive way for the "normal" keywords. Anime operators
        # remain case-sensitive via explicit entries.
        token_type = keyword_map.get(lexeme) or keyword_map.get(lower)

        if token_type is not None:
            self._add_token(token_type)
        else:
            # Fallback: identifier
            self._add_token(TokenType.IDENT, lexeme)

    def _try_multi_word_keyword(
        self, first_word: str
    ) -> Optional[tuple[TokenType, Any]]:
        """
        Attempt to match any multi-word keyword or operator starting with first_word.
        If successful, this method advances self.current past the phrase and returns
        (TokenType, literal).
        """
        # Map of starting word (lowercased) to list of (full phrase words, TokenType).
        MULTI_WORD: dict[str, List[tuple[List[str], TokenType]]] = {
            "give": [(["give", "back"], TokenType.GIVE_BACK)],
            "or": [(["or", "else"], TokenType.OR_ELSE)],
            "trust": [(["trust", "me"], TokenType.TRUST_ME)],
            "training": [(["training", "arc"], TokenType.TRAINING_ARC)],
            "for": [
                (["for", "science"], TokenType.FOR_SCIENCE),
            ],
            "knowing": [(["knowing", "this", "will", "hurt"], TokenType.KNOWING)],
            "on": [(["on", "my", "honor", "as"], TokenType.ON_MY_HONOR)],
            "plus": [(["PLUS", "ULTRA"], TokenType.PLUS_ULTRA)],
            "final": [(["FINAL", "FORM"], TokenType.FINAL_FORM)],
            "bringing": [(["bringing", "back"], TokenType.BRINGING_BACK)],
        }

        lower_first = first_word.lower()
        candidates = MULTI_WORD.get(first_word) or MULTI_WORD.get(lower_first)
        if not candidates:
            return None

        # Save current position to roll back if no candidate matches.
        save_current = self.current
        save_line = self.line
        save_col = self.column

        for words, token_type in candidates:
            # We've already consumed the first word; ensure it matches.
            if words[0].lower() != lower_first:
                continue

            # Try to read the remaining words in the phrase.
            ok = True
            for w in words[1:]:
                # Skip a single space or newline between words.
                if self._peek().isspace():
                    # Allow multiple spaces/newlines but require at least one.
                    while self._peek().isspace() and self._peek() not in ("\0",):
                        # Do not skip past comments; phrase cannot cross comment.
                        if self._peek() == "\n":
                            # Newline allowed inside phrase.
                            self._advance()
                            break
                        self._advance()

                # Now read the next "word" token characters.
                if not self._is_identifier_start(self._peek()):
                    ok = False
                    break

                start_word = self.current
                self._advance()
                while self._is_identifier_part(self._peek()):
                    self._advance()
                word_text = self.source[start_word : self.current]
                if word_text.lower() != w.lower():
                    ok = False
                    break

            if ok:
                # Entire phrase matched.
                return token_type, None

            # Roll back and try next candidate.
            self.current = save_current
            self.line = save_line
            self.column = save_col

        return None

    # Numbers -----------------------------------------------------------

    def _number(self, first_digit: str) -> None:
        # Support decimal, hex (0x..), and binary (0b..) integers plus floats.
        if first_digit == "0" and self._peek() in ("x", "X"):
            # Hex literal
            self._advance()  # consume x
            while self._peek().isalnum():
                self._advance()
            text = self.source[self.start : self.current]
            value = int(text, 16)
            self._add_token(TokenType.INT_LIT, value)
            return

        if first_digit == "0" and self._peek() in ("b", "B"):
            # Binary literal
            self._advance()  # consume b
            while self._peek() in ("0", "1"):
                self._advance()
            text = self.source[self.start : self.current]
            value = int(text, 2)
            self._add_token(TokenType.INT_LIT, value)
            return

        while self._peek().isdigit():
            self._advance()

        is_float = False
        if self._peek() == "." and self._peek_next().isdigit():
            is_float = True
            self._advance()  # consume '.'
            while self._peek().isdigit():
                self._advance()

        # Optional numeric suffixes (u, t, f, b) — for now we parse the core number
        # and leave suffix handling to the type checker / parser. We just drop suffix.
        if self._peek().isalpha():
            # Consume suffix characters (e.g., 'u', 't', 'f', 'b').
            while self._peek().isalpha():
                self._advance()

        text = self.source[self.start : self.current]
        if is_float:
            value = float(text.rstrip("utfbUTFB"))
            self._add_token(TokenType.FLOAT_LIT, value)
        else:
            # Strip possible suffix from integer.
            core = ""
            for ch in text:
                if ch.isdigit():
                    core += ch
                else:
                    break
            value = int(core)
            self._add_token(TokenType.INT_LIT, value)

    # Strings -----------------------------------------------------------

    # Escape sequence map for strings.
    _ESCAPE_MAP = {
        "n": "\n",
        "t": "\t",
        '"': '"',
        "\\": "\\",
        "r": "\r",
        "0": "\0",
    }

    def _string(self) -> None:
        # Consume until closing quote or EOF. Interpolation markers { } are
        # tracked later at parse time; lexer treats whole literal as STRING_LIT.
        # Supports escape sequences: \n \t \" \\ \r \0
        value_chars: list[str] = []
        while self._peek() != '"' and not self._is_at_end():
            ch = self._advance()
            if ch == "\\":
                # Escape sequence
                if self._is_at_end():
                    raise LexerError(
                        f"Unterminated escape sequence at line {self.line}"
                    )
                esc = self._advance()
                mapped = self._ESCAPE_MAP.get(esc)
                if mapped is not None:
                    value_chars.append(mapped)
                else:
                    # Unknown escape — keep both characters as-is
                    value_chars.append("\\")
                    value_chars.append(esc)
            elif ch == "\n":
                # Multiline strings are allowed; NEWLINE tokens are not emitted inside.
                value_chars.append(ch)
            else:
                value_chars.append(ch)

        if self._is_at_end():
            raise LexerError(f"Unterminated string at line {self.line}")

        # Consume closing "
        self._advance()

        # The lexeme is the raw source text including quotes.
        text = self.source[self.start : self.current]
        # The value is the processed string with escape sequences resolved.
        value = "".join(value_chars)
        self.tokens.append(
            Token(TokenType.STRING_LIT, text, value, self.line, self.column - len(text))
        )


__all__ = ["TokenType", "Token", "Lexer", "LexerError"]
