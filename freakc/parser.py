from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union

from .lexer import Lexer, LexerError, Token, TokenType

# ===================================================================
#  AST NODES — Bible Section 7.1 (expanded)
# ===================================================================

Statement = Union[
    "PilotDecl",
    "SayStmt",
    "TaskDecl",
    "GiveBack",
    "IfExpr",
    "WhenExpr",
    "ForEach",
    "RepeatTimes",
    "RepeatUntil",
    "TrainingArc",
    "ShapeDecl",
    "ImplBlock",
    "DoctrineDecl",
    "Assign",
    "ExprStmt",
    "CheckMaybe",
    "CheckResult",
    "Annotation",
    "TrustMeBlock",
    "ForeshadowDecl",
    "PayoffStmt",
    "UseImport",
    "DeusExMachina",
    "IsekaiBlock",
    "EventuallyBlock",
]
Expr = Union[
    "IntLit",
    "FloatLit",
    "StrLit",
    "BoolLit",
    "Ident",
    "BinOp",
    "UnaryOp",
    "ListLit",
    "MapLit",
    "TupleLit",
    "Call",
    "MethodCall",
    "FieldAccess",
    "Index",
    "Lambda",
    "SomeExpr",
    "OkExpr",
    "ErrExpr",
    "Nobody",
    "ShapeInstantiation",
    "PathIdent",
]


# --- Declarations ---------------------------------------------------


@dataclass
class Program:
    statements: List[Statement]


@dataclass
class PilotDecl:
    name: str
    type_ann: Optional["TypeExpr"]
    value: Expr
    is_foreshadow: bool = False


@dataclass
class SayStmt:
    value: Expr


@dataclass
class Param:
    name: str
    type_ann: Optional["TypeExpr"] = None


@dataclass
class Block:
    statements: List[Statement]


@dataclass
class TaskDecl:
    name: str
    type_params: List[str]
    params: List[Param]
    return_type: Optional["TypeExpr"]
    body: Union[Block, Expr]
    annotations: List[str]
    is_launch: bool = False


@dataclass
class ShapeDecl:
    name: str
    type_params: List[str]
    fields: List[Param]
    is_launch: bool = False


@dataclass
class ImplBlock:
    doctrine: Optional[str]
    target_type: str
    methods: List[TaskDecl]


@dataclass
class DoctrineDecl:
    name: str
    methods: List[TaskDecl]


@dataclass
class Assign:
    target: Expr
    op: str  # "=", "+=", "-=", "*=", "/="
    value: Expr


@dataclass
class ExprStmt:
    """Bare expression used as a statement (e.g. a function call)."""

    expr: Expr


# --- Expressions ----------------------------------------------------


@dataclass
class IntLit:
    value: int


@dataclass
class FloatLit:
    value: float


@dataclass
class StrLit:
    value: str
    # Interpolation parts: list of (literal_text, expr | None) pairs
    # e.g. "Hello {name}, power {p}" → [("Hello ", Ident("name")), (", power ", Ident("p")), ("", None)]
    parts: Optional[List[Tuple[str, Optional[Expr]]]] = None


@dataclass
class BoolLit:
    value: bool


@dataclass
class Ident:
    name: str


@dataclass
class PathIdent:
    parts: List[str]


@dataclass
class Nobody:
    pass


@dataclass
class SomeExpr:
    value: Expr


@dataclass
class OkExpr:
    value: Expr


@dataclass
class ErrExpr:
    value: Expr


@dataclass
class BinOp:
    op: str
    left: Expr
    right: Expr


@dataclass
class UnaryOp:
    op: str
    operand: Expr


@dataclass
class Call:
    func: Expr
    args: List[Expr]


@dataclass
class MethodCall:
    obj: Expr
    method: str
    args: List[Expr]


@dataclass
class FieldAccess:
    obj: Expr
    field: str


@dataclass
class Index:
    obj: Expr
    index: Expr


@dataclass
class Lambda:
    params: List[Param]
    body: Union[Block, Expr]
    capture_mode: str = "borrow"  # "borrow", "copy", "move", "mut"


@dataclass
class IfExpr:
    condition: Expr
    then_block: Block
    elif_branches: List[Tuple[Expr, Block]]
    else_block: Optional[Block]


@dataclass
class WhenArm:
    pattern: Union[Expr, str]  # value or "_"
    body: Union[Block, Expr]


@dataclass
class WhenExpr:
    subject: Expr
    arms: List[WhenArm]


@dataclass
class ForEach:
    pattern: Expr
    iterable: Expr
    body: Block


@dataclass
class RepeatTimes:
    count: Expr
    body: Block


@dataclass
class RepeatUntil:
    condition: Expr
    body: Block


@dataclass
class TrainingArc:
    condition: Expr
    max_sessions: Expr
    body: Block


@dataclass
class ListLit:
    elements: List[Expr]


@dataclass
class MapLit:
    pairs: List[Tuple[Expr, Expr]]


@dataclass
class TupleLit:
    elements: List[Expr]


@dataclass
class ShapeInstantiation:
    """Point { x: 1, y: 2 }"""

    shape_name: str
    fields: List[Tuple[str, Expr]]


@dataclass
class GiveBack:
    value: Optional[Expr]


@dataclass
class TypeExpr:
    name: str
    params: List["TypeExpr"]
    is_pointer: bool = False
    is_mut_pointer: bool = False


@dataclass
class CheckMaybe:
    """check expr { got x -> ... nobody -> ... }"""

    subject: Expr
    got_name: str  # variable name for the unwrapped value
    got_body: "Block"
    nobody_body: "Block"


