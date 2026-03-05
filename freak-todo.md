# FREAK Lite — Development Checklist
**Language:** Python → transpiles to C  
**Goal:** Get FREAK source files compiling to native binaries via Clang/GCC  
**Reference:** freak-lite-bible.md for all syntax/mapping details

---

## PHASE 0 — Project Setup
*Do this first. Takes 20 minutes.*

- [ ] Create project folder structure
- [ ] Set up `__main__.py` so `python -m freakc file.fk` works
- [ ] Create `tests/hello.fk` — first target program:
  ```
  pilot name = "Takeru"
  pilot power = 9001
  say "Hello from FREAK! {name} has power {power}."
  ```
- [ ] Confirm Python 3.10+
- [ ] Create `run.sh`: compile → clang → execute in one command

---

## PHASE 1 — Lexer
*Source string → list of Token objects*

- [ ] Define `Token` dataclass: `type`, `value`, `line`, `col`
- [ ] Define `TokenType` enum (all types from Bible Section 6.1)
- [ ] Implement `Lexer` class with `tokenize(source: str) -> list[Token]`
- [ ] Whitespace skipping, line number tracking
- [ ] `--` line comments (skip to end of line)
- [ ] Integer literals: `42`, `0xFF`, `0b1010`
- [ ] Float literals: `3.14`
- [ ] String literals `"..."` with `{interp}` markers
- [ ] Bool literals: `true`, `false`, `yes`, `no`, `hai`, `iie`
- [ ] Single-char tokens: `{ } ( ) [ ] , : . @ _`
- [ ] Multi-char operators: `-> => |> :: == != <= >= ** += -= *= /=`
- [ ] Identifiers and keywords (keyword list from Bible 6.1)
- [ ] Multi-word keywords (lex greedily):
  - `give back`, `or else`, `trust me`, `for each`
  - `training arc`, `on my honor as`
  - `knowing this will hurt`, `for science`
  - `PLUS ULTRA`, `FINAL FORM`
- [ ] `done` keyword as synonym for `}`
- [ ] TEST: tokenize `hello.fk`, print all tokens, visually verify

---

## PHASE 2 — Parser
*Token list → Program AST*

- [ ] Define all AST dataclasses (Bible Section 7.1)
- [ ] Implement `Parser` class with `parse() -> Program`
- [ ] `pilot x = expr` variable declarations
- [ ] `pilot x: Type = expr` with type annotation
- [ ] `say expr` print statement
- [ ] String interpolation: extract `{expr}` spans
- [ ] Literals: int, float, bool
- [ ] Identifiers and field access `a.b.c`
- [ ] Binary operators with correct precedence
- [ ] Unary operators: `not`, `-`
- [ ] Function calls `f(a, b)`
- [ ] `task` declarations (block, arrow, done forms)
- [ ] `give back expr`
- [ ] `if / else if / else` blocks
- [ ] `when` pattern match with arms and `_`
- [ ] `for each x in y { }` loop
- [ ] `repeat N times { }` loop
- [ ] `shape Name { }` struct declaration
- [ ] `impl` blocks (with and without doctrine)
- [ ] `{ }` and `done` blocks (identical)
- [ ] `[1, 2, 3]` list literals
- [ ] `{ "key": value }` map literals
- [ ] `(a, b)` tuple literals and destructuring
- [ ] `|x| => expr` and `|x| { block }` lambdas
- [ ] Generic type expressions: `maybe<T>`, `result<T,E>`, `List<T>`
- [ ] `some(x)`, `nobody`, `ok(x)`, `err(x)`
- [ ] `check expr { got x -> ... nobody -> ... }`
- [ ] `check result expr { ok(x) -> ... err(e) -> ... }`
- [ ] `expr?` error propagation
- [ ] `expr or else expr` fallback
- [ ] `use module::{items}` imports
- [ ] `launch` modifier
- [ ] `@annotation` annotations
- [ ] `trust me "msg" on my honor as .level { }`
- [ ] `training arc until cond max N sessions { }`
- [ ] `foreshadow pilot x = expr` and `payoff x`
- [ ] `knowing this will hurt, call()` and `sadly call()`
- [ ] `for science, call()`
- [ ] Anime operators as binary ops
- [ ] TEST: parse `hello.fk`, pretty-print AST, visually verify

