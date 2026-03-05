"""
FREAK Lite CLI — transpile, compile, and run .fk programs.

Usage:
    python -m freakc run <file.fk>     Transpile + compile + execute
    python -m freakc build <file.fk>   Transpile + compile only
    python -m freakc check <file.fk>   Type-check only (no compilation)
    python -m freakc test              Run all tests/*.fk files
    python -m freakc <file.fk>         Same as 'run' (default)

Options:
    --keep-c        Keep the generated .c file
    -o, --output    Output binary name
"""

from __future__ import annotations

import glob

# ── Colour helpers ──────────────────────────────────────────────────
# Force UTF-8 on Windows
import io
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .auditor import audit_miracles, audit_science, audit_trust, foreshadow_audit
from .emitter import CEmitter, EmitError
from .parser import ParseError, Parser
from .type_checker import TypeChecker

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _c(code: str, msg: str) -> str:
    if not sys.stderr.isatty():
        return msg
    return f"\033[{code}m{msg}\033[0m"


def _dim(msg):
    return _c("90", msg)


def _green(msg):
    return _c("92", msg)


def _yellow(msg):
    return _c("93", msg)


def _red(msg):
    return _c("91", msg)


def _bold(msg):
    return _c("1", msg)


# ── Compiler pipeline ──────────────────────────────────────────────


def find_c_compiler() -> str | None:
    for cc in ("gcc", "clang", "cc"):
        if shutil.which(cc):
            return cc
    return None


def transpile(source: str, path: Path):
    """Parse + type-check + emit C.  Returns (c_source, diagnostics)."""
    try:
        program = Parser.from_source(source)
    except ParseError as e:
        return None, [f"Parse error: {e}"]

    # Type check
    checker = TypeChecker()
    diagnostics = checker.check(program)
    diag_msgs = []
    has_errors = False
    for d in diagnostics:
        prefix = _red("✗") if d.level == "error" else _yellow("⚠")
        diag_msgs.append(f"  {prefix} {d}")
        if d.level == "error":
            has_errors = True

    # Emit C even if there are warnings (but not errors)
    emitter = CEmitter()
    try:
        c_source = emitter.emit(program)
    except EmitError as e:
        diag_msgs.append(f"Emit error: {e}")
        return None, diag_msgs

    return c_source, diag_msgs


