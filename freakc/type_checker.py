"""
FREAK Lite — Basic Type Checker

Performs static analysis on the AST before emission:
  - Symbol table with lexical scoping
  - Type inference for literals and expressions
  - Variable declared-before-use checks
  - Function call arity validation
  - Return type consistency within tasks
  - Friendly error messages with line numbers
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .parser import (
    Annotation,
    Assign,
    BinOp,
    Block,
    BoolLit,
    Call,
    CheckMaybe,
    CheckResult,
    DeusExMachina,
    DoctrineDecl,
    ErrExpr,
    EventuallyBlock,
    ExprStmt,
    FieldAccess,
    FloatLit,
    ForEach,
    ForeshadowDecl,
    GiveBack,
    Ident,
    IfExpr,
    ImplBlock,
    Index,
    IntLit,
    IsekaiBlock,
    Lambda,
    ListLit,
    MapLit,
    MethodCall,
    Nobody,
    OkExpr,
    Param,
    PathIdent,
    PayoffStmt,
    PilotDecl,
    Program,
    RepeatTimes,
    RepeatUntil,
    SayStmt,
    ShapeDecl,
    ShapeInstantiation,
    SomeExpr,
    StrLit,
    TaskDecl,
    TrainingArc,
    TrustMeBlock,
    TupleLit,
    TypeExpr,
    UnaryOp,
    UseImport,
    WhenExpr,
)

# ===================================================================
#  Types
# ===================================================================


@dataclass
class FreakType:
    """Represents a resolved FREAK type."""

    name: str  # "int", "num", "word", "bool", "void", shape name, etc.
    params: List["FreakType"] = field(default_factory=list)  # generic params
    is_pointer: bool = False

    def __eq__(self, other):
        if not isinstance(other, FreakType):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        if self.params:
            p = ", ".join(str(p) for p in self.params)
            return f"{self.name}<{p}>"
        return self.name


# Common types
T_INT = FreakType("int")
T_NUM = FreakType("num")
T_WORD = FreakType("word")
T_BOOL = FreakType("bool")
T_VOID = FreakType("void")
T_UNKNOWN = FreakType("unknown")


# ===================================================================
#  Symbol Table
# ===================================================================


@dataclass
class Symbol:
    name: str
    type: FreakType
    is_mutable: bool = True


@dataclass
class FuncSignature:
    name: str
    params: List[Tuple[str, FreakType]]  # (name, type)
    return_type: FreakType
    is_method: bool = False


class Scope:
    def __init__(self, parent: Optional["Scope"] = None) -> None:
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}

    def define(self, name: str, sym: Symbol) -> None:
        self.symbols[name] = sym

    def lookup(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None


# ===================================================================
#  Diagnostics
# ===================================================================


@dataclass
class Diagnostic:
    level: str  # "error", "warning"
    message: str
    line: Optional[int] = None
    column: Optional[int] = None

    def __str__(self):
        loc = ""
        if self.line is not None:
            loc = f"[line {self.line}] "
        return f"{self.level}: {loc}{self.message}"


# ===================================================================
#  Type Checker
# ===================================================================


class TypeChecker:
    """
    Walk the AST and collect type errors/warnings.

    Usage:
        checker = TypeChecker()
        diagnostics = checker.check(program)
        for d in diagnostics:
            print(d)
    """

    def __init__(self) -> None:
        self.scope: Scope = Scope()
        self.functions: Dict[str, FuncSignature] = {}
        self.shapes: Dict[str, ShapeDecl] = {}
        self.diagnostics: List[Diagnostic] = []
        self._current_return_type: Optional[FreakType] = None

    def check(self, program: Program) -> List[Diagnostic]:
        self.scope = Scope()
        self.functions = {}
        self.shapes = {}
        self.diagnostics = []
        self._current_return_type = None

        # Pre-register built-in functions
        self.functions["panic"] = FuncSignature("panic", [("msg", T_WORD)], T_VOID)
        self.functions["ask"] = FuncSignature("ask", [("prompt", T_WORD)], T_WORD)

        # First pass: register all functions and shapes
        for stmt in program.statements:
            if isinstance(stmt, TaskDecl):
                self._register_task(stmt)
            elif isinstance(stmt, ShapeDecl):
                self.shapes[stmt.name] = stmt
            elif isinstance(stmt, ImplBlock):
                for m in stmt.methods:
                    self._register_method(stmt.target_type, m)
            elif isinstance(stmt, Annotation) and stmt.target:
                # Also register tasks/shapes inside annotations
                if isinstance(stmt.target, TaskDecl):
                    self._register_task(stmt.target)
                elif isinstance(stmt.target, ShapeDecl):
                    self.shapes[stmt.target.name] = stmt.target

        # Second pass: check all statements
        for stmt in program.statements:
            self._check_statement(stmt)

        return self.diagnostics

    # --- Registration (first pass) ---

    def _register_task(self, td: TaskDecl) -> None:
        params = []
        for p in td.params:
            pt = self._resolve_type_expr(p.type_ann) if p.type_ann else T_UNKNOWN
            params.append((p.name, pt))
        ret = self._resolve_type_expr(td.return_type) if td.return_type else T_VOID
        self.functions[td.name] = FuncSignature(td.name, params, ret)

    def _register_method(self, type_name: str, td: TaskDecl) -> None:
        key = f"{type_name}.{td.name}"
        params = []
        for p in td.params:
            if p.name == "self":
                params.append(("self", FreakType(type_name, is_pointer=True)))
            else:
                pt = self._resolve_type_expr(p.type_ann) if p.type_ann else T_UNKNOWN
                params.append((p.name, pt))
        ret = self._resolve_type_expr(td.return_type) if td.return_type else T_VOID
        self.functions[key] = FuncSignature(td.name, params, ret, is_method=True)

    # --- Statement checking ---

    def _check_statement(self, stmt) -> None:
        if isinstance(stmt, PilotDecl):
            self._check_pilot_decl(stmt)
        elif isinstance(stmt, SayStmt):
            self._check_expr(stmt.value)
        elif isinstance(stmt, TaskDecl):
            self._check_task_decl(stmt)
        elif isinstance(stmt, GiveBack):
            self._check_give_back(stmt)
        elif isinstance(stmt, IfExpr):
            self._check_if(stmt)
        elif isinstance(stmt, WhenExpr):
            self._check_when(stmt)
        elif isinstance(stmt, ForEach):
            self._check_for_each(stmt)
        elif isinstance(stmt, (RepeatTimes, RepeatUntil)):
            self._check_repeat(stmt)
        elif isinstance(stmt, TrainingArc):
            self._check_training_arc(stmt)
        elif isinstance(stmt, Assign):
            self._check_assign(stmt)
        elif isinstance(stmt, ExprStmt):
            self._check_expr(stmt.expr)
        elif isinstance(stmt, CheckMaybe):
            self._check_check_maybe(stmt)
        elif isinstance(stmt, CheckResult):
            self._check_check_result(stmt)
        elif isinstance(stmt, Annotation):
            if stmt.target:
                self._check_statement(stmt.target)
        elif isinstance(stmt, TrustMeBlock):
            self._check_block(stmt.body)
        elif isinstance(stmt, ForeshadowDecl):
            self._check_pilot_decl(stmt.decl)
        elif isinstance(stmt, PayoffStmt):
            sym = self.scope.lookup(stmt.name)
            if sym is None:
                self._warn(f"payoff for undeclared variable '{stmt.name}'")
        elif isinstance(stmt, (ShapeDecl, ImplBlock, DoctrineDecl, UseImport)):
            pass  # already handled in first pass or at emit time
        elif isinstance(stmt, DeusExMachina):
            self._check_deus_ex_machina(stmt)
        elif isinstance(stmt, IsekaiBlock):
            self._check_isekai(stmt)
        elif isinstance(stmt, EventuallyBlock):
            self._check_eventually(stmt)

    def _check_pilot_decl(self, decl: PilotDecl) -> None:
        inferred = self._check_expr(decl.value)
        declared = self._resolve_type_expr(decl.type_ann) if decl.type_ann else inferred

        # Check type consistency if both are known
        if decl.type_ann and inferred != T_UNKNOWN and declared != T_UNKNOWN:
            if inferred != declared:
                self._warn(
                    f"Variable '{decl.name}' declared as {declared} but initialized with {inferred}"
                )

        self.scope.define(
            decl.name, Symbol(decl.name, declared if decl.type_ann else inferred)
        )

    def _check_task_decl(self, td: TaskDecl) -> None:
        saved_scope = self.scope
        self.scope = Scope(parent=saved_scope)

        # Define parameters
        for p in td.params:
            pt = self._resolve_type_expr(p.type_ann) if p.type_ann else T_UNKNOWN
            self.scope.define(p.name, Symbol(p.name, pt))

        # Set expected return type
        saved_ret = self._current_return_type
        sig = self.functions.get(td.name)
        self._current_return_type = sig.return_type if sig else T_VOID

        if isinstance(td.body, Block):
            self._check_block(td.body)
        else:
            self._check_expr(td.body)

        self._current_return_type = saved_ret
        self.scope = saved_scope

    def _check_give_back(self, stmt: GiveBack) -> None:
        if stmt.value is None:
            if self._current_return_type and self._current_return_type != T_VOID:
                self._warn(
                    f"'give back' without value in task that returns {self._current_return_type}"
                )
        else:
            actual = self._check_expr(stmt.value)
            if (
                self._current_return_type
                and actual != T_UNKNOWN
                and self._current_return_type != T_VOID
                and actual != self._current_return_type
            ):
                self._warn(
                    f"'give back' type {actual} doesn't match expected {self._current_return_type}"
                )

    def _check_if(self, stmt: IfExpr) -> None:
        cond_type = self._check_expr(stmt.condition)
        if cond_type != T_UNKNOWN and cond_type != T_BOOL and cond_type != T_INT:
            self._warn(f"if condition has type {cond_type}, expected bool")
        self._check_block(stmt.then_block)
        for cond, blk in stmt.elif_branches:
            self._check_expr(cond)
            self._check_block(blk)
        if stmt.else_block:
            self._check_block(stmt.else_block)

    def _check_when(self, stmt: WhenExpr) -> None:
        self._check_expr(stmt.subject)
        for arm in stmt.arms:
            if isinstance(arm.pattern, str) and arm.pattern == "_":
                pass
            else:
                self._check_expr(arm.pattern)
            if isinstance(arm.body, Block):
                self._check_block(arm.body)
            else:
                self._check_expr(arm.body)

    def _check_for_each(self, stmt: ForEach) -> None:
        self._check_expr(stmt.iterable)
        saved = self.scope
        self.scope = Scope(parent=saved)
        if isinstance(stmt.pattern, Ident):
            self.scope.define(stmt.pattern.name, Symbol(stmt.pattern.name, T_UNKNOWN))
        self._check_block(stmt.body)
        self.scope = saved

    def _check_repeat(self, stmt) -> None:
        if isinstance(stmt, RepeatTimes):
            self._check_expr(stmt.count)
        else:
            self._check_expr(stmt.condition)
        self._check_block(stmt.body)

    def _check_training_arc(self, stmt: TrainingArc) -> None:
        self._check_expr(stmt.condition)
        self._check_expr(stmt.max_sessions)
        self._check_block(stmt.body)

    def _check_assign(self, stmt: Assign) -> None:
        lhs_type = self._check_expr(stmt.target)
        rhs_type = self._check_expr(stmt.value)
        # Check assignability
        if isinstance(stmt.target, Ident):
            sym = self.scope.lookup(stmt.target.name)
            if sym is None:
                self._error(f"Undeclared variable '{stmt.target.name}' in assignment")

    def _check_check_maybe(self, stmt: CheckMaybe) -> None:
        self._check_expr(stmt.subject)
        saved = self.scope
        self.scope = Scope(parent=saved)
        self.scope.define(stmt.got_name, Symbol(stmt.got_name, T_UNKNOWN))
        self._check_block(stmt.got_body)
        self.scope = saved
        saved = self.scope
        self.scope = Scope(parent=saved)
        self._check_block(stmt.nobody_body)
        self.scope = saved

    def _check_check_result(self, stmt: CheckResult) -> None:
        self._check_expr(stmt.subject)
        saved = self.scope
        self.scope = Scope(parent=saved)
        self.scope.define(stmt.ok_name, Symbol(stmt.ok_name, T_UNKNOWN))
        self._check_block(stmt.ok_body)
        self.scope = saved
        saved = self.scope
        self.scope = Scope(parent=saved)
        self.scope.define(stmt.err_name, Symbol(stmt.err_name, T_WORD))
        self._check_block(stmt.err_body)
        self.scope = saved

    def _check_block(self, block: Block) -> None:
        for s in block.statements:
            self._check_statement(s)

    def _check_deus_ex_machina(self, stmt: DeusExMachina) -> None:
        """Validate deus_ex_machina: monologue must be >= 20 words."""
        word_count = len(stmt.monologue.split())
        if word_count < 20:
            self._error(
                f"deus_ex_machina monologue is only {word_count} word(s). "
                f"It must be at least 20 words. "
                f'(Yuuko voice: "That wasn\'t a speech. That was a sentence.")'
            )
        self._check_block(stmt.body)

    def _check_isekai(self, stmt: IsekaiBlock) -> None:
        """isekai block runs in complete isolation — fresh scope."""
        saved = self.scope
        from .type_checker import Scope

        self.scope = Scope()  # brand new scope — no access to outer vars
        self._check_block(stmt.body)
        # After isekai, exported names become available in outer scope
        for name in stmt.exports:
            sym = self.scope.lookup(name)
            if sym is None:
                self._warn(f"isekai exports '{name}' but it was never declared inside")
            else:
                saved.define(name, sym)
        self.scope = saved

    def _check_eventually(self, stmt: EventuallyBlock) -> None:
        """eventually block: check condition (if any) and body."""
        if stmt.condition is not None:
            self._check_expr(stmt.condition)
        self._check_block(stmt.body)

    # --- Expression checking (returns inferred type) ---

    def _check_expr(self, expr) -> FreakType:
        if isinstance(expr, IntLit):
            return T_INT
        if isinstance(expr, FloatLit):
            return T_NUM
        if isinstance(expr, BoolLit):
            return T_BOOL
        if isinstance(expr, StrLit):
            # Check interpolation references
            if expr.parts:
                for _, interp in expr.parts:
                    if interp:
                        self._check_expr(interp)
            return T_WORD
        if isinstance(expr, Nobody):
            return T_UNKNOWN
        if isinstance(expr, Ident):
            sym = self.scope.lookup(expr.name)
            if sym is None:
                self._error(f"Undeclared variable '{expr.name}'")
                return T_UNKNOWN
            return sym.type
        if isinstance(expr, PathIdent):
            # Namespaced symbol (e.g., process::pid)
            # Treat as callable symbol reference; declaration may come from stdlib/imports.
            return T_UNKNOWN
        if isinstance(expr, BinOp):
            lt = self._check_expr(expr.left)
            rt = self._check_expr(expr.right)
            if expr.op in ("==", "!=", "<", ">", "<=", ">=", "and", "or"):
                return T_BOOL
            if lt == T_NUM or rt == T_NUM:
                return T_NUM
            if lt == T_WORD and rt == T_WORD and expr.op == "+":
                return T_WORD
            return lt if lt != T_UNKNOWN else rt
        if isinstance(expr, UnaryOp):
            inner = self._check_expr(expr.operand)
            if expr.op in ("not", "!"):
                return T_BOOL
            return inner
        if isinstance(expr, Call):
            return self._check_call(expr)
        if isinstance(expr, MethodCall):
            self._check_expr(expr.obj)
            for a in expr.args:
                self._check_expr(a)
            return T_UNKNOWN
        if isinstance(expr, FieldAccess):
            self._check_expr(expr.obj)
            return T_UNKNOWN
        if isinstance(expr, Index):
            self._check_expr(expr.obj)
            self._check_expr(expr.index)
            return T_UNKNOWN
        if isinstance(expr, ListLit):
            for e in expr.elements:
                self._check_expr(e)
            return T_UNKNOWN
        if isinstance(expr, MapLit):
            for k, v in expr.pairs:
                self._check_expr(k)
                self._check_expr(v)
            return T_UNKNOWN
        if isinstance(expr, TupleLit):
            for e in expr.elements:
                self._check_expr(e)
            return T_UNKNOWN
        if isinstance(expr, ShapeInstantiation):
            if expr.shape_name not in self.shapes:
                self._error(f"Unknown shape '{expr.shape_name}'")
            for _, fval in expr.fields:
                self._check_expr(fval)
            return FreakType(expr.shape_name)
        if isinstance(expr, SomeExpr):
            self._check_expr(expr.value)
            return T_UNKNOWN
        if isinstance(expr, (OkExpr, ErrExpr)):
            self._check_expr(expr.value)
            return T_UNKNOWN
        if isinstance(expr, Lambda):
            # Check lambda body in a new scope
            saved = self.scope
            self.scope = Scope(parent=saved)
            for p in expr.params:
                pt = self._resolve_type_expr(p.type_ann) if p.type_ann else T_UNKNOWN
                self.scope.define(p.name, Symbol(p.name, pt))
            if isinstance(expr.body, Block):
                self._check_block(expr.body)
            else:
                self._check_expr(expr.body)
            self.scope = saved
            return T_UNKNOWN
        return T_UNKNOWN

    def _check_call(self, call: Call) -> FreakType:
        # Check arguments
        for a in call.args:
            self._check_expr(a)

        if isinstance(call.func, Ident):
            sig = self.functions.get(call.func.name)
            if sig:
                # Check arity
                expected_arity = len(sig.params)
                actual_arity = len(call.args)
                if expected_arity != actual_arity:
                    self._error(
                        f"Function '{call.func.name}' expects {expected_arity} "
                        f"argument(s), got {actual_arity}"
                    )
                return sig.return_type
            else:
                # Unknown function — might be a builtin or imported
                return T_UNKNOWN

        if isinstance(call.func, PathIdent):
            fq_name = "::".join(call.func.parts)

            # std::process built-ins
            process_builtins: Dict[str, Tuple[int, FreakType]] = {
                "process::run": (2, T_UNKNOWN),
                "process::spawn": (2, T_UNKNOWN),
                "process::pid": (0, T_INT),
                "process::exit": (1, T_VOID),
                "process::env_var": (1, T_UNKNOWN),
                "process::set_env": (2, T_VOID),
                "process::args": (0, T_UNKNOWN),
            }

            # std::thread built-ins
            thread_builtins: Dict[str, Tuple[int, FreakType]] = {
                "thread::spawn": (1, T_UNKNOWN),
                "thread::current_id": (0, T_INT),
                "thread::yield_now": (0, T_VOID),
                "thread::available_parallelism": (0, T_INT),
            }

            # std::bytes built-ins (constructor-style static calls)
            bytes_builtins: Dict[str, Tuple[int, FreakType]] = {
                "ByteBuffer::new": (0, T_UNKNOWN),
                "ByteBuffer::from": (1, T_UNKNOWN),
            }

            all_builtins: Dict[str, Tuple[int, FreakType]] = {}
            all_builtins.update(process_builtins)
            all_builtins.update(thread_builtins)
            all_builtins.update(bytes_builtins)

            if fq_name in all_builtins:
                expected_arity, ret_type = all_builtins[fq_name]
                actual_arity = len(call.args)
                if expected_arity != actual_arity:
                    self._error(
                        f"Function '{fq_name}' expects {expected_arity} "
                        f"argument(s), got {actual_arity}"
                    )
                return ret_type

            return T_UNKNOWN

        return T_UNKNOWN

    # --- Type resolution ---

    def _resolve_type_expr(self, te: Optional[TypeExpr]) -> FreakType:
        if te is None:
            return T_UNKNOWN
        mapping = {
            "int": T_INT,
            "uint": T_INT,
            "num": T_NUM,
            "float": T_NUM,
            "float32": T_NUM,
            "word": T_WORD,
            "bool": T_BOOL,
            "void": T_VOID,
        }
        if te.name in mapping:
            return mapping[te.name]
        if te.name in self.shapes:
            return FreakType(te.name)
        return FreakType(te.name)

    # --- Diagnostics ---

    def _error(self, msg: str, line: Optional[int] = None) -> None:
        self.diagnostics.append(Diagnostic("error", msg, line=line))

    def _warn(self, msg: str, line: Optional[int] = None) -> None:
        self.diagnostics.append(Diagnostic("warning", msg, line=line))


__all__ = ["TypeChecker", "Diagnostic", "FreakType"]