@dataclass
class CheckResult:
    """check result expr { ok(x) -> ... err(e) -> ... }"""

    subject: Expr
    ok_name: str
    ok_body: "Block"
    err_name: str
    err_body: "Block"


@dataclass
class Annotation:
    """@protagonist, @nakige, etc. — decorates the next declaration."""

    name: str
    target: Optional[Statement] = None  # the decorated statement


@dataclass
class TrustMeBlock:
    """trust me "reason" on my honor as .level { ... }"""

    reason: str
    honor_level: str
    body: "Block"


@dataclass
class ForeshadowDecl:
    """foreshadow pilot x = expr"""

    decl: "PilotDecl"


@dataclass
class PayoffStmt:
    """payoff x"""

    name: str


@dataclass
class UseImport:
    """use module::{a, b} / use module::* / use module::Name as Alias"""

    module: str
    names: List[str]  # imported names, or ["*"] for wildcard
    alias: Optional[str] = None  # only for single-symbol aliased imports


@dataclass
class DeusExMachina:
    """deus_ex_machina "monologue >= 20 words" { body }"""

    monologue: str
    body: "Block"


@dataclass
class IsekaiBlock:
    """isekai { body } bringing back { name, ... }"""

    body: "Block"
    exports: List[str]


@dataclass
class EventuallyBlock:
    """eventually { body }  or  eventually if cond { body }"""

    body: "Block"
    condition: Optional["Expr"] = None


# ===================================================================
#  PARSER
# ===================================================================

# Update Statement union to include new nodes (kept as comment for reference)
# DeusExMachina, IsekaiBlock, EventuallyBlock are now valid statements.


class ParseError(Exception):
    pass


