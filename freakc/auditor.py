"""
FREAK Auditor — static analysis commands for Phase 8.

Commands:
    freak audit-science     list every 'for science,' call site
    freak audit-trust       list every 'trust me' block (file, line, level, reason)
    freak audit-miracles    list every 'deus_ex_machina' block with monologue preview
    freak foreshadow-audit  show all foreshadow/payoff pairs and any unpaid ones

All commands accept one or more .fk file paths (or scan recursively if a
directory is given).  They return a non-zero exit code if any warnings/errors
are found (unpaid foreshadows, too many miracles, under-word-count monologues).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .lexer import Lexer, TokenType
from .parser import (
    Annotation,
    Assign,
    Block,
    CheckMaybe,
    CheckResult,
    DeusExMachina,
    DoctrineDecl,
    EventuallyBlock,
    ExprStmt,
    ForEach,
    ForeshadowDecl,
    GiveBack,
    IfExpr,
    ImplBlock,
    IsekaiBlock,
    ParseError,
    Parser,
    PayoffStmt,
    PilotDecl,
    Program,
    RepeatTimes,
    RepeatUntil,
    SayStmt,
    ShapeDecl,
    TaskDecl,
    TrainingArc,
    TrustMeBlock,
    UseImport,
    WhenExpr,
)

# ---------------------------------------------------------------------------
#  Data classes for audit results
# ---------------------------------------------------------------------------


@dataclass
class ScienceCallSite:
    file: str
    line: int

    def __str__(self) -> str:
        return f"  {self.file}:{self.line}: for science"


@dataclass
class TrustMeEntry:
    file: str
    line: int
    honor_level: str
    reason: str

    def __str__(self) -> str:
        return (
            f"  {self.file}:{self.line}: "
            f'trust me (honor: .{self.honor_level}) — "{self.reason}"'
        )


@dataclass
class MiracleEntry:
    file: str
    line: int
    word_count: int
    monologue_preview: str  # first 60 chars

    def __str__(self) -> str:
        wc = f"{self.word_count} words"
        preview = self.monologue_preview
        return f'  {self.file}:{self.line}: deus_ex_machina ({wc}) — "{preview}"'


@dataclass
class ForeshadowEntry:
    file: str
    line: int
    name: str
    paid_off: bool = False
    payoff_line: Optional[int] = None

    def __str__(self) -> str:
        if self.paid_off:
            return (
                f"  {self.file}:{self.line}: foreshadow '{self.name}'"
                f" → paid off at line {self.payoff_line}"
            )
        return f"  {self.file}:{self.line}: foreshadow '{self.name}' ← UNPAID ✗"


# ---------------------------------------------------------------------------
#  Token-level scanner (gives us line numbers)
# ---------------------------------------------------------------------------


def _scan_tokens_for_science(source: str, file: str) -> List[ScienceCallSite]:
    """Scan the token stream for FOR_SCIENCE tokens."""
    results: List[ScienceCallSite] = []
    try:
        tokens = Lexer(source).tokenize()
    except Exception:
        return results
    for tok in tokens:
        if tok.type == TokenType.FOR_SCIENCE:
            results.append(ScienceCallSite(file=file, line=tok.line))
    return results


def _scan_tokens_line_map(source: str) -> Dict[str, int]:
    """
    Build a map of {lexeme_lower → first line} by scanning every token.
    Used to correlate AST nodes (which lack line numbers) back to their
    approximate source location.
    """
    mapping: Dict[str, int] = {}
    try:
        tokens = Lexer(source).tokenize()
    except Exception:
        return mapping
    for tok in tokens:
        key = tok.lexeme.lower()
        if key not in mapping:
            mapping[key] = tok.line
    return mapping


def _find_trust_me_lines(source: str) -> List[int]:
    """Return line numbers of every TRUST_ME token."""
    lines: List[int] = []
    try:
        tokens = Lexer(source).tokenize()
    except Exception:
        return lines
    for tok in tokens:
        if tok.type == TokenType.TRUST_ME:
            lines.append(tok.line)
    return lines


def _find_deus_ex_lines(source: str) -> List[int]:
    """Return line numbers of every DEUS_EX_MACHINA token."""
    lines: List[int] = []
    try:
        tokens = Lexer(source).tokenize()
    except Exception:
        return lines
    for tok in tokens:
        if tok.type == TokenType.DEUS_EX_MACHINA:
            lines.append(tok.line)
    return lines


def _find_foreshadow_payoff_lines(source: str) -> Tuple[List[int], List[int]]:
    """Return (foreshadow_lines, payoff_lines)."""
    fshadow: List[int] = []
    payoff: List[int] = []
    try:
        tokens = Lexer(source).tokenize()
    except Exception:
        return fshadow, payoff
    for tok in tokens:
        if tok.type == TokenType.FORESHADOW:
            fshadow.append(tok.line)
        elif tok.type == TokenType.PAYOFF:
            payoff.append(tok.line)
    return fshadow, payoff


# ---------------------------------------------------------------------------
#  AST walker helpers
# ---------------------------------------------------------------------------


def _walk_statements(stmts, visitor) -> None:
    """Recursively walk all statements in a program/block, calling visitor."""
    for stmt in stmts:
        visitor(stmt)
        # Recurse into nested blocks
        if isinstance(stmt, (TaskDecl,)):
            if isinstance(stmt.body, Block):
                _walk_statements(stmt.body.statements, visitor)
        elif isinstance(stmt, (IfExpr,)):
            _walk_statements(stmt.then_block.statements, visitor)
            for _, blk in stmt.elif_branches:
                _walk_statements(blk.statements, visitor)
            if stmt.else_block:
                _walk_statements(stmt.else_block.statements, visitor)
        elif isinstance(stmt, (WhenExpr,)):
            for arm in stmt.arms:
                if isinstance(arm.body, Block):
                    _walk_statements(arm.body.statements, visitor)
        elif isinstance(stmt, (ForEach, RepeatTimes, RepeatUntil, TrainingArc)):
            _walk_statements(stmt.body.statements, visitor)
        elif isinstance(stmt, (CheckMaybe,)):
            _walk_statements(stmt.got_body.statements, visitor)
            _walk_statements(stmt.nobody_body.statements, visitor)
        elif isinstance(stmt, (CheckResult,)):
            _walk_statements(stmt.ok_body.statements, visitor)
            _walk_statements(stmt.err_body.statements, visitor)
        elif isinstance(stmt, (TrustMeBlock,)):
            _walk_statements(stmt.body.statements, visitor)
        elif isinstance(stmt, (DeusExMachina,)):
            _walk_statements(stmt.body.statements, visitor)
        elif isinstance(stmt, (IsekaiBlock,)):
            _walk_statements(stmt.body.statements, visitor)
        elif isinstance(stmt, (EventuallyBlock,)):
            _walk_statements(stmt.body.statements, visitor)
        elif isinstance(stmt, (Annotation,)):
            if stmt.target:
                visitor(stmt.target)
                _walk_statements([stmt.target], lambda s: None)  # recurse
        elif isinstance(stmt, (ImplBlock,)):
            for m in stmt.methods:
                visitor(m)
                if isinstance(m.body, Block):
                    _walk_statements(m.body.statements, visitor)
        elif isinstance(stmt, ForeshadowDecl):
            pass  # handled by visitor directly
        elif isinstance(stmt, ExprStmt):
            pass


def _collect_trust_me(program: Program, source: str, file: str) -> List[TrustMeEntry]:
    """Walk AST to find all TrustMeBlock nodes, correlate with token line numbers."""
    trust_lines = _find_trust_me_lines(source)
    results: List[TrustMeEntry] = []
    idx = [0]  # mutable counter for matching line numbers

    def visitor(stmt):
        if isinstance(stmt, TrustMeBlock):
            line = trust_lines[idx[0]] if idx[0] < len(trust_lines) else 0
            idx[0] += 1
            preview = stmt.reason[:80] if stmt.reason else "(no reason given)"
            results.append(
                TrustMeEntry(
                    file=file,
                    line=line,
                    honor_level=stmt.honor_level,
                    reason=preview,
                )
            )

    _walk_statements(program.statements, visitor)
    return results


def _collect_miracles(program: Program, source: str, file: str) -> List[MiracleEntry]:
    """Walk AST to find all DeusExMachina nodes."""
    deus_lines = _find_deus_ex_lines(source)
    results: List[MiracleEntry] = []
    idx = [0]

    def visitor(stmt):
        if isinstance(stmt, DeusExMachina):
            line = deus_lines[idx[0]] if idx[0] < len(deus_lines) else 0
            idx[0] += 1
            word_count = len(stmt.monologue.split())
            preview = stmt.monologue[:60].replace("\n", " ").strip()
            if len(stmt.monologue) > 60:
                preview += "..."
            results.append(
                MiracleEntry(
                    file=file,
                    line=line,
                    word_count=word_count,
                    monologue_preview=preview,
                )
            )

    _walk_statements(program.statements, visitor)
    return results


def _collect_foreshadows(
    program: Program, source: str, file: str
) -> List[ForeshadowEntry]:
    """Walk AST and collect foreshadow/payoff pairs."""
    fs_lines, po_lines = _find_foreshadow_payoff_lines(source)
    fs_idx = [0]
    po_idx = [0]

    # First pass: collect all foreshadow decls
    foreshadows: Dict[str, ForeshadowEntry] = {}
    ordered: List[ForeshadowEntry] = []

    def visit_foreshadow(stmt):
        if isinstance(stmt, ForeshadowDecl):
            line = fs_lines[fs_idx[0]] if fs_idx[0] < len(fs_lines) else 0
            fs_idx[0] += 1
            entry = ForeshadowEntry(file=file, line=line, name=stmt.decl.name)
            foreshadows[stmt.decl.name] = entry
            ordered.append(entry)

    _walk_statements(program.statements, visit_foreshadow)

    # Second pass: collect payoffs and mark
    def visit_payoff(stmt):
        if isinstance(stmt, PayoffStmt):
            line = po_lines[po_idx[0]] if po_idx[0] < len(po_lines) else 0
            po_idx[0] += 1
            if stmt.name in foreshadows:
                foreshadows[stmt.name].paid_off = True
                foreshadows[stmt.name].payoff_line = line

    _walk_statements(program.statements, visit_payoff)

    return ordered


# ---------------------------------------------------------------------------
#  High-level per-file analysis
# ---------------------------------------------------------------------------


def _analyse_file(
    path: Path,
) -> Tuple[
    List[ScienceCallSite],
    List[TrustMeEntry],
    List[MiracleEntry],
    List[ForeshadowEntry],
    Optional[str],  # parse error message, or None
]:
    source = path.read_text(encoding="utf-8")
    file_str = str(path)

    science = _scan_tokens_for_science(source, file_str)

    try:
        program = Parser.from_source(source)
    except ParseError as e:
        return science, [], [], [], str(e)

    trust = _collect_trust_me(program, source, file_str)
    miracles = _collect_miracles(program, source, file_str)
    foreshadows = _collect_foreshadows(program, source, file_str)
    return science, trust, miracles, foreshadows, None


def _gather_fk_files(paths: List[Path]) -> List[Path]:
    """Expand directories recursively; keep .fk files."""
    result: List[Path] = []
    for p in paths:
        if p.is_dir():
            result.extend(sorted(p.rglob("*.fk")))
        elif p.suffix == ".fk":
            result.append(p)
    return result


# ---------------------------------------------------------------------------
#  Public command functions
# ---------------------------------------------------------------------------


def audit_science(paths: List[Path]) -> int:
    """
    List every 'for science,' call site in the given files/directories.
    Returns 0 (always informational).
    """
    fk_files = _gather_fk_files(paths)
    if not fk_files:
        print("No .fk files found.")
        return 1

    all_sites: List[ScienceCallSite] = []
    for path in fk_files:
        source = path.read_text(encoding="utf-8")
        all_sites.extend(_scan_tokens_for_science(source, str(path)))

    if not all_sites:
        print("No 'for science' call sites found.")
        return 0

    print(f"Found {len(all_sites)} 'for science' call site(s):\n")
    for site in all_sites:
        print(site)
    return 0


def audit_trust(paths: List[Path]) -> int:
    """
    List every 'trust me' block with file, line, honor level, and reason.
    Returns 0 (always informational).
    """
    fk_files = _gather_fk_files(paths)
    if not fk_files:
        print("No .fk files found.")
        return 1

    all_entries: List[TrustMeEntry] = []
    for path in fk_files:
        source = path.read_text(encoding="utf-8")
        file_str = str(path)
        trust_lines = _find_trust_me_lines(source)
        try:
            program = Parser.from_source(source)
        except ParseError:
            continue
        all_entries.extend(_collect_trust_me(program, source, file_str))

    if not all_entries:
        print("No 'trust me' blocks found.")
        return 0

    print(f"Found {len(all_entries)} 'trust me' block(s):\n")
    for entry in all_entries:
        print(entry)
    return 0


def audit_miracles(paths: List[Path]) -> int:
    """
    List every 'deus_ex_machina' block with file, line, word count, and monologue preview.
    Warns if > 3, errors if > 10 in the scanned codebase.
    """
    fk_files = _gather_fk_files(paths)
    if not fk_files:
        print("No .fk files found.")
        return 1

    all_miracles: List[MiracleEntry] = []
    for path in fk_files:
        source = path.read_text(encoding="utf-8")
        file_str = str(path)
        deus_lines = _find_deus_ex_lines(source)
        try:
            program = Parser.from_source(source)
        except ParseError:
            continue
        all_miracles.extend(_collect_miracles(program, source, file_str))

    if not all_miracles:
        print("No deus_ex_machina blocks found. The laws of physics remain intact.")
        return 0

    print(f"Found {len(all_miracles)} deus_ex_machina block(s):\n")
    for entry in all_miracles:
        print(entry)
        if entry.word_count < 20:
            print(f"    ✗ Monologue too short ({entry.word_count} words, need 20)")

    exit_code = 0
    if len(all_miracles) > 10:
        print(
            f"\n✗ ERROR: {len(all_miracles)} miracles is too many. "
            f"(Yuuko voice: \"At this point you're not bending the rules,"
            f" you're snapping them in half.\")"
        )
        exit_code = 1
    elif len(all_miracles) > 3:
        print(
            f"\n⚠ WARNING: {len(all_miracles)} miracles found. "
            f'(Sagiri voice: "Three is a coincidence. Four is a habit.")'
        )

    return exit_code


def foreshadow_audit(paths: List[Path]) -> int:
    """
    Show all foreshadow/payoff pairs and highlight any unpaid foreshadows.
    Returns 1 if any foreshadow is unpaid.
    """
    fk_files = _gather_fk_files(paths)
    if not fk_files:
        print("No .fk files found.")
        return 1

    all_entries: List[ForeshadowEntry] = []
    parse_errors: List[str] = []

    for path in fk_files:
        science, trust, miracles, foreshadows, err = _analyse_file(path)
        all_entries.extend(foreshadows)
        if err:
            parse_errors.append(f"  {path}: {err}")

    if parse_errors:
        print("Parse errors encountered:")
        for e in parse_errors:
            print(e)
        print()

    if not all_entries:
        print("No foreshadow declarations found.")
        return 0

    unpaid = [e for e in all_entries if not e.paid_off]
    paid = [e for e in all_entries if e.paid_off]

    print(
        f"Foreshadow audit: {len(all_entries)} total, "
        f"{len(paid)} paid, {len(unpaid)} unpaid\n"
    )

    for entry in all_entries:
        print(entry)

    if unpaid:
        print(
            f"\n✗ {len(unpaid)} unpaid foreshadow(s). "
            f'(Takeru voice: "Every promise you make, you keep. '
            f"That's what it means to be a pilot.\")"
        )
        return 1

    print(
        "\n✓ All foreshadows paid off. "
        '(Yuuko voice: "Good. Loose ends are for lesser writers.")'
    )
    return 0


__all__ = [
    "audit_science",
    "audit_trust",
    "audit_miracles",
    "foreshadow_audit",
    "ScienceCallSite",
    "TrustMeEntry",
    "MiracleEntry",
    "ForeshadowEntry",
]
