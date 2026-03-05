<div align="center">

```
███████╗██████╗ ███████╗ █████╗ ██╗  ██╗
██╔════╝██╔══██╗██╔════╝██╔══██╗██║ ██╔╝
█████╗  ██████╔╝█████╗  ███████║█████╔╝ 
██╔══╝  ██╔══██╗██╔══╝  ██╔══██║██╔═██╗ 
██║     ██║  ██║███████╗██║  ██║██║  ██╗
╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
```

**A programming language written by someone who has watched too much anime**  
and not enough sleep, but somehow it compiles.

[![License: MIT](https://img.shields.io/badge/license-MIT-pink?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/version-Alternative--4-red?style=flat-square)](freak-full-bible.md)
[![Status](https://img.shields.io/badge/status-definitely%20compiling-brightgreen?style=flat-square)](#)
[![Vibes](https://img.shields.io/badge/vibes-MONO__NO__AWARE-blueviolet?style=flat-square)](#)

</div>

---

## What is FREAK?

FREAK is a compiled, statically-typed, memory-safe systems language with a syntax inspired by visual novels, anime, and the kind of programming that only makes sense at 3am.

It compiles to native binaries. It has a borrow checker. It has **mood types**. It has a package manager called **Hangar**. It has a UI framework called **freak-ui**. And every variable is called `pilot` because you are always on a mission.

```fk
pilot name = "Takeru"
pilot power = 9001

task greet(name: word) -> void {
    say "Hello, {name}! Your power level is {power}."
}

greet(name)
```

That's it. That's the whole vibe.

---

## Features

### The Language

- **`pilot`** — variables. You are assigning a pilot to a mission.
- **`task`** — functions. Everything is a task.
- **`give back`** — return. Because `return` is cowardly.
- **`say`** — print. Always available. No imports.
- **`when`** — pattern matching. Destructures anything.
- **`fixed pilot`** — immutable binding. The pilot cannot be reassigned.
- **`trust-me`** — unsafe blocks. You asked for this.
- **`training arc`** — loops guaranteed to terminate (with a session cap).

### The Type System

| Type | What it is |
|---|---|
| `num` | 64-bit float. The default. Context-narrows to `int`. |
| `word` | UTF-8 string. Fat pointer. Knows its own length. |
| `big` | Arbitrary precision integer. Never overflows. Ever. |
| `maybe<T>` | Optional. `some(42)` or `nobody`. |
| `result<T, E>` | Success or failure. `ok(val)` or `err("message")`. |
| `mood` | Emotional state enum. `.chill` `.focused` `.hype` `.mono_no_aware` |
| `prob[lo..hi]` | A value constrained to a probability range. Yes, really. |
| `power<N>` | A number that must be ≥ N. The compiler enforces it. |

### The Mood System

FREAK has a compile-time `mood` type with real arithmetic:

```fk
pilot current_mood: mood = .focused

-- Moods can be added and subtracted
pilot new_mood = current_mood + .hype      -- .hype
pilot worn_out  = current_mood - .focused  -- .chill

-- Anime-aware standard library uses mood context
use std::anime::power_check
power_check(pilot_power, required: power<9000>)
```

Moods flow through the type system. The standard library uses them. The UI framework uses them for theming. They're not a joke. (They're a little bit of a joke.)

### Memory Safety

FREAK has a borrow checker — single owner, shared borrows, mutable borrows, the whole deal — and it does it with syntax that doesn't make you want to quit programming:

```fk
pilot data = [1, 2, 3, 4, 5]

-- Immutable borrow
task sum(items: &List<num>) -> num { ... }

-- Mutable borrow
task push_double(items: &mut List<num>, val: num) {
    items.push(val * 2)
}

-- Move (transfer ownership)
task consume(items: List<num>) -> void { ... }
```

If you need to step outside the rules, `trust-me` blocks give you raw pointers and full unsafety. You asked for this. The compiler will remember.

---

## Getting Started

### Install

```bash
# Clone the repo
git clone https://github.com/yourname/freak.git
cd freak

# Build the compiler (requires Python 3.10+ for FREAK Lite transpiler)
python -m freakc --version

# Or build the full self-hosting compiler
make freak
```

### Your First Program

Create `hello.fk`:

```fk
pilot name = "world"
say "Hello, {name}!"
say "Your mission has begun."
```

Compile and run:

```bash
freakc hello.fk -o hello
./hello
```

Output:
```
Hello, world!
Your mission has begun.
```

---

## Hangar — The Package Manager

Hangar is FREAK's package manager. Projects have a `hangar.toml`. Dependencies come from Git. It's simple.

```bash
# Initialize a new project
hangar init my-project
cd my-project

# Add a dependency
hangar add freak-ui https://github.com/yourname/freak-ui

# Install all dependencies
hangar install

# Remove a package
hangar remove freak-ui
```

`hangar.toml` looks like this:

```toml
[project]
name = "my-project"
version = "0.1.0"

[dependencies]
freak-ui = { git = "https://github.com/yourname/freak-ui", version = "latest" }
```

Dependencies live in `hangar_modules/`. The layout is deliberately minimal.

---

## freak-ui — The UI Framework

freak-ui is FREAK's immediate mode UI framework. It runs on Windows, macOS, and Linux. It has five built-in themes. It does not have widget trees, callbacks, or retained state. You just call widget functions in order and the frame renders.

```
Your FREAK app
     │
     ▼
freak-ui (Hangar)     ← widgets, layout, theming, input
     │
     ▼
std::ui               ← window, events, raw draw calls
     │
     ├── Windows: Win32 / Direct2D
     ├── macOS:   Cocoa / CoreGraphics
     └── Linux:   X11 / Cairo
```

### A Calculator in freak-ui

```fk
use freak_ui::{UI, Theme}
use std::ui::Window

pilot win = Window::open(WindowConfig { title: "Calc", width: 300, height: 400 })
pilot ui  = UI::new(Theme::default())

win.run(|canvas, events| {
    ui.begin_frame(canvas, events)

    ui.label("FREAK Calc", LabelStyle::title())

    if ui.button("7") { append_digit(7) }
    if ui.button("=") { evaluate() }

    ui.end_frame()
    give back true
})
```

### Themes

| Theme | Mood | Vibe |
|---|---|---|
| `Theme::default()` | `.focused` | Dark. Professional. Ready. |
| `Theme::light()` | `.chill` | Light. Calm. Readable. |
| `Theme::terminal()` | `.hype` | Green on black. Pure. |
| `Theme::alternative()` | `.muv_luv` | Navy and pink. Dangerous. |
| `Theme::muvluv()` | `.mono_no_aware` | Red and black. You know what you've done. |

---

## More Syntax Highlights

### Pattern Matching

```fk
when contact {
    BETA::Soldier { position }  -> engage_at(position)
    BETA::BRAIN   { .. }        -> request_orbital_strike()
    _                           -> say "unknown contact"
}
```

### Error Handling

```fk
-- Propagate errors with ?
task load_config(path: word) -> result<Config, word> {
    pilot data = fs::read(path)?
    pilot cfg  = Config::parse(data)?
    give back ok(cfg)
}

-- Handle inline
when load_config("settings.toml") {
    ok(cfg) -> use_config(cfg)
    err(e)  -> say "Config failed: {e}"
}
```

### Concurrency

```fk
use std::thread::spawn
use std::sync::Channel

pilot (tx, rx) = Channel::new()

pilot handle = spawn(copy(tx) || {
    tx.send("message from another dimension")
})

pilot msg = rx.recv()
say msg
handle.join()
```

### The Training Arc

```fk
-- A loop the compiler knows will end
training arc until power >= 9000 max 1000 sessions {
    practice()
    receive_trauma()
    power = power + 1
}
-- If max sessions is hit in tests, the compiler warns you
```

### Doctrines (Traits)

```fk
doctrine Displayable {
    task display(self) -> word
}

impl Displayable for Point {
    task display(self) -> word {
        give back "({self.x}, {self.y})"
    }
}

task print_it<T: Displayable>(val: T) {
    say val.display()
}
```

---

## The Standard Library

| Module | What it gives you |
|---|---|
| `std::fs` | File I/O |
| `std::net` | TCP, UDP, HTTP client |
| `std::json` | Parse and serialize JSON |
| `std::thread` | Threads, atomics, channels |
| `std::math` | Everything `num` needs |
| `std::time` | Timestamps, durations, sleep |
| `std::process` | Spawn processes, read env |
| `std::ui` | Native window, events, canvas |
| `std::anime` | Mood arithmetic, power checks |
| `std::narrative` | Death flags, foreshadow logs |
| `std::test` | Tests with vibes ratings |

Yes, `std::narrative` ships with the compiler. The `foreshadow_log.unpaid` field should be 0 at program end. This is a compiler warning if it isn't.

---

## Testing

```fk
test "addition works" {
    expect 2 + 2 to be 4
}

test "panics correctly" {
    expect divide(10, 0) to panic
}

test "sad path" @nakige {
    -- @nakige: this test is expected to make you feel something
    expect character.survives_ending to be false
}
```

Test output includes a **vibes rating**:
```
✓ addition works
✓ panics correctly  
✓ sad path

vibes: MONO_NO_AWARE  (almost there. so close.)
```

---

## Compiler Pipeline

```
.fk source
    │
    ▼
  Lexer          → tokens
    │
    ▼
  Parser         → AST
    │
    ▼
  Type Checker   → typed AST
    │
    ▼
  Borrow Checker → ownership validated
    │
    ▼
  Anime Layer    → mood/power/prob types resolved
    │
    ▼
  IR             → intermediate representation
    │
    ▼
  Optimizer      → dead code, inlining, strength reduction
    │
    ▼
  Native Binary  → your program
```

---

## Project Status

FREAK is under active development. The language specification is complete (see `freak-full-bible.md`). The transpiler (Python → C) implements the FREAK Lite subset. The full self-hosting compiler and freak-ui framework are in progress.

See [`freak-todo.md`](freak-todo.md) for the exact development checklist.

---

## Contributing

Read the bible first (`freak-full-bible.md`). It is the authoritative source. If something in the code disagrees with the bible, the bible wins.

Then:
1. Fork the repo
2. Create your branch: `git checkout -b feature/something-cool`
3. Write tests
4. Submit a PR

---

## License

MIT. Do whatever you want. Just know the `std::narrative` death flag system is watching.

---

<div align="center">

*"It was always going to end this way."*  
*— freak-ui mono_no_aware theme, on program exit*

</div>