class Parser:
    """
    Recursive-descent parser for FREAK Lite.

    Grammar precedence (low → high):
        pipe  |>
        or
        and
        equality  ==  !=
        comparison  <  >  <=  >=
        term  +  -
        factor  *  /  %
        power  **
        unary  -  not  !  FINAL_FORM  TSUNDERE
        postfix  .field  (args)  [index]
        primary  literals  identifiers  grouping
    """

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    @classmethod
    def from_source(cls, source: str) -> "Program":
        lexer = Lexer(source)
        try:
            tokens = lexer.tokenize()
        except LexerError as e:
            raise ParseError(str(e)) from e
        parser = cls(tokens)
        return parser.parse()

    # --- Top-level -----------------------------------------------------

    def parse(self) -> Program:
        statements: List[Statement] = []
        while not self._is_at_end():
            while self._match(TokenType.NEWLINE):
                pass
            if self._is_at_end():
                break
            statements.append(self._declaration())
        return Program(statements=statements)

    def _declaration(self) -> Statement:
        # Keywords that start specific constructs
        if self._match(TokenType.PILOT):
            return self._pilot_decl()
        if self._match(TokenType.IF):
            return self._if_stmt()
        if self._match(TokenType.WHEN):
            return self._when_stmt()
        if self._match(TokenType.FOR_KW):
            return self._for_each_stmt()
        if self._match(TokenType.REPEAT):
            return self._repeat_stmt()
        if self._match(TokenType.TRAINING_ARC):
            return self._training_arc_stmt()
        if self._match(TokenType.SAY):
            return self._say_stmt()
        if self._match(TokenType.TASK):
            return self._task_decl()
        if self._match(TokenType.GIVE_BACK):
            return self._give_back_stmt()
        if self._match(TokenType.CHECK):
            return self._check_stmt()
        if self._match(TokenType.SHAPE):
            return self._shape_decl()
        if self._match(TokenType.IMPL):
            return self._impl_block()
        if self._match(TokenType.DOCTRINE):
            return self._doctrine_decl()
        if self._match(TokenType.LAUNCH):
            return self._launch_modified()
        if self._match(TokenType.AT):
            return self._annotation()
        if self._match(TokenType.TRUST_ME):
            return self._trust_me_block()
        if self._match(TokenType.FORESHADOW):
            return self._foreshadow_decl()
        if self._match(TokenType.PAYOFF):
            return self._payoff_stmt()
        if self._match(TokenType.USE):
            return self._use_import()
        if self._match(TokenType.DEUS_EX_MACHINA):
            return self._deus_ex_machina()
        if self._match(TokenType.ISEKAI):
            return self._isekai_block()
        if self._match(TokenType.EVENTUALLY):
            return self._eventually_block()

        # Call wrappers: knowing this will hurt / sadly / for science
        # These are thematic prefixes that strip away, leaving the inner statement.
        if self._match(TokenType.KNOWING):
            self._match(TokenType.COMMA)  # optional comma
            return self._declaration()
        if self._match(TokenType.SADLY):
            return self._declaration()
        if self._match(TokenType.FOR_SCIENCE):
            self._match(TokenType.COMMA)  # optional comma
            return self._declaration()

        # Fallback: expression statement (could be a call, assignment, etc.)
        return self._expr_or_assign_stmt()

    # --- Specific constructs -------------------------------------------

    def _pilot_decl(self) -> PilotDecl:
        name_tok = self._consume(TokenType.IDENT, "Expected identifier after 'pilot'")
        type_ann: Optional[TypeExpr] = None
        if self._match(TokenType.COLON):
            type_ann = self._type_expr()
        self._consume(TokenType.EQ, "Expected '=' in pilot declaration")
        value_expr = self._expression()
        return PilotDecl(name=name_tok.value, type_ann=type_ann, value=value_expr)

    def _say_stmt(self) -> SayStmt:
        value_expr = self._expression()
        return SayStmt(value=value_expr)

    def _if_stmt(self) -> IfExpr:
        condition = self._expression()
        then_block = self._consume_block("Expected '{' or block after if condition")

        elif_branches: List[Tuple[Expr, Block]] = []
        else_block: Optional[Block] = None

        while self._match(TokenType.ELSE):
            if self._match(TokenType.IF):
                cond = self._expression()
                blk = self._consume_block("Expected '{' after else if condition")
                elif_branches.append((cond, blk))
            else:
                else_block = self._consume_block("Expected '{' after else")
                break

        return IfExpr(
            condition=condition,
            then_block=then_block,
            elif_branches=elif_branches,
            else_block=else_block,
        )

    def _when_stmt(self) -> WhenExpr:
        subject = self._expression()
        self._consume(TokenType.LBRACE, "Expected '{' after when subject")

        arms: List[WhenArm] = []
        while (
            not self._check(TokenType.RBRACE)
            and not self._check(TokenType.DONE)
            and not self._is_at_end()
        ):
            while self._match(TokenType.NEWLINE):
                pass
            if self._check(TokenType.RBRACE) or self._check(TokenType.DONE):
                break

            # Pattern
            if self._match(TokenType.UNDERSCORE):
                pattern: Union[Expr, str] = "_"
            else:
                pattern = self._expression()

            self._consume(TokenType.ARROW, "Expected '->' in when arm")

            # Body can be a block, a statement (say, pilot, etc.), or expression
            if self._check(TokenType.LBRACE):
                self._advance()
                body: Union[Block, Expr] = self._block_body()
            elif (
                self._check(TokenType.SAY)
                or self._check(TokenType.PILOT)
                or self._check(TokenType.IF)
                or self._check(TokenType.GIVE_BACK)
                or self._check(TokenType.FOR_KW)
                or self._check(TokenType.REPEAT)
                or self._check(TokenType.WHEN)
                or self._check(TokenType.TRAINING_ARC)
            ):
                # Statement as arm body — wrap in a block
                stmt = self._declaration()
                body = Block(statements=[stmt])
            else:
                body = self._expression()

            arms.append(WhenArm(pattern=pattern, body=body))

            while self._match(TokenType.NEWLINE):
                pass

        self._consume_block_end("Expected '}' or 'done' to close when")
        return WhenExpr(subject=subject, arms=arms)

    def _for_each_stmt(self) -> ForEach:
        self._consume(TokenType.EACH, "Expected 'each' after 'for'")
        pattern_expr = self._expression()
        self._consume(TokenType.IN, "Expected 'in' in for each loop")
        iterable = self._expression()
        body = self._consume_block("Expected '{' to start for each body")
        return ForEach(pattern=pattern_expr, iterable=iterable, body=body)

    def _repeat_stmt(self) -> Union[RepeatTimes, RepeatUntil]:
        if self._match(TokenType.UNTIL):
            condition = self._expression()
            body = self._consume_block("Expected '{' after repeat until condition")
            return RepeatUntil(condition=condition, body=body)

        count_expr = self._expression()
        self._consume(TokenType.TIMES, "Expected 'times' after repeat count")
        body = self._consume_block("Expected '{' to start repeat body")
        return RepeatTimes(count=count_expr, body=body)

    def _training_arc_stmt(self) -> TrainingArc:
        self._consume(TokenType.UNTIL, "Expected 'until' after 'training arc'")
        condition = self._expression()
        self._consume(TokenType.MAX, "Expected 'max' in training arc")
        max_sessions = self._expression()
        self._consume(
            TokenType.SESSIONS, "Expected 'sessions' after training arc max count"
        )
        body = self._consume_block("Expected '{' to start training arc body")
        return TrainingArc(condition=condition, max_sessions=max_sessions, body=body)

    def _task_decl(
        self, annotations: Optional[List[str]] = None, is_launch: bool = False
    ) -> TaskDecl:
        if annotations is None:
            annotations = []
        name_tok = self._consume(TokenType.IDENT, "Expected task name after 'task'")

        # Generic type parameters <T, U>
        type_params: List[str] = []
        if self._check(TokenType.LT):
            self._advance()
            while True:
                tp = self._consume(TokenType.IDENT, "Expected type parameter name")
                type_params.append(tp.value)
                if not self._match(TokenType.COMMA):
                    break
            self._consume(TokenType.GT, "Expected '>' after type parameters")

        # Parameters
        self._consume(TokenType.LPAREN, "Expected '(' after task name")
        params: List[Param] = []
        if not self._check(TokenType.RPAREN):
            while True:
                # Handle 'self' parameter
                if self._check(TokenType.IDENT) and self._peek().value == "self":
                    self._advance()
                    params.append(Param(name="self", type_ann=None))
                else:
                    param_name = self._consume(
                        TokenType.IDENT, "Expected parameter name"
                    ).lexeme
                    p_type: Optional[TypeExpr] = None
                    if self._match(TokenType.COLON):
                        p_type = self._type_expr()
                    params.append(Param(name=param_name, type_ann=p_type))
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RPAREN, "Expected ')' after parameters")

        # Optional return type
        return_type: Optional[TypeExpr] = None
        if self._match(TokenType.ARROW):
            return_type = self._type_expr()

        # Body: block, arrow, or done
        if self._match(TokenType.LBRACE):
            body: Union[Block, Expr] = self._block_body()
        elif self._match(TokenType.FAT_ARROW):
            body = self._expression()
        else:
            # done-form: everything until 'done' keyword
            stmts: List[Statement] = []
            while not self._check(TokenType.DONE) and not self._is_at_end():
                while self._match(TokenType.NEWLINE):
                    pass
                if self._check(TokenType.DONE):
                    break
                stmts.append(self._declaration())
            self._consume(TokenType.DONE, "Expected 'done' to close task body")
            body = Block(statements=stmts)

        return TaskDecl(
            name=name_tok.lexeme,
            type_params=type_params,
            params=params,
            return_type=return_type,
            body=body,
            annotations=annotations,
            is_launch=is_launch,
        )

    def _shape_decl(self, is_launch: bool = False) -> ShapeDecl:
        name_tok = self._consume(TokenType.IDENT, "Expected shape name")
        type_params: List[str] = []
        if self._check(TokenType.LT):
            self._advance()
            while True:
                tp = self._consume(TokenType.IDENT, "Expected type parameter name")
                type_params.append(tp.value)
                if not self._match(TokenType.COMMA):
                    break
            self._consume(TokenType.GT, "Expected '>' after type parameters")

        self._consume(TokenType.LBRACE, "Expected '{' after shape name")
        fields: List[Param] = []
        while (
            not self._check(TokenType.RBRACE)
            and not self._check(TokenType.DONE)
            and not self._is_at_end()
        ):
            while self._match(TokenType.NEWLINE, TokenType.COMMA):
                pass
            if self._check(TokenType.RBRACE) or self._check(TokenType.DONE):
                break
            fname = self._consume(TokenType.IDENT, "Expected field name").lexeme
            self._consume(TokenType.COLON, "Expected ':' after field name")
            ftype = self._type_expr()
            fields.append(Param(name=fname, type_ann=ftype))
            # optional comma
            self._match(TokenType.COMMA)
        self._consume_block_end("Expected '}' or 'done' to close shape")

        return ShapeDecl(
            name=name_tok.lexeme,
            type_params=type_params,
            fields=fields,
            is_launch=is_launch,
        )

    def _impl_block(self) -> ImplBlock:
        # impl [Doctrine for] TypeName { methods }
        first_name = self._consume(
            TokenType.IDENT, "Expected type name after 'impl'"
        ).lexeme
        doctrine: Optional[str] = None

        if self._check(TokenType.FOR_KW):
            # impl Doctrine for Type
            self._advance()
            doctrine = first_name
            first_name = self._consume(
                TokenType.IDENT, "Expected type name after 'for'"
            ).lexeme

        self._consume(TokenType.LBRACE, "Expected '{' after impl header")
        methods: List[TaskDecl] = []
        while (
            not self._check(TokenType.RBRACE)
            and not self._check(TokenType.DONE)
            and not self._is_at_end()
        ):
            while self._match(TokenType.NEWLINE):
                pass
            if self._check(TokenType.RBRACE) or self._check(TokenType.DONE):
                break
            self._consume(TokenType.TASK, "Expected 'task' in impl block")
            methods.append(self._task_decl())
        self._consume_block_end("Expected '}' or 'done' to close impl block")

        return ImplBlock(doctrine=doctrine, target_type=first_name, methods=methods)

    def _doctrine_decl(self) -> DoctrineDecl:
        name_tok = self._consume(TokenType.IDENT, "Expected doctrine name")
        self._consume(TokenType.LBRACE, "Expected '{' after doctrine name")
        methods: List[TaskDecl] = []
        while (
            not self._check(TokenType.RBRACE)
            and not self._check(TokenType.DONE)
            and not self._is_at_end()
        ):
            while self._match(TokenType.NEWLINE):
                pass
            if self._check(TokenType.RBRACE) or self._check(TokenType.DONE):
                break
            self._consume(TokenType.TASK, "Expected 'task' in doctrine body")
            methods.append(self._task_decl())
        self._consume_block_end("Expected '}' or 'done' to close doctrine")
        return DoctrineDecl(name=name_tok.lexeme, methods=methods)

    def _check_stmt(self) -> Union[CheckMaybe, CheckResult]:
        """Parse check (maybe) or check result (result) pattern matching."""
        if self._match(TokenType.RESULT_KW):
            # check result expr { ok(x) -> ... err(e) -> ... }
            subject = self._expression()
            self._consume(TokenType.LBRACE, "Expected '{' after check result subject")

            ok_name = "x"
            ok_body = Block(statements=[])
            err_name = "e"
            err_body = Block(statements=[])

            while (
                not self._check(TokenType.RBRACE)
                and not self._check(TokenType.DONE)
                and not self._is_at_end()
            ):
                while self._match(TokenType.NEWLINE):
                    pass
                if self._check(TokenType.RBRACE) or self._check(TokenType.DONE):
                    break

                if self._match(TokenType.OK):
                    self._consume(TokenType.LPAREN, "Expected '(' after 'ok'")
                    ok_name = self._consume(
                        TokenType.IDENT, "Expected identifier in ok pattern"
                    ).lexeme
                    self._consume(TokenType.RPAREN, "Expected ')' after ok pattern")
                    self._consume(TokenType.ARROW, "Expected '->' after ok pattern")
                    if self._check(TokenType.LBRACE):
                        self._advance()
                        ok_body = self._block_body()
                    else:
                        stmt = self._declaration()
                        ok_body = Block(statements=[stmt])
                elif self._match(TokenType.ERR):
                    self._consume(TokenType.LPAREN, "Expected '(' after 'err'")
                    err_name = self._consume(
                        TokenType.IDENT, "Expected identifier in err pattern"
                    ).lexeme
                    self._consume(TokenType.RPAREN, "Expected ')' after err pattern")
                    self._consume(TokenType.ARROW, "Expected '->' after err pattern")
                    if self._check(TokenType.LBRACE):
                        self._advance()
                        err_body = self._block_body()
                    else:
                        stmt = self._declaration()
                        err_body = Block(statements=[stmt])
                else:
                    raise self._error(
                        self._peek(), "Expected 'ok' or 'err' in check result arms"
                    )

                while self._match(TokenType.NEWLINE):
                    pass

            self._consume_block_end("Expected '}' or 'done' after check result")
            return CheckResult(
                subject=subject,
                ok_name=ok_name,
                ok_body=ok_body,
                err_name=err_name,
                err_body=err_body,
            )
        else:
            # check expr { got x -> ... nobody -> ... }
            subject = self._expression()
            self._consume(TokenType.LBRACE, "Expected '{' after check subject")

            got_name = "x"
            got_body = Block(statements=[])
            nobody_body = Block(statements=[])

            while (
                not self._check(TokenType.RBRACE)
                and not self._check(TokenType.DONE)
                and not self._is_at_end()
            ):
                while self._match(TokenType.NEWLINE):
                    pass
                if self._check(TokenType.RBRACE) or self._check(TokenType.DONE):
                    break

                if self._match(TokenType.GOT):
                    got_name = self._consume(
                        TokenType.IDENT, "Expected identifier after 'got'"
                    ).lexeme
                    self._consume(TokenType.ARROW, "Expected '->' after got pattern")
                    if self._check(TokenType.LBRACE):
                        self._advance()
                        got_body = self._block_body()
                    else:
                        stmt = self._declaration()
                        got_body = Block(statements=[stmt])
                elif self._match(TokenType.NOBODY):
                    self._consume(TokenType.ARROW, "Expected '->' after nobody")
                    if self._check(TokenType.LBRACE):
                        self._advance()
                        nobody_body = self._block_body()
                    else:
                        stmt = self._declaration()
                        nobody_body = Block(statements=[stmt])
                else:
                    raise self._error(
                        self._peek(), "Expected 'got' or 'nobody' in check arms"
                    )

                while self._match(TokenType.NEWLINE):
                    pass

            self._consume_block_end("Expected '}' or 'done' after check")
            return CheckMaybe(
                subject=subject,
                got_name=got_name,
                got_body=got_body,
                nobody_body=nobody_body,
            )

    def _annotation(self) -> Annotation:
        """Parse @name, then attach to the next declaration."""
        name_tok = self._consume(TokenType.IDENT, "Expected annotation name after '@'")
        while self._match(TokenType.NEWLINE):
            pass
        # The next declaration is the target
        target = self._declaration()
        return Annotation(name=name_tok.lexeme, target=target)

    def _trust_me_block(self) -> TrustMeBlock:
        """Parse: trust me "reason" on my honor as .level { body }"""
        reason = ""
        if self._check(TokenType.STRING_LIT):
            reason = self._advance().value

        honor_level = "cadet"
        if self._match(TokenType.ON_MY_HONOR):
            # Expect .level — level can be a keyword like 'pilot'
            if self._match(TokenType.DOT):
                tok = self._advance()  # accept any token as honor level name
                honor_level = tok.lexeme if tok.lexeme else tok.value

        self._consume(TokenType.LBRACE, "Expected '{' after trust me")
        body = self._block_body()
        return TrustMeBlock(reason=reason, honor_level=honor_level, body=body)

    def _foreshadow_decl(self) -> ForeshadowDecl:
        """Parse: foreshadow pilot x = expr"""
        self._consume(TokenType.PILOT, "Expected 'pilot' after 'foreshadow'")
        decl = self._pilot_decl()
        return ForeshadowDecl(decl=decl)

    def _payoff_stmt(self) -> PayoffStmt:
        """Parse: payoff x"""
        name_tok = self._consume(
            TokenType.IDENT, "Expected variable name after 'payoff'"
        )
        return PayoffStmt(name=name_tok.lexeme)

    def _use_import(self) -> UseImport:
        """Parse: use module::{a, b} / use module::* / use module::Name as Alias"""
        module_tok = self._consume(TokenType.IDENT, "Expected module name after 'use'")
        module_name = module_tok.lexeme

        self._consume(TokenType.COLON_COLON, "Expected '::' after module name")

        # use module::*
        if self._match(TokenType.STAR):
            return UseImport(module=module_name, names=["*"])

        # use module::{a, b, c}
        if self._match(TokenType.LBRACE):
            names: List[str] = []
            while not self._check(TokenType.RBRACE) and not self._is_at_end():
                name = self._consume(TokenType.IDENT, "Expected import name")
                names.append(name.lexeme)
                if not self._match(TokenType.COMMA):
                    break
            self._consume(TokenType.RBRACE, "Expected '}' after import list")
            return UseImport(module=module_name, names=names)

        # use module::Name  or  use module::Name as Alias
        name_tok = self._consume(TokenType.IDENT, "Expected import name")
        alias = None
        if self._match(TokenType.AS):
            alias_tok = self._consume(TokenType.IDENT, "Expected alias name after 'as'")
            alias = alias_tok.lexeme
        return UseImport(module=module_name, names=[name_tok.lexeme], alias=alias)

    def _deus_ex_machina(self) -> DeusExMachina:
        """Parse: deus_ex_machina "monologue" { body }"""
        monologue = ""
        if self._check(TokenType.STRING_LIT):
            monologue = self._advance().value
        body = self._consume_block("Expected '{' after deus_ex_machina monologue")
        # Validate monologue length >= 20 words
        word_count = len(monologue.split())
        if word_count < 20:
            # Warn but don't hard-fail; the compiler voice would say it
            pass  # type checker / emitter can emit the warning
        return DeusExMachina(monologue=monologue, body=body)

    def _isekai_block(self) -> IsekaiBlock:
        """Parse: isekai { body } bringing back { name, ... }"""
        body = self._consume_block("Expected '{' after 'isekai'")
        exports: List[str] = []
        if self._match(TokenType.BRINGING_BACK):
            self._consume(TokenType.LBRACE, "Expected '{' after 'bringing back'")
            while not self._check(TokenType.RBRACE) and not self._is_at_end():
                while self._match(TokenType.NEWLINE, TokenType.COMMA):
                    pass
                if self._check(TokenType.RBRACE):
                    break
                name = self._consume(
                    TokenType.IDENT, "Expected identifier in bringing back list"
                )
                exports.append(name.lexeme)
                self._match(TokenType.COMMA)
            self._consume(TokenType.RBRACE, "Expected '}' after bringing back list")
        return IsekaiBlock(body=body, exports=exports)

    def _eventually_block(self) -> EventuallyBlock:
        """Parse: eventually { body }  or  eventually if cond { body }"""
        condition: Optional[Expr] = None
        if self._match(TokenType.IF):
            condition = self._expression()
        body = self._consume_block("Expected '{' after 'eventually'")
        return EventuallyBlock(body=body, condition=condition)

    def _launch_modified(self) -> Statement:
        """Handle 'launch task ...' or 'launch shape ...'."""
        if self._match(TokenType.TASK):
            decl = self._task_decl(is_launch=True)
            return decl
        if self._match(TokenType.SHAPE):
            decl = self._shape_decl(is_launch=True)
            return decl
        raise self._error(self._peek(), "Expected 'task' or 'shape' after 'launch'")

    def _give_back_stmt(self) -> GiveBack:
        if (
            self._check(TokenType.NEWLINE)
            or self._check(TokenType.RBRACE)
            or self._check(TokenType.DONE)
            or self._check(TokenType.EOF)
        ):
            return GiveBack(value=None)
        value_expr = self._expression()
        return GiveBack(value=value_expr)

    def _expr_or_assign_stmt(self) -> Statement:
        """Parse an expression statement or assignment."""
        expr = self._expression()

        # Check for assignment operators
        if self._match(
            TokenType.EQ,
            TokenType.PLUS_EQ,
            TokenType.MINUS_EQ,
            TokenType.STAR_EQ,
            TokenType.SLASH_EQ,
        ):
            op = self._previous().lexeme
            value = self._expression()
            return Assign(target=expr, op=op, value=value)

        return ExprStmt(expr=expr)

    # --- Block helpers -------------------------------------------------

    def _block_body(self) -> Block:
        """Parse statements until '}' or 'done'."""
        statements: List[Statement] = []
        while (
            not self._check(TokenType.RBRACE)
            and not self._check(TokenType.DONE)
            and not self._is_at_end()
        ):
            while self._match(TokenType.NEWLINE):
                pass
            if self._check(TokenType.RBRACE) or self._check(TokenType.DONE):
                break
            statements.append(self._declaration())
        self._consume_block_end("Expected '}' or 'done' to close block")
        return Block(statements=statements)

    def _consume_block(self, message: str) -> Block:
        """Expect '{' then parse block body."""
        self._consume(TokenType.LBRACE, message)
        return self._block_body()

    def _consume_block_end(self, message: str) -> None:
        """Accept '}' or 'done' to close a block."""
        if self._match(TokenType.RBRACE):
            return
        if self._match(TokenType.DONE):
            return
        raise self._error(self._peek(), message)

    # --- Expressions with precedence ----------------------------------

    def _expression(self) -> Expr:
        return self._pipe()

    def _pipe(self) -> Expr:
        """Pipe operator |> (lowest precedence)."""
        expr = self._or_else()
        while self._match(TokenType.PIPE):
            right = self._or_else()
            expr = BinOp(op="|>", left=expr, right=right)
        return expr

    def _or_else(self) -> Expr:
        """or else operator — fallback for maybe/result."""
        expr = self._or()
        while self._match(TokenType.OR_ELSE):
            right = self._or()
            expr = BinOp(op="or else", left=expr, right=right)
        return expr

    def _or(self) -> Expr:
        expr = self._and()
        while self._match(TokenType.OR):
            op_token = self._previous()
            right = self._and()
            expr = BinOp(op=op_token.lexeme, left=expr, right=right)
        return expr

    def _and(self) -> Expr:
        expr = self._equality()
        while self._match(TokenType.AND):
            op_token = self._previous()
            right = self._equality()
            expr = BinOp(op=op_token.lexeme, left=expr, right=right)
        return expr

    def _equality(self) -> Expr:
        expr = self._comparison()
        while self._match(TokenType.EQ_EQ, TokenType.BANG_EQ):
            op_token = self._previous()
            right = self._comparison()
            expr = BinOp(op=op_token.lexeme, left=expr, right=right)
        return expr

    def _comparison(self) -> Expr:
        expr = self._term()
        while self._match(TokenType.LT, TokenType.LT_EQ, TokenType.GT, TokenType.GT_EQ):
            op_token = self._previous()
            right = self._term()
            expr = BinOp(op=op_token.lexeme, left=expr, right=right)
        return expr

    def _term(self) -> Expr:
        expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS, TokenType.NAKAMA):
            op_token = self._previous()
            right = self._factor()
            expr = BinOp(op=op_token.lexeme, left=expr, right=right)
        return expr

    def _factor(self) -> Expr:
        expr = self._power()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_token = self._previous()
            right = self._power()
            expr = BinOp(op=op_token.lexeme, left=expr, right=right)
        return expr

    def _power(self) -> Expr:
        expr = self._unary()
        if self._match(TokenType.STAR_STAR):
            right = self._unary()
            expr = BinOp(op="**", left=expr, right=right)
        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.MINUS, TokenType.NOT, TokenType.BANG):
            op_token = self._previous()
            operand = self._unary()
            return UnaryOp(op=op_token.lexeme, operand=operand)
        if self._match(TokenType.FINAL_FORM):
            operand = self._unary()
            return UnaryOp(op="FINAL FORM", operand=operand)
        if self._match(TokenType.PLUS_ULTRA):
            operand = self._unary()
            return UnaryOp(op="PLUS ULTRA", operand=operand)
        return self._postfix()

    def _postfix(self) -> Expr:
        """Handle call (args), field .name, method .name(args), index [expr]."""
        expr = self._primary()

        while True:
            if self._match(TokenType.LPAREN):
                # Function call
                args: List[Expr] = []
                if not self._check(TokenType.RPAREN):
                    while True:
                        args.append(self._expression())
                        if not self._match(TokenType.COMMA):
                            break
                self._consume(TokenType.RPAREN, "Expected ')' after arguments")
                expr = Call(func=expr, args=args)
            elif self._match(TokenType.DOT):
                # Field access or method call
                name_tok = self._consume(
                    TokenType.IDENT, "Expected field/method name after '.'"
                )
                if self._match(TokenType.LPAREN):
                    # Method call
                    args = []
                    if not self._check(TokenType.RPAREN):
                        while True:
                            args.append(self._expression())
                            if not self._match(TokenType.COMMA):
                                break
                    self._consume(
                        TokenType.RPAREN, "Expected ')' after method arguments"
                    )
                    expr = MethodCall(obj=expr, method=name_tok.lexeme, args=args)
                else:
                    expr = FieldAccess(obj=expr, field=name_tok.lexeme)
            elif self._match(TokenType.LBRACKET):
                # Index access
                idx = self._expression()
                self._consume(TokenType.RBRACKET, "Expected ']' after index")
                expr = Index(obj=expr, index=idx)
            elif self._match(TokenType.QUESTION):
                # ? error propagation (postfix)
                expr = UnaryOp(op="?", operand=expr)
            elif self._match(TokenType.TSUNDERE):
                # x TSUNDERE → !(x) for bool, -x for num
                expr = UnaryOp(op="TSUNDERE", operand=expr)
            else:
                break

        return expr

    def _primary(self) -> Expr:
        tok = self._peek()

        # Lambda: |params| => expr  or  |params| { block }
        # Also handle capture modes: copy |...|, move |...|, mut |...|
        if tok.type == TokenType.PIPE_SINGLE:
            return self._lambda("borrow")
        if tok.type in (TokenType.COPY, TokenType.MOVE, TokenType.MUT):
            self._advance()
            capture = self._previous().lexeme
            return self._lambda(capture)

        tok = self._advance()

        if tok.type == TokenType.INT_LIT:
            return IntLit(tok.value)
        if tok.type == TokenType.FLOAT_LIT:
            return FloatLit(tok.value)
        if tok.type == TokenType.STRING_LIT:
            return self._parse_string_lit(tok)
        if tok.type == TokenType.BOOL_LIT:
            return BoolLit(tok.value)
        if tok.type == TokenType.NOBODY:
            return Nobody()

        # some(x), ok(x), err(x)
        if tok.type == TokenType.SOME:
            self._consume(TokenType.LPAREN, "Expected '(' after 'some'")
            val = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after some value")
            return SomeExpr(value=val)
        if tok.type == TokenType.OK:
            self._consume(TokenType.LPAREN, "Expected '(' after 'ok'")
            val = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after ok value")
            return OkExpr(value=val)
        if tok.type == TokenType.ERR:
            self._consume(TokenType.LPAREN, "Expected '(' after 'err'")
            val = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after err value")
            return ErrExpr(value=val)

        if tok.type == TokenType.IDENT:
            # Support namespace paths: module::symbol::name
            parts = [tok.value]
            while self._match(TokenType.COLON_COLON):
                next_part = self._consume(
                    TokenType.IDENT, "Expected identifier after '::'"
                )
                parts.append(next_part.value)

            # Check for shape instantiation only on single identifiers
            if (
                len(parts) == 1
                and self._check(TokenType.LBRACE)
                and parts[0][0:1].isupper()
            ):
                return self._shape_instantiation(parts[0])

            if len(parts) == 1:
                return Ident(parts[0])
            return PathIdent(parts=parts)

        if tok.type == TokenType.LPAREN:
            first = self._expression()
            if self._match(TokenType.COMMA):
                # Tuple literal
                elements: List[Expr] = [first]
                while True:
                    elements.append(self._expression())
                    if not self._match(TokenType.COMMA):
                        break
                self._consume(TokenType.RPAREN, "Expected ')' after tuple literal")
                return TupleLit(elements=elements)
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return first

        if tok.type == TokenType.LBRACKET:
            elements = []
            if not self._check(TokenType.RBRACKET):
                while True:
                    elements.append(self._expression())
                    if not self._match(TokenType.COMMA):
                        break
            self._consume(TokenType.RBRACKET, "Expected ']' after list literal")
            return ListLit(elements=elements)

        if tok.type == TokenType.LBRACE:
            # Map literal: { key: value, ... }
            pairs: List[Tuple[Expr, Expr]] = []
            if not self._check(TokenType.RBRACE):
                while True:
                    while self._match(TokenType.NEWLINE):
                        pass
                    if self._check(TokenType.RBRACE):
                        break
                    key = self._expression()
                    self._consume(TokenType.COLON, "Expected ':' in map literal")
                    value = self._expression()
                    pairs.append((key, value))
                    if not self._match(TokenType.COMMA):
                        break
                    while self._match(TokenType.NEWLINE):
                        pass
            self._consume(TokenType.RBRACE, "Expected '}' after map literal")
            return MapLit(pairs=pairs)

        raise self._error(tok, "Expected expression")

    def _lambda(self, capture_mode: str) -> Lambda:
        """Parse |params| => expr  or  |params| { block }."""
        self._consume(TokenType.PIPE_SINGLE, "Expected '|' to start lambda parameters")
        params: List[Param] = []
        if not self._check(TokenType.PIPE_SINGLE):
            while True:
                pname = self._consume(TokenType.IDENT, "Expected parameter name").lexeme
                ptype: Optional[TypeExpr] = None
                if self._match(TokenType.COLON):
                    ptype = self._type_expr()
                params.append(Param(name=pname, type_ann=ptype))
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.PIPE_SINGLE, "Expected '|' after lambda parameters")

        if self._match(TokenType.FAT_ARROW):
            body: Union[Block, Expr] = self._expression()
        elif self._match(TokenType.LBRACE):
            body = self._block_body()
        else:
            raise self._error(self._peek(), "Expected '=>' or '{' after lambda params")

        return Lambda(params=params, body=body, capture_mode=capture_mode)

    def _shape_instantiation(self, name: str) -> ShapeInstantiation:
        """Parse Name { field: val, ... }."""
        self._consume(TokenType.LBRACE, "Expected '{' in shape instantiation")
        fields: List[Tuple[str, Expr]] = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            while self._match(TokenType.NEWLINE, TokenType.COMMA):
                pass
            if self._check(TokenType.RBRACE):
                break
            fname = self._consume(TokenType.IDENT, "Expected field name").lexeme
            self._consume(
                TokenType.COLON, "Expected ':' after field name in shape instantiation"
            )
            fval = self._expression()
            fields.append((fname, fval))
            self._match(TokenType.COMMA)
        self._consume(TokenType.RBRACE, "Expected '}' after shape instantiation")
        return ShapeInstantiation(shape_name=name, fields=fields)

    def _parse_string_lit(self, tok: Token) -> StrLit:
        """Parse a string literal, extracting {expr} interpolation parts."""
        raw = tok.value
        if "{" not in raw:
            return StrLit(value=raw)

        # Parse interpolation: split on {identifier} patterns
        parts: List[Tuple[str, Optional[Expr]]] = []
        i = 0
        text_acc = ""
        while i < len(raw):
            if raw[i] == "{":
                # Find closing }
                j = raw.index("}", i + 1) if "}" in raw[i + 1 :] else -1
                if j == -1:
                    text_acc += raw[i]
                    i += 1
                    continue
                j = raw.index("}", i + 1)
                interp_content = raw[i + 1 : j]
                # Parse dotted identifiers: p.x → FieldAccess(Ident("p"), "x")
                dot_parts = interp_content.split(".")
                interp_expr: Expr = Ident(name=dot_parts[0])
                for field_name in dot_parts[1:]:
                    interp_expr = FieldAccess(obj=interp_expr, field=field_name)
                parts.append((text_acc, interp_expr))
                text_acc = ""
                i = j + 1
            else:
                text_acc += raw[i]
                i += 1

        if text_acc:
            parts.append((text_acc, None))

        return StrLit(value=raw, parts=parts)

    # --- Type expressions ----------------------------------------------

    def _type_expr(self) -> TypeExpr:
        # Handle pointer types: *T, *mut T
        if self._match(TokenType.STAR):
            if self._match(TokenType.MUT):
                inner = self._type_expr()
                return TypeExpr(
                    name=inner.name,
                    params=inner.params,
                    is_pointer=True,
                    is_mut_pointer=True,
                )
            inner = self._type_expr()
            return TypeExpr(name=inner.name, params=inner.params, is_pointer=True)

        ident = self._consume(TokenType.IDENT, "Expected type name")
        type_params: List[TypeExpr] = []

        # Generic params: Type<A, B>
        if self._check(TokenType.LT):
            self._advance()
            while True:
                type_params.append(self._type_expr())
                if not self._match(TokenType.COMMA):
                    break
            self._consume(TokenType.GT, "Expected '>' after type parameters")

        return TypeExpr(name=ident.value, params=type_params)

    # --- Helpers -------------------------------------------------------

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _consume(self, type_: TokenType, message: str) -> Token:
        if self._check(type_):
            return self._advance()
        raise self._error(self._peek(), message)

    def _check(self, type_: TokenType) -> bool:
        return self._peek().type == type_

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _error(self, token: Token, message: str) -> ParseError:
        where = f"line {token.line}, col {token.column}"
        return ParseError(f"[{where}] {message} (found {token.type} {token.lexeme!r})")


__all__ = [
    "Program",
    "PilotDecl",
    "SayStmt",
    "Param",
    "Block",
    "TaskDecl",
    "ShapeDecl",
    "ImplBlock",
    "DoctrineDecl",
    "GiveBack",
    "Assign",
    "ExprStmt",
    "IntLit",
    "FloatLit",
    "StrLit",
    "BoolLit",
    "Ident",
    "PathIdent",
    "Nobody",
    "SomeExpr",
    "OkExpr",
    "ErrExpr",
    "BinOp",
    "UnaryOp",
    "Call",
    "MethodCall",
    "FieldAccess",
    "Index",
    "Lambda",
    "IfExpr",
    "WhenArm",
    "WhenExpr",
    "ForEach",
    "RepeatTimes",
    "RepeatUntil",
    "TrainingArc",
    "ListLit",
    "MapLit",
    "TupleLit",
    "ShapeInstantiation",
    "TypeExpr",
    "DeusExMachina",
    "IsekaiBlock",
    "EventuallyBlock",
    "Parser",
    "ParseError",
]