def compile_c(c_path: Path, out_bin: Path, runtime_dir: Path) -> tuple[bool, str]:
    """Compile the generated C file. Returns (success, message)."""
    cc = find_c_compiler()
    if not cc:
        return False, "No C compiler found (gcc/clang). Install one to compile."

    runtime_c = runtime_dir / "freak_runtime.c"
    cmd = [
        cc,
        "-o",
        str(out_bin),
        str(c_path),
        str(runtime_c),
        f"-I{runtime_dir}",
        "-g",
        "-std=c11",
        "-Wall",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, ""


# ── Subcommands ─────────────────────────────────────────────────────


def cmd_run(path: Path, keep_c: bool = False, output: str = None) -> int:
    """Transpile → compile → run."""
    source = path.read_text(encoding="utf-8")
    c_source, diags = transpile(source, path)

    for d in diags:
        print(d, file=sys.stderr)

    if c_source is None:
        return 1

    # Write C output
    out_c = path.with_suffix(".c")
    out_c.write_text(c_source, encoding="utf-8")
    print(_dim(f"→ Wrote {out_c}"))

    # Compile
    runtime_dir = Path(__file__).parent / "runtime"
    if output:
        out_bin = Path(output)
    else:
        out_bin = (
            path.with_suffix(".exe")
            if sys.platform == "win32"
            else path.with_suffix("")
        )

    print(_dim(f"→ Compiling..."))
    ok, err_msg = compile_c(out_c, out_bin, runtime_dir)
    if not ok:
        print(_red("✗ Compilation failed:"), file=sys.stderr)
        print(err_msg, file=sys.stderr)
        return 1

    print(_green(f"✓ Built {out_bin}"))

    if not keep_c:
        try:
            out_c.unlink()
        except OSError:
            pass

    # Run
    print(_dim("→ Running..."))
    print("─" * 40)
    result = subprocess.run([str(out_bin)], text=True)
    print("─" * 40)

    if result.returncode != 0:
        print(_red(f"✗ Process exited with code {result.returncode}"))

    return result.returncode


def cmd_build(path: Path, keep_c: bool = False, output: str = None) -> int:
    """Transpile → compile (no run)."""
    source = path.read_text(encoding="utf-8")
    c_source, diags = transpile(source, path)

    for d in diags:
        print(d, file=sys.stderr)

    if c_source is None:
        return 1

    out_c = path.with_suffix(".c")
    out_c.write_text(c_source, encoding="utf-8")
    print(_dim(f"→ Wrote {out_c}"))

    runtime_dir = Path(__file__).parent / "runtime"
    if output:
        out_bin = Path(output)
    else:
        out_bin = (
            path.with_suffix(".exe")
            if sys.platform == "win32"
            else path.with_suffix("")
        )

    print(_dim("→ Compiling..."))
    ok, err_msg = compile_c(out_c, out_bin, runtime_dir)
    if not ok:
        print(_red("✗ Compilation failed:"), file=sys.stderr)
        print(err_msg, file=sys.stderr)
        return 1

    print(_green(f"✓ Built {out_bin}"))

    if not keep_c:
        try:
            out_c.unlink()
        except OSError:
            pass

    return 0


def cmd_check(path: Path) -> int:
    """Type-check only (no compilation)."""
    source = path.read_text(encoding="utf-8")
    _, diags = transpile(source, path)

    if not diags:
        print(_green(f"✓ {path.name}: No issues found"))
        return 0

    print(f"{_bold(str(path))}:")
    has_errors = False
    for d in diags:
        print(d, file=sys.stderr)
        if "error" in d.lower() if isinstance(d, str) else False:
            has_errors = True
    return 1 if has_errors else 0


def cmd_test() -> int:
    """Run all tests/*.fk files."""
    test_dir = Path("tests")
    if not test_dir.exists():
        print(_red("✗ No tests/ directory found"))
        return 1

    fk_files = sorted(test_dir.glob("*.fk"))
    if not fk_files:
        print(_yellow("⚠ No .fk files found in tests/"))
        return 0

    passed = 0
    failed = 0

    for fk in fk_files:
        print(f"\n{_bold(fk.name)}:")
        result = cmd_run(fk, keep_c=False)
        if result == 0:
            passed += 1
        else:
            failed += 1

    print(f"\n{'─' * 40}")
    print(
        f"{_green(f'{passed} passed')}, {_red(f'{failed} failed') if failed else '0 failed'} "
        f"out of {len(fk_files)} tests"
    )
    return 1 if failed else 0


# ── Audit commands ─────────────────────────────────────────────────


def cmd_audit(sub: str, argv: list[str]) -> int:
    """Dispatch freak audit-* and freak foreshadow-audit commands."""
    from pathlib import Path as _P

    # Resolve target paths: remaining argv, or default to current dir
    raw_paths = argv if argv else ["."]
    paths = [_P(p) for p in raw_paths]

    if sub == "audit-science":
        return audit_science(paths)
    if sub == "audit-trust":
        return audit_trust(paths)
    if sub == "audit-miracles":
        return audit_miracles(paths)
    if sub == "foreshadow-audit":
        return foreshadow_audit(paths)

    print(_red(f"✗ Unknown audit command: '{sub}'"), file=sys.stderr)
    return 1


# ── Main ────────────────────────────────────────────────────────────


def cmd_hangar(argv: list[str]) -> int:
    """Handle 'freak hangar <subcommand>' commands."""
    from .hangar import hangar_add, hangar_init, hangar_install, hangar_remove

    if not argv:
        print(_red("✗ Missing hangar subcommand. Use: init, install, add, remove"))
        return 1

    sub = argv[0]
    project_dir = Path.cwd()

    if sub == "init":
        return hangar_init(project_dir)

    if sub == "install":
        return hangar_install(project_dir)

    if sub == "add":
        if len(argv) < 3:
            print(_red("✗ Usage: freak hangar add <name> <owner/repo>"))
            return 1
        name = argv[1]
        repo = argv[2]
        version = argv[3] if len(argv) > 3 else "latest"
        return hangar_add(project_dir, name, repo, version)

    if sub == "remove":
        if len(argv) < 2:
            print(_red("✗ Usage: freak hangar remove <name>"))
            return 1
        return hangar_remove(project_dir, argv[1])

    print(_red(f"✗ Unknown hangar subcommand: '{sub}'"))
    return 1


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    # Parse flags
    keep_c = "--keep-c" in argv
    argv = [a for a in argv if a != "--keep-c"]

    output = None
    if "-o" in argv:
        idx = argv.index("-o")
        if idx + 1 < len(argv):
            output = argv[idx + 1]
            argv = argv[:idx] + argv[idx + 2 :]
    if "--output" in argv:
        idx = argv.index("--output")
        if idx + 1 < len(argv):
            output = argv[idx + 1]
            argv = argv[:idx] + argv[idx + 2 :]

    if not argv:
        print("FREAK Lite Compiler v0.4.0")
        print()
        print("Usage:")
        print("  python -m freakc run <file.fk>       Transpile + compile + run")
        print("  python -m freakc build <file.fk>     Transpile + compile")
        print("  python -m freakc check <file.fk>     Type check only")
        print("  python -m freakc test                Run all tests/*.fk")
        print("  python -m freakc hangar <cmd>        Package manager")
        print(
            "  python -m freakc audit-science [paths]   List 'for science' call sites"
        )
        print("  python -m freakc audit-trust [paths]     List 'trust me' blocks")
        print("  python -m freakc audit-miracles [paths]  List deus_ex_machina blocks")
        print(
            "  python -m freakc foreshadow-audit [paths] Check foreshadow/payoff pairs"
        )
        print("  python -m freakc <file.fk>           Same as 'run'")
        print()
        print("Hangar commands:")
        print("  hangar init                  Create project skeleton")
        print("  hangar install               Install all dependencies")
        print("  hangar add <name> <repo>     Add a dependency")
        print("  hangar remove <name>         Remove a dependency")
        print()
        print("Audit commands scan one or more .fk files/directories (default: cwd).")
        print()
        print("Options:")
        print("  --keep-c       Keep generated .c file")
        print("  -o, --output   Output binary name")
        return 0

    cmd = argv[0]

    if cmd == "test":
        return cmd_test()

    if cmd == "hangar":
        return cmd_hangar(argv[1:])

    if cmd in ("audit-science", "audit-trust", "audit-miracles", "foreshadow-audit"):
        return cmd_audit(cmd, argv[1:])

    if cmd in ("run", "build", "check"):
        if len(argv) < 2:
            print(_red(f"✗ Missing file argument for '{cmd}'"), file=sys.stderr)
            return 1
        path = Path(argv[1])
        if not path.exists():
            print(_red(f"✗ File not found: {path}"), file=sys.stderr)
            return 1

        if cmd == "run":
            return cmd_run(path, keep_c, output)
        elif cmd == "build":
            return cmd_build(path, keep_c, output)
        elif cmd == "check":
            return cmd_check(path)

    # Default: treat first arg as a file to run
    path = Path(cmd)
    if not path.exists():
        print(_red(f"✗ Unknown command or file: '{cmd}'"), file=sys.stderr)
        return 1
    return cmd_run(path, keep_c, output)


if __name__ == "__main__":
    raise SystemExit(main())