---

## PHASE 3 — Minimal C Emitter (Hello World target)
*AST → C source string. Skip type checker. Get something running.*

- [ ] `CEmitter` class with `emit(program: Program) -> str`
- [ ] Emit `#include "freak_runtime.h"`
- [ ] Emit `int main() { freak_main(); return 0; }`
- [ ] `pilot x = 42` → `int64_t x = 42;`
- [ ] `pilot x = "hello"` → `freak_word x = freak_word_lit("hello");`
- [ ] `pilot x = true` → `bool x = true;`
- [ ] `say "Hello {name}!"` → `freak_say(freak_interpolate(...));`
- [ ] `task f(a: int) -> int { give back a; }` → C function
- [ ] Function forward declarations before definitions
- [ ] **★ MILESTONE: hello.fk compiles and runs ★**

---

## PHASE 4 — Runtime Header (freak_runtime.h)

- [ ] `freak_word` struct: data pointer + byte_length + char_count
- [ ] `freak_word_lit(const char* s)`
- [ ] `freak_say(freak_word msg)` — print with newline
- [ ] `freak_ask(freak_word prompt)` — read stdin
- [ ] `freak_interpolate(...)` — handle `{x}` substitution
- [ ] `freak_word_concat`, `freak_word_eq`
- [ ] `freak_word_from_int`, `freak_word_from_double`
- [ ] `freak_panic(freak_word msg)` — print + exit(1)
- [ ] Generated `freak_maybe_T` structs per type used
- [ ] Generated `freak_result_T_E` structs per type combo used
- [ ] Generated `freak_list_T` structs with push/get/length/filter/map/fold

---

## PHASE 5 — Full C Emitter

- [ ] `if / else if / else` → C if/else
- [ ] `when` → switch (int) or strcmp chain (word)
- [ ] `for each x in list` → C for loop
- [ ] `repeat N times` → C for loop
- [ ] `training arc` → C while with session counter
- [ ] `shape` → C typedef struct (topologically sorted)
- [ ] `impl` methods → C functions with shape pointer first arg
- [ ] Closures → capture struct + function pointer (Bible Section 2.6)
- [ ] `|>` pipe → desugar to nested calls or temp vars
- [ ] `?` operator → inline result check + early return
- [ ] `check` (maybe) → if/else on has_value
- [ ] `check result` → if/else on is_ok
- [ ] `or else` → ternary fallback
- [ ] `some/nobody/ok/err` → macro calls
- [ ] List literals → new() + push calls
- [ ] Destructuring → temp var + field assignments
- [ ] `launch` → non-static; no launch → static
- [ ] `trust me` → plain C block + compile-time log
- [ ] `foreshadow/payoff` → C comments + symbol table tracking
- [ ] Annotations → C comments
- [ ] `knowing this will hurt` / `sadly` / `for science` → strip prefix, call normally
- [ ] `route` return type → generated enum + tagged union
- [ ] Anime operators → C expressions (Bible Section 2.12)
- [ ] Generics → monomorphise per concrete type used

---

## PHASE 6 — Type Checker

- [ ] Symbol table: variables and types per scope
- [ ] Type inference for all literals (Bible Section 8.3)
- [ ] All referenced variables declared before use
- [ ] Function call argument counts match signature
- [ ] Explicit annotations consistent with inferred types
- [ ] `give back` type matches task return type
- [ ] `check` only on `maybe<T>` values
- [ ] `check result` only on `result<T,E>` values
- [ ] `?` only inside result-returning tasks
- [ ] `foreshadow` variables paid off before scope ends
- [ ] `@nakige` tasks called with acknowledgement
- [ ] Only ONE `@season_finale` per program
- [ ] Annotate every AST node with resolved type
- [ ] Clear, line-numbered error messages

---

## PHASE 7 — CLI

- [ ] `freak run file.fk` — compile and run
- [ ] `freak build file.fk` — compile to binary
- [ ] `freak check file.fk` — type check only
- [ ] `freak test` — run all test blocks
- [ ] `--output / -o` flag
- [ ] `--keep-c` flag (keep emitted C for debugging)
- [ ] Friendly errors: filename, line number, highlighted bad line

---

## PHASE 8 — Audit Commands
*No AI API needed — these are pure static analysis over the AST*

- [x] `freak audit-science` — list every `for science,` call site in the project
- [x] `freak audit-trust` — list every `trust me` block with file, line, honor level, and message
- [x] `freak audit-miracles` — list every `deus_ex_machina` block with monologue preview
- [x] `freak foreshadow-audit` — show all foreshadow/payoff pairs and any unpaid ones

---

## PHASE 9 — Hangar Package Manager (v1)

- [ ] `hangar.toml` parsing (use `tomllib`, built-in since Python 3.11)
- [ ] `freak hangar init` — project skeleton + hangar.toml
- [ ] `freak hangar install` — download deps to `hangar_cache/`
- [ ] `freak hangar add [package]` — add dep + update hangar.toml
- [ ] Basic registry: GitHub releases is fine for v1
- [ ] Resolve `use muvluv::{}` imports to downloaded files

---

## PHASE 10 — muvluv Package (Official)
*The flagship Hangar package. You maintain this.*

- [ ] `Eishi` type: name, power, status, callsign
- [ ] `BETA::Tier` enum: Soldier → Grappler → Destroyer → Tank → Laser → Fort → BRAIN
- [ ] `Tier::required_power()` method
- [ ] `TSF` type: model, variant, mounted_weapon, os_version
- [ ] `COSMO` module: request_strike() (stub — prints confirmation)
- [ ] `YuukoLab` helpers for @experiment scaffolding
- [ ] Write the BETA early warning system as the showcase example
- [ ] Publish to Hangar registry

---

## MILESTONES

```
[x] M1  — hello.fk compiles and runs              (Phase 0-3)
[x] M2  — variables, tasks, if/when/loops all work (Phase 5 partial)
[x] M3  — closures and pipes work
[x] M4  — maybe<T> and result<T,E> fully work
[x] M5  — type checker catching real errors        (Phase 6)
[x] M6  — `freak run` CLI works end-to-end         (Phase 7)
[x] M7  — Audit commands (freak audit-science/trust/miracles/foreshadow-audit)
[x] M8  — muvluv installable via Hangar            (Phase 9-10)
[x] M9  — BETA early warning system runs in FREAK
[x] M10 — GitHub repo public, README written       ← tell people
```

---

## QUICK TIPS

**How to use Opus when building:**
Paste `freak-lite-bible.md` into the context window first.
Then ask for one phase at a time. e.g.:
- *"Write the Python Lexer class for FREAK based on Section 6 of this spec"*
- *"Write the C emitter for closures based on Section 2.6 of this spec"*

**The one rule:**
Get M1 working before doing anything else.
A running Hello World beats a perfect unfinished type checker every time.

---

## PHASE 11 — std::process
*Run and manage external processes*

- [x] `process::run(cmd: word, args: List<word>) -> result<Output, word>`
  — run a command, wait for it, return stdout/stderr/exit code
- [x] `process::spawn(cmd: word, args: List<word>) -> result<Process, word>`
  — launch without waiting (background process)
- [x] `process::pid() -> uint` — current process ID
- [x] `process::exit(code: int)` — terminate with exit code
- [x] `Process` shape: `.pid`, `.wait() -> result<int, word>`, `.kill() -> result<void, word>`
- [x] `Output` shape: `.out: word`, `.err: word`, `.exit_code: int`, `.success: bool`
- [x] `process::env_var(name: word) -> maybe<word>` — read environment variable
- [x] `process::set_env(name: word, val: word)` — set environment variable
- [x] `process::args() -> List<word>` — command line arguments passed to this program

---

## PHASE 12 — std::thread
*Raw thread control beyond the Squadron model*
*Squadron (sorties/formation) is for structured concurrency.*
*std::thread is for when you need direct control.*

- [x] `thread::spawn(f: OneShot) -> ThreadHandle` — create a raw OS thread
- [x] `thread::current_id() -> uint` — ID of the calling thread
- [ ] `thread::sleep(d: Duration)` — already in std::time, re-export here
- [x] `thread::yield()` — hint to scheduler to switch threads (`freak_thread_yield_now`)
- [x] `ThreadHandle` shape:
  - `.join() -> result<void, word>` — wait for thread to finish
  - `.id() -> uint`
  - `.is_finished() -> bool`
- [x] `thread::available_parallelism() -> uint` — number of logical CPU cores
- [x] Atomic types for lock-free shared state:
  - `Atomic<int>` with `.load()`, `.store(val)`, `.fetch_add(n)`, `.compare_swap(old, new)`
  - `Atomic<bool>` with `.load()`, `.store(val)`, `.flip()`
- [x] Note: for most concurrency use Squadron model — std::thread is the escape hatch

---

## PHASE 13 — std::bytes
*ByteBuffer type for binary I/O*

- [x] `ByteBuffer` shape — growable buffer with read/write cursor
- [x] `ByteBuffer::new() -> ByteBuffer`
- [x] `ByteBuffer::from(data: List<tiny>) -> ByteBuffer`
- [x] `.write_byte(b: tiny)` — append one byte
- [x] `.write_int(n: int)` — append 8 bytes little-endian
- [x] `.write_int_be(n: int)` — big-endian
- [x] `.write_word(s: word)` — append UTF-8 bytes (no null terminator)
- [x] `.write_bytes(data: List<tiny>)` — append raw bytes
- [x] `.read_byte() -> maybe<tiny>` — read one byte, advance cursor
- [x] `.read_int() -> maybe<int>` — read 8 bytes little-endian
- [x] `.read_word(len: uint) -> maybe<word>` — read N bytes as UTF-8 word
- [x] `.seek(pos: uint)` — move read cursor to position
- [x] `.position() -> uint` — current read cursor position
- [x] `.length() -> uint` — total bytes written
- [x] `.to_list() -> List<tiny>` — export as raw byte list
- [x] `.to_word() -> result<word, word>` — interpret bytes as UTF-8 string
- [x] Useful for: file formats, network packets, binary protocols

---

## PHASE 14 — Operator Overloading via Doctrines
*Properly spec and implement operator overloading*

- [x] Define built-in operator doctrines:
  ```
  doctrine Add    { task add(self, other: Self) -> Self }
  doctrine Sub    { task sub(self, other: Self) -> Self }
  doctrine Mul    { task mul(self, other: Self) -> Self }
  doctrine Div    { task div(self, other: Self) -> Self }
  doctrine Neg    { task neg(self) -> Self }              -- unary -
  doctrine Eq     { task equals(self, other: Self) -> bool }
  doctrine Ord    { task compare(self, other: Self) -> Order }
  doctrine Index  { task index(self, i: uint) -> T }      -- x[i]
  doctrine IndexMut { task index_mut(self, i: uint) -> lend mut T }
  ```
- [x] Emitter tracks `impl Doctrine for Type` blocks in `impl_doctrines` dict
- [x] Emitter: `a + b` → `TypeName_add(&a, b)` when left type implements `Add`
- [x] Emitter: `a - b` → `TypeName_sub(&a, b)` when left type implements `Sub`
- [x] Emitter: `a * b` → `TypeName_mul(&a, b)` when left type implements `Mul`
- [x] Emitter: `a == b` → `TypeName_equals(&a, b)` when type implements `Eq`
- [x] Emitter: `-a` → `TypeName_neg(&a)` when type implements `Neg`
- [x] Type inference for overloaded operator results uses method return type
- [x] Example — Vector type working in `tests/operator_overload.fk`:
  ```
  shape Vector2 { x: num, y: num }
  impl Add for Vector2 {
      task add(self, other: Vector2) -> Vector2 {
          give back Vector2 { x: self.x + other.x, y: self.y + other.y }
      }
  }
  pilot v = Vector2 { x: 1.0, y: 2.0 } + Vector2 { x: 3.0, y: 4.0 }
  ```
- [x] `word` implements Add (concatenation): `"Hello" + " World"` → `freak_word_concat`
- [ ] `Ord` doctrine (compare returning Order enum) — deferred to future phase
- [ ] `Index` / `IndexMut` doctrines — deferred to future phase

---

## PHASE 15 — Hangar Community Packages (Seed these yourself or wait for community)
*These don't ship with the compiler. They live in the Hangar registry.*
*Mark as official (freak- prefix, core team maintained) or community.*

- [ ] `freak-http` — HTTP client and server (official, maintain yourself)
  - `http::get(url)`, `http::post(url, body)` returning `promise<result<Response, word>>`
  - `http::serve(port, handler)` basic server
- [ ] `freak-json` — JSON parse and emit (official)
  - `json::parse(s: word) -> result<JsonValue, word>`
  - `json::emit(v: JsonValue) -> word`
  - `JsonValue` enum: Null / Bool / Num / Str / List / Object
- [ ] `freak-win32` — Windows API bindings (community)
  - Wraps common Win32 calls via `trust me` blocks
  - Window creation, message loop, GDI basics
- [ ] `freak-ui` — cross-platform UI (community, big project)
  - Probably wraps a C UI library (e.g. libui or nuklear)
- [ ] `freak-zip` — zip file reading and writing (community)
  - `zip::read(path) -> result<ZipArchive, word>`
  - `zip::write(path, entries) -> result<void, word>`
- [ ] `freak-image` — image loading and pixel manipulation (community)
  - Load PNG/JPEG/BMP into a `Bitmap` shape
  - `Bitmap` shape: width, height, pixels: List<Pixel>
  - `Pixel` shape: r, g, b, a as tiny
  - Save back to file
- [ ] `freak-regex` — regular expressions (community)
  - `regex::match(pattern: word, input: word) -> maybe<Match>`
  - `regex::find_all(pattern, input) -> List<Match>`
- [ ] `freak-sqlite` — SQLite database (community)
  - `sqlite::open(path) -> result<Database, word>`
  - `db.query(sql, params) -> result<List<Row>, word>`
- [ ] `freak-tls` — TLS/HTTPS (community, wraps OpenSSL or mbedTLS)
- [ ] `freak-datetime` — timezones, date arithmetic (community)

---

## UPDATED MILESTONES

```
[x] M1  — hello.fk compiles and runs              (Phase 0-3)
[x] M2  — variables, tasks, if/when/loops all work (Phase 5 partial)
[x] M3  — closures and pipes work
[x] M4  — maybe<T> and result<T,E> fully work
[x] M5  — type checker catching real errors        (Phase 6)
[x] M6  — `freak run` CLI works end-to-end         (Phase 7)
[x] M7  — Audit commands (freak audit-science/trust/miracles/foreshadow-audit)
[x] M8  — muvluv installable via Hangar            (Phase 9-10)
[x] M9  — BETA early warning system runs in FREAK
[x] M10 — GitHub repo public, README written       ← tell people
[x] M11 — std::process, std::thread, std::bytes done (runtime stubs + emitter + tests)
[x] M12 — operator overloading works (Add/Sub/Mul/Div/Neg/Eq via doctrines)
[ ] M13 — freak-http and freak-json published to Hangar
[ ] M14 — freak-image and freak-zip exist (yours or community)
[ ] M15 — self-hosting compiler started            ← the big one
```

---

## SESSION NOTES — What was done this session

### New language features
- **`deus_ex_machina` block** — lexer token, parser AST node (`DeusExMachina`), emitter (C block with dramatic comment), type checker (validates monologue ≥ 20 words)
- **`isekai` block** — lexer/parser/emitter/type checker; fresh isolated scope with `bringing back { ... }` exports
- **`eventually` block** — lexer/parser/emitter/type checker; `eventually { }` and `eventually if cond { }` forms
- **`PathIdent` AST node** — namespace path expressions like `process::pid()` and `ByteBuffer::new()`

### Audit commands (Phase 8)
- `freakc/auditor.py` — new module with AST walker + token scanner
- `freak audit-science` — finds every `for science,` call site with line numbers
- `freak audit-trust` — lists every `trust me` block with honor level and reason
- `freak audit-miracles` — lists every `deus_ex_machina` block, warns >3, errors >10
- `freak foreshadow-audit` — shows all foreshadow/payoff pairs, flags unpaid ones

### std::process / std::thread / std::bytes (Phases 11–13)
- Runtime header declarations and C stub implementations in `freak_runtime.h/.c`
- Emitter PathIdent call dispatch: `process::pid()` → `freak_process_pid()`
- ByteBuffer method dispatch table in emitter (type-aware, avoids `freak_word_length` collision)
- Correct return type inference for all std module calls
- `tests/process.fk`, `tests/bytes.fk` — compile and run

### Operator overloading (Phase 14)
- Emitter tracks `impl_doctrines: Dict[type → set[doctrine]]` during first pass
- `
