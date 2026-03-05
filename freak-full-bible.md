# FREAK FULL LANGUAGE BIBLE
## The Complete Authoritative Reference — Full Language, No Exclusions
### Version: Alternative-4 Edition | Status: Authoritative | Supersedes: freak-lite-bible.md

---

## WHAT THIS DOCUMENT IS

This is the complete FREAK language specification. It covers every feature
of the full language including all features excluded from FREAK Lite.

FREAK Lite (the Python → C transpiler) implements a subset of this.
The full FREAK compiler (self-hosting, written in FREAK itself) implements all of it.

When building the self-hosting compiler, use this document, not freak-lite-bible.md.

Pipeline (full compiler):
  .fk source → Lexer → Parser → Type Checker → Borrow Checker →
  Anime Layer → IR → Optimizer → Native Binary

---

## SECTION 1: SYNTAX — COMPLETE REFERENCE

### 1.1 Variables

```
pilot x = 42
pilot name = "Takeru"
pilot active = true
pilot ratio = 3.14
pilot x: int = 42           -- explicit type annotation
pilot x: word = "hello"
```

- `pilot` is the variable keyword — you are assigning a pilot to a mission
- Type annotation optional — inferred from value
- Semicolons optional everywhere
- Mutable by default
- Immutable binding: `fixed pilot x = 42` — cannot be reassigned

### 1.2 Functions

```
task add(a: num, b: num) -> num {
    give back a + b
}

task greet(name: word) -> void {
    say "Hello, {name}!"
}

-- Arrow shorthand (single expression)
task square(x: num) => x * x

-- done keyword closes blocks (identical to })
task cube(x: num) -> num
    give back x * x * x
done

-- Named parameters at call site
task connect(host: word, port: int, timeout: int) -> result<Connection, word>

connect(host: "localhost", port: 8080, timeout: 30)
```

- `task` — function keyword
- `give back` — return keyword
- `say` — print keyword (always available, no import)
- String interpolation: `{expr}` inside double-quoted strings
- `{}` and `done` are identical block delimiters

### 1.3 Types — Primitive

| FREAK type  | Notes                                                          |
|-------------|----------------------------------------------------------------|
| num         | 64-bit float. Default numeric type. Context-narrows to int.   |
| int         | 64-bit signed integer                                          |
| uint        | 64-bit unsigned integer                                        |
| tiny        | 8-bit unsigned (single byte)                                   |
| float       | 64-bit IEEE 754 double (explicit)                              |
| float32     | 32-bit IEEE 754 single                                         |
| big         | Arbitrary precision integer. Heap-allocated. Never overflows.  |
| word        | UTF-8 string. Fat pointer (data + byte_len + char_count).      |
| bool        | Boolean. true/false/yes/no/hai/iie all valid literals.         |
| char        | Unicode scalar value (32-bit codepoint)                        |
| void        | Unit type. Absence of value.                                   |
| [T; N]      | Fixed-size array. Stack-allocated. Size known at compile time. |
| (A, B, ...) | Tuple. Heterogeneous fixed grouping.                           |
| *T          | Raw pointer. Only inside trust-me blocks.                      |
| *mut T      | Raw mutable pointer. Only inside trust-me blocks.              |

### 1.4 Types — Compound

```
maybe<T>           -- optional value
some(42)           -- construct with value
nobody             -- empty

result<T, E>       -- success or failure
ok(42)             -- success
err("message")     -- failure

List<T>            -- dynamic array
[1, 2, 3]          -- literal

Map<K, V>          -- hash map
{ "key": value }   -- literal

Set<T>             -- unique value collection
Lineup<T>          -- FIFO queue

(A, B)             -- tuple
(42, "hello")      -- literal
```

### 1.5 Shapes (Structs)

```
shape Point {
    x: num
    y: num
}

-- Instantiate
pilot p = Point { x: 3.0, y: 4.0 }

-- Methods via impl
impl Point {
    task distance(self, other: Point) -> num {
        pilot dx = self.x - other.x
        pilot dy = self.y - other.y
        give back (dx*dx + dy*dy).sqrt()
    }
}

-- Shapes with generic fields
shape Pair<A, B> { first: A, second: B }
```

### 1.6 Doctrines (Traits)

```
doctrine Displayable {
    task display(self) -> word
}

impl Displayable for Point {
    task display(self) -> word {
        give back "({self.x}, {self.y})"
    }
}

-- Generic with doctrine bound
task print_it<T: Displayable>(val: T) {
    say val.display()
}

-- Multi-bound
task log_sorted<T: Comparable + Displayable>(items: List<T>) { ... }

-- Built-in operator doctrines
doctrine Add     { task add(self, other: Self) -> Self }
doctrine Sub     { task sub(self, other: Self) -> Self }
doctrine Mul     { task mul(self, other: Self) -> Self }
doctrine Div     { task div(self, other: Self) -> Self }
doctrine Neg     { task neg(self) -> Self }
doctrine Eq      { task equals(self, other: Self) -> bool }
doctrine Ord     { task compare(self, other: Self) -> Order }
doctrine Index   { task index(self, i: uint) -> T }

-- Operator overloading: implement Add and + works
impl Add for Vector2 {
    task add(self, other: Vector2) -> Vector2 {
        give back Vector2 { x: self.x + other.x, y: self.y + other.y }
    }
}
pilot v = v1 + v2   -- calls freak_add_Vector2
```

### 1.7 Control Flow

```
-- if/else
if x > 10 { say "big" }
else if x > 5 { say "medium" }
else { say "small" }

-- when (pattern match)
when x {
    1    -> say "one"
    2    -> say "two"
    _    -> say "other"
}

-- when with destructuring
when contact {
    BETA::Soldier { position } -> engage_at(position)
    BETA::BRAIN   { .. }       -> request_orbital_strike()
    _                          -> say "unknown contact"
}

-- for each
for each item in my_list { say item }

-- for each with index
for each (i, item) in my_list.enumerate() { say "{i}: {item}" }

-- repeat N times
repeat 5 times { do_thing() }

-- repeat until
repeat until condition { do_thing() }

-- training arc: loop guaranteed to eventually terminate
training arc until power >= 9000 max 100 sessions {
    practice()
    receive_trauma()
}
-- compiles to while loop with iteration counter cap
-- compiler warns if max sessions is never reached in testing

-- break and continue work inside all loops
for each item in list {
    if item.skip { continue }
    if item.fatal { break }
    process(item)
}
```

### 1.8 Closures and Lambdas

```
-- Arrow lambda
pilot double = |x: num| => x * 2

-- Block lambda
pilot clamp = |x: num, lo: num, hi: num| {
    if x < lo { give back lo }
    if x > hi { give back hi }
    give back x
}

-- Capture modes
pilot threshold = 100

-- Default: borrow (immutable borrow of outer vars)
pilot check = |x| => x > threshold

-- copy: copy value into closure (safe across threads)
pilot check2 = copy |x| => x > threshold

-- move: closure takes ownership
pilot handler = move |x| { process(x) }

-- mut: closure mutates captured variable
pilot count = 0
pilot counter = mut |_| { count += 1 }

-- Closure doctrine types (auto-inferred, never written manually)
-- Callable    — borrows captures, callable many times
-- MutCallable — mutates captures, one active call at a time
-- OneShot     — moves captures, callable exactly ONCE
```

### 1.9 Pipe Operator

```
pilot result = data
    |> filter(|x| => x > 0)
    |> map(|x| => x * 2)
    |> take(10)
    |> collect()
```

### 1.10 Error Handling

```
-- ? propagates errors
task parse_and_double(s: word) -> result<int, word> {
    pilot n = parse_int(s)?
    give back ok(n * 2)
}

-- check (maybe)
check find_user(id) {
    got u    -> say u.name
    nobody   -> say "not found"
}

-- check result
check result parse_int(s) {
    ok(n)    -> say "Got: {n}"
    err(msg) -> say "Error: {msg}"
}

-- or else: fallback
pilot n = parse_int(input) or else 0
```

### 1.11 Generics

```
task first<T>(list: List<T>) -> maybe<T> {
    if list.empty() { give back nobody }
    give back some(list[0])
}

-- Multi-bound
task log_sorted<T: Comparable + Displayable>(items: List<T>) { ... }

-- Generic shape
shape Pair<A, B> { first: A, second: B }
```

### 1.12 Borrowing and Ownership

Full borrow rules — see Section 4.

```
-- Immutable borrow
task print_name(lend p: Person) { say p.name }

-- Mutable borrow
task rename(lend mut p: Person, name: word) { p.name = name }

-- Ownership transfer (move)
task consume(p: Person) { ... }   -- p is moved in, caller loses it

-- Copy types (primitives): automatically copied, no move
pilot a = 42
pilot b = a    -- b is a copy, a still valid

-- Clone: explicit deep copy
pilot c = p.clone()
```

### 1.13 Modules and Imports

```
-- Import from local module
use tactics::{engage, Formation}

-- Import everything
use tactics::*

-- Import from Hangar package
use muvluv::{TSF, Eishi, Alternative}

-- Aliased import
use cosmo::OrbitalStrike as Strike

-- Conditional import (feature flag)
use[feature="orbital"] cosmo::GBomb

-- Making things public
launch task my_function() { ... }
launch shape MyType { ... }
```

---

## SECTION 2: ADVANCED TYPE SYSTEM

### 2.1 power<N> — Compile-Time Capability Type

power<N> is a compile-time numeric annotation that tracks whether a value
has sufficient capability to perform an operation. N is any numeric literal
or the special value `over9000`.

```
-- Declare a value with power level
pilot takeru: power<9001> = Eishi::new("Takeru")
pilot generic_pilot: power<3000> = Eishi::new("Generic")

-- Tasks can require minimum power
task engage_fort(pilot: power<7000>) -> result<void, word> {
    -- only callable with power >= 7000
    ...
}

-- Compiler enforces at call site:
engage_fort(takeru)          -- OK: 9001 >= 7000
engage_fort(generic_pilot)   -- COMPILE ERROR: power 3000 < required 7000
-- Error (Sagiri voice): "3000. The requirement is 7000. Do the math."

-- Power arithmetic: adding powers produces their sum type
task combine<A: num, B: num>(a: power<A>, b: power<B>) -> power<A + B>

-- power<over9000>: uncapped, satisfies any power requirement
pilot protagonist: power<over9000> = Eishi::new("Takeru")
engage_fort(protagonist)     -- always OK

-- @protagonist annotation auto-grants power<over9000>
@protagonist
pilot takeru = Eishi::new("Takeru")   -- inferred power<over9000>

-- Runtime check (for dynamically determined power)
if pilot.power >= required_power {
    engage(pilot)
}
```

Power levels are erased at runtime — zero overhead. All checks happen at
compile time via the type system. They are purely a correctness annotation.

### 2.2 prob[lo..hi] — Probability Distribution Type

prob[lo..hi] is a value that carries a probability range rather than a
concrete value. Useful for expressing uncertainty, dice rolls, skill checks,
and BETA encounter probability calculations.

```
-- Declare a probability value
pilot hit_chance: prob[0.0..1.0] = 0.75

-- Probability range can be narrower
pilot accuracy: prob[0.5..0.95] = 0.82

-- Operations on prob values return prob values with adjusted ranges
pilot adjusted = accuracy * 1.1        -- range scales: prob[0.55..1.0]
pilot combined = hit_chance * accuracy -- prob[0.0..0.95]

-- Resolve a probability: sample it
pilot did_hit: bool = hit_chance.resolve()

-- Resolve with seed (deterministic — useful for tests)
pilot did_hit = hit_chance.resolve_seeded(seed: 42)

-- expected(): get the midpoint of the range
pilot expected_hit = hit_chance.expected()   -- 0.75

-- Probability gates: only execute if probability check passes
prob[0.3] chance {
    trigger_ambush()
}
-- compiles to: if (freak_prob_roll(0.3)) { trigger_ambush(); }

-- Probability match: exhaustive probability branching
prob_when hit_chance {
    >= 0.9 -> critical_hit()
    >= 0.5 -> normal_hit()
    _      -> miss()
}

-- @fixed_fate annotation: removes probability, makes outcome certain
@fixed_fate
pilot hit: prob[1.0..1.0] = 1.0    -- always hits. fate has decided.
```

### 2.3 causality<T> — Cross-Timeline Broadcast Type

causality<T> is a value that exists across multiple registered timelines
simultaneously. Writing to it broadcasts the write to all timelines.
Reading from it returns the value in the current timeline.

```
-- Declare a causality value
pilot shared_memory: causality<word> = causality::new("initial")

-- Register timelines
pilot timeline_a = causality::register("timeline-A")
pilot timeline_b = causality::register("timeline-B")

-- Write: broadcasts to ALL registered timelines
shared_memory.write("updated value")
-- Compiler emits: "causality write on line N. All timelines notified."

-- Read: returns value in current timeline
pilot current = shared_memory.read()

-- Timeline-specific read
pilot from_a = shared_memory.read_from(timeline_a)

-- Causality conductor: manage multiple causality values together
pilot conductor = causality::Conductor::new()
conductor.add(shared_memory)
conductor.add(timeline_flag)

-- Broadcast to all at once
conductor.broadcast()

-- Observe changes across timelines
conductor.on_diverge(|timeline, value| {
    say "Timeline {timeline} diverged: {value}"
})

-- declare was: assert what a value was in a previous timeline
-- Compiler verifies consistency across timeline branches
declare shared_memory was "initial" in timeline "timeline-A"

-- The @fixed_fate annotation prevents causality divergence
-- A @fixed_fate causality<T> has the same value in all timelines
```

### 2.4 Mood Type — Emotional State System

mood is a built-in enum type. Values can be combined with + to produce
compound moods. The full compound table:

```
-- Mood literals (all .variant syntax)
pilot state: mood = .chill

-- Simple moods
.chill          -- relaxed, low urgency
.hype           -- high energy, motivated
.chaotic        -- unpredictable
.focused        -- locked in
.tired          -- low energy
.done           -- finished. no more.
.amae           -- comfortable dependency on others
.mono_no_aware  -- bittersweet awareness of impermanence
.ganbatte       -- trying one's hardest
.shoganai       -- acceptance of the unchangeable
.ikigai         -- reason for being
.muv_luv        -- terminal. you know what it means.

-- Compound mood arithmetic (all produce new mood values)
.chill + .hype           = .focused
.hype + .tired           = .wired
.chaotic + .focused      = .genius
.tired + .tired          = .done
.amae + .focused         = .trust
.mono_no_aware + .shoganai = .muv_luv
.ganbatte + .tired       = .hero
.ikigai + .ganbatte      = .protagonist
.done + anything         = .done      -- terminal, absorbs all

-- Mood affects compiler warnings and runtime behavior
-- @protagonist annotation auto-sets mood to .protagonist
-- Code with mood .muv_luv emits a quiet compiler note:
--   "note: this code carries the weight of all timelines."

-- Mood-based branching
when pilot.mood {
    .focused    -> assign_critical_mission(pilot)
    .done       -> send_to_rest(pilot)
    .muv_luv    -> knowing this will hurt, final_mission(pilot)
    _           -> standard_assignment(pilot)
}

-- mood inference: compiler tracks mood through control flow
-- If all paths through a task lead to .done, return type
-- can be annotated mood<.done> to make this explicit
task final_goodbye(pilot: Eishi) -> void mood<.muv_luv> { ... }
```

---

## SECTION 3: CONCURRENCY — FULL MODEL

### 3.1 XM3 {} — Parallel Racing Concurrency

xm3 {} runs multiple branches in parallel and commits the FIRST branch
that completes successfully. All other branches are aborted.
Named after the XM3 OS which processes pilot reflexes in parallel
and commits the first valid response.

```
-- Basic xm3: race two approaches
pilot result = xm3 {
    try_approach_alpha(target)
    ||
    try_approach_beta(target)
}

-- Three-way race
pilot best_route = xm3 {
    calculate_route_a(origin, dest)
    ||
    calculate_route_b(origin, dest)
    ||
    calculate_route_c(origin, dest)
}

-- With timeout: if no branch completes in time, err
pilot result = xm3[timeout: 500.milliseconds] {
    slow_scan()
    ||
    fast_scan()
}

-- xm3 with fallback: if ALL branches fail
pilot result = xm3 {
    primary_approach()
    ||
    secondary_approach()
} fallback {
    emergency_protocol()
}

-- Branches have access to their own scoped state
-- Shared state access requires BriefingRoom (mutex)
-- xm3 branches cannot mutate outer variables directly
-- Return type of xm3 = result<T, List<E>> where T is branch return type
```

### 3.2 Squadron Model — Structured Concurrency

```
-- sortie: spawn a concurrent thread
pilot mission = sortie[callsign: "Hawk-1"] {
    scan_sector("North")
}

-- debrief: wait for sortie result
pilot data = debrief mission

-- formation: run all, wait for ALL
formation {
    hawk_1: scan_sector("Alpha")
    hawk_2: scan_sector("Beta")
    hawk_3: scan_sector("Gamma")
} debrief as reports { ... }

-- formation first: run all, take FASTEST success
formation first {
    route_a: try_approach("vector-alpha")
    route_b: try_approach("vector-beta")
} debrief as winner { ... }

-- Comms: typed message channels
pilot (tx, rx) = Comms::open<BetaSighting>()
pilot (tx, rx) = Comms::buffered<Alert>(capacity: 32)
pilot (broadcast, r1, r2) = Comms::broadcast<Order>(receivers: 2)

-- BriefingRoom: mutex-guarded shared state
pilot map = BriefingRoom::new(ThreatMap::empty())
enter briefing map as m { m.mark(contact) }   -- exclusive write
observe briefing map as m { say m.count }     -- shared read

-- Wingman: actor model
wingman ThreatTracker {
    pilot threats: List<BetaSighting> = []
    on spotted(s: BetaSighting) { threats.push(s) }
    on report() -> List<BetaSighting> { give back threats.clone() }
}
pilot tracker = ThreatTracker::deploy()
tracker.spotted(contact)
pilot all = tracker.report()
```

---

## SECTION 4: BORROW CHECKER — FULL RULES

The borrow checker enforces memory safety without a garbage collector.
It runs as a separate pass after type checking, before code generation.

### 4.1 Ownership Rules

1. Every value has exactly ONE owner at any time.
2. When the owner goes out of scope, the value is dropped (freed).
3. Ownership can be transferred (moved) to a new owner.
4. After a move, the original binding is invalid.

```
pilot a = Eishi::new("Takeru")   -- a owns the Eishi
pilot b = a                       -- ownership MOVES to b
say a.name                        -- COMPILE ERROR: a is moved
-- Error (Meiya voice): "Shirogane. You gave this away. It no longer belongs to you."

-- Primitives are copied, not moved (they implement Copy)
pilot x = 42
pilot y = x    -- y is a copy, x still valid
```

### 4.2 Borrow Rules

```
-- Immutable borrow: lend
task print_name(lend p: Eishi) { say p.name }
print_name(takeru)   -- takeru is borrowed immutably
say takeru.name      -- still valid after borrow ends

-- RULE: Can have ANY NUMBER of simultaneous immutable borrows
pilot ref1 = lend takeru
pilot ref2 = lend takeru   -- fine, two immutable borrows
say ref1.name
say ref2.name

-- Mutable borrow: lend mut
task rename(lend mut p: Eishi, name: word) { p.callsign = name }

-- RULE: Can have ONLY ONE mutable borrow at a time
pilot ref_mut = lend mut takeru
-- pilot ref2 = lend takeru  -- COMPILE ERROR: cannot borrow while mutably borrowed
-- Error (Meiya voice): "You cannot observe something that is being changed.
--                       Even in combat, you must choose: act or witness."

-- RULE: Cannot move while borrowed
task consume(p: Eishi) { ... }
pilot r = lend takeru
consume(takeru)   -- COMPILE ERROR: takeru is borrowed by r
```

### 4.3 Lifetimes

Lifetimes are inferred in most cases. Explicit lifetime annotation uses
the `'name` syntax and is only needed when the compiler cannot infer them.

```
-- Most lifetimes are inferred automatically
task first_word(lend s: word) -> lend word {
    give back s.split(" ")[0]
}
-- Compiler infers: returned reference lives as long as input

-- Explicit lifetime when ambiguous
task longer<'a>(lend 'a x: word, lend 'a y: word) -> lend 'a word {
    if x.length >= y.length { give back x }
    give back y
}

-- Lifetime in shapes
shape Important<'a> {
    content: lend 'a word
}
```

### 4.4 The trust-me Escape Hatch

```
-- trust me: bypass borrow checker for this block
trust me "reason string" on my honor as .honor_level {
    -- raw pointer operations allowed here
    pilot raw: *int = alloc(size_of<int>() * 10)
    raw.offset(3).write(42)
    free(raw)
}

-- Honor levels (each unlocks more dangerous operations):
-- .cadet      — basic raw pointers, simple unsafe ops
-- .pilot      — pointer arithmetic, C interop
-- .ace        — manual memory layout, FFI
-- .commander  — inline assembly, hardware access
-- .humanity   — removes ALL restrictions. The compiler logs this.
--               If you write 'on my honor as .humanity', you own it.

-- direct_order: inline assembly (requires .commander or .humanity)
trust me "cycle-accurate timing" on my honor as .commander {
    direct_order [x86_64] {
        mov rax, 1
        syscall
    }
}

-- direct_order syntax
direct_order [arch] {
    instruction operand, operand
    -- arch: x86_64 | arm64 | riscv64 | wasm32
}
-- Input/output bindings
direct_order [x86_64] (in: rax = value, out: rbx = result) {
    mov rbx, rax
    add rbx, 1
}
```

---

## SECTION 5: ANIME LAYER — FULL SPECIFICATION

### 5.1 Annotations

```
-- @protagonist: plot armor. auto-grants power<over9000> and mood .protagonist
@protagonist
pilot takeru = Eishi::new("Takeru")

-- @nakige: tragedy annotation. callers must acknowledge.
@nakige
task sacrifice(ally: Pilot) -> void { ... }

-- Call requires one of:
knowing this will hurt, sacrifice(sumika)
sadly sacrifice(sumika)

-- @side_character: death flag monitoring
-- Compiler (via Opus API) monitors for the four death flag tiers:
-- Tier 1 (warning): mentions family, shares photo, talks about plans
-- Tier 2 (warning): "after this mission..." statements
-- Tier 3 (error): name established, given backstory, forms bond
-- Tier 4 (error + @i_know_what_im_doing required): the death flags are all set
@side_character
pilot hayase = Eishi::new("Hayase Mitsuki")

-- Override death flag error:
@i_know_what_im_doing("hayase is supposed to die here")
@side_character
pilot hayase = Eishi::new("Hayase")

-- @experiment: Yuuko's lab annotation. requires 'for science,' to call.
-- All calls logged to research.fklog automatically.
@experiment("XM3 reflex override — may cause dissociation")
task activate_xm3(lend mut p: Eishi) { ... }
for science, activate_xm3(takeru)

-- @classified: value is redacted from ALL output
-- Compiler errors, logs, stack traces, debug symbols — all show [REDACTED]
-- Requires --clearance=TOP_SECRET flag to unredact
@classified("Operation Ouka — council eyes only")
pilot operation_target: word = "Sadogashima"

-- @rival: mutual power coefficient boost based on shared missions
@rival(meiya)
pilot takeru = Eishi::new("Takeru")
-- rivalry_coefficient = 1.0 + shared_missions * 0.05
-- Both pilots get the boost. It is mutual. That is the point.

-- @fixed_fate: outcome is certain. removes probability. removes maybe.
-- A task annotated @fixed_fate cannot return nobody or err.
@fixed_fate
task the_confrontation(takeru: Eishi, meiya: Eishi) -> route {
    route TrueRoute
}

-- @season_finale: ONE PER CODEBASE. MAXIMUM.
-- Uncaps all power levels. Pre-acknowledges all @nakige calls.
-- Silences all death flag warnings. Applies all optimizations.
-- Two @season_finale in one codebase = compile error:
--   "There can only be one final episode. Choose."
@season_finale
task alternative() { ... }
```

### 5.2 Foreshadowing System

```
-- foreshadow: mark a variable as a narrative promise
foreshadow pilot the_sword = get_from_storage("type-94")
-- Compiler tracks this. It MUST be paid off.

-- payoff: resolve the foreshadowing
-- Must occur in the same task or a task reachable from it
payoff the_sword
-- Error if foreshadow has no payoff before scope ends:
-- Error (Takeru voice, Timeline 3): "You set this up. You didn't finish it.
--   I've watched this happen four times now. Please. Pay it off."

-- foreshadow works with any expression
foreshadow pilot clue = "the culprit wore red"
foreshadow pilot weakness = calculate_beta_weakness(tier)

-- Multiple foreshadows can be paid off in batch
payoff { the_sword, clue, weakness }
```

### 5.3 Route System

```
-- route: visual novel outcome type
-- Declare routes a task can return
task confess(courage: num) -> route {
    if courage >= 100 { route TrueRoute }
    else if courage >= 50 { route GoodEnd }
    else { route BadEnd }
}

-- Built-in route names: TrueRoute, GoodEnd, NormalEnd, BadEnd
-- Custom routes: any identifier

-- Callers must handle all possible routes
check route confess(my_courage) {
    TrueRoute -> say "She said yes."
    GoodEnd   -> say "It went well."
    BadEnd    -> say "..."
    _         -> say "unknown outcome"
}

-- Route-locked variables: only valid on specific routes
pilot confession_result = confess(courage)
only on TrueRoute from confession_result {
    pilot ring = get_ring()   -- ring only exists on TrueRoute
    propose(ring)
}

-- @fixed_fate forces a specific route
@fixed_fate
task the_final_battle() -> route {
    route TrueRoute   -- this always returns TrueRoute. fate decided.
}
```

### 5.4 Operator System

```
-- PLUS ULTRA: exponential power scaling (emotion drives it)
pilot damage = base_power PLUS ULTRA emotion_intensity
-- Compiles to: base_power * (1.0 + emotion_intensity * emotion_intensity)

-- NAKAMA: friendship synergy (working together beats working alone)
pilot combined = takeru_power NAKAMA meiya_power
-- Compiles to: takeru_power + meiya_power + (takeru_power * meiya_power * 0.1)

-- FINAL FORM: ultimate squaring
pilot final = base FINAL FORM
-- Compiles to: base * base
-- Also: compiler prints a 5-second pause message at build time:
--   "...FINAL FORM activating. Please stand by."

-- TSUNDERE: inverse operator
pilot actual_feeling = tsun_response TSUNDERE
-- For bool: compiles to !(tsun_response)
-- For num:  compiles to -(tsun_response)
-- "It's not like I wanted this value to be true or anything."

-- Operators can chain
pilot result = base PLUS ULTRA emotion NAKAMA ally_power
-- Left-associative: ((base PLUS ULTRA emotion) NAKAMA ally_power)
```

### 5.5 deus_ex_machina Block

```
-- deus_ex_machina: bypass ALL safety checks
-- Requires a dramatic monologue of at least 20 words.
-- Logged separately to freak-audit-miracles.
-- More than 3 in a codebase triggers warning.
-- More than 10 triggers error.

deus_ex_machina "I know this is impossible and I know the odds are zero but
                 I have come too far and lost too much to accept that this
                 ends here, so it will not" {
    -- ALL borrow checker rules suspended
    -- ALL power level requirements waived
    -- ALL probability constraints removed
    -- ALL type safety suspended (with great power...)
    perform_the_impossible()
}

-- The monologue is NOT a comment. It is required. The compiler counts words.
-- Less than 20 words: compile error.
-- Error (Yuuko voice): "That wasn't a speech. That was a sentence.
--   If you're going to do something impossible, at least commit to it."
```

### 5.6 Training Arc Loop (Full Spec)

```
training arc until condition max N sessions {
    body
}

-- Compiles to:
-- int64_t __arc_sessions = 0;
-- while (!(condition) && __arc_sessions < N) {
--     body;
--     __arc_sessions++;
-- }

-- If condition is never met after N sessions, execution continues normally
-- The compiler warns if static analysis shows the condition can never be met:
-- Warning (Takeru voice): "I've done this training arc. It doesn't work if
--   the condition is structurally unreachable. Trust me."

-- with growth: training arc variant that verifies progress each session
training arc until power >= 9000 max 100 sessions with growth {
    power += practice()
}
-- Compiler verifies body mutates the variable in the condition.
-- If it doesn't: compile error. You must actually train.
```

### 5.7 Isekai and Eventually Blocks

```
-- isekai: the protagonist dies and is reborn in another world (scope reset)
-- Creates a fresh scope with no access to outer variables
-- Outer state after isekai block is the state it was before + explicit exports
isekai {
    -- this scope has no access to outer variables
    -- start fresh. new world. new rules.
    pilot new_power = 9999
    pilot cheat_skill = "system administrator"
    ...
} bringing back { new_power, cheat_skill }
-- After the isekai block: new_power and cheat_skill exist in outer scope

-- Use case: complete isolation for a segment of logic
-- The compiler cannot see into an isekai block from outside
-- Useful for: sandboxed computation, testing extreme logic paths,
--             literally starting over without side effects

-- eventually: deferred execution block
-- Body runs when current scope ends, regardless of how it ends
eventually {
    cleanup_resources()
    log_mission_complete()
}
-- Similar to defer in other languages but named better
-- Multiple eventually blocks run in reverse order (LIFO)
-- eventually runs even if a panic occurs (before unwind)
-- eventually runs even if give back is hit

-- eventually with condition
eventually if mission_failed {
    sound_retreat()
}
```

---

## SECTION 6: MODULE SYSTEM AND HANGAR

### 6.1 Module System

```
-- File = module. Directory = module with same name as directory.
-- 'launch' makes things public. Without launch: private to file.

launch task my_function() { ... }
launch shape MyType { ... }
launch use muvluv::BETA::{Tier, Hive}   -- re-export

-- Imports
use tactics::{engage, Formation}
use tactics::*
use muvluv::{TSF, Eishi}
use cosmo::OrbitalStrike as Strike
use[feature="orbital"] cosmo::GBomb
```

### 6.2 hangar.toml

```toml
[unit]
name        = "my-project"
version     = "1.0.0"
author      = "Shirogane Takeru"
entry       = "src/main.fk"
edition     = "alternative-4"

[build]
mode        = "shonen_jump"
target      = "x86_64-linux"
voice       = "yuuko"

[dependencies]
muvluv      = "2.0.0"
std-tactics = "^1.4"

[profile.final_form]
optimize    = "maximum"
drama_pause = true
```

### 6.3 Hangar CLI

```
freak hangar init          -- create project
freak hangar install       -- install all deps
freak hangar add [unit]    -- add dependency
freak hangar remove [unit] -- remove dependency
freak hangar update        -- update all deps
freak hangar launch        -- publish to registry
freak hangar search [q]    -- search registry
freak hangar status        -- show installed units + power levels
freak hangar clean         -- clear cache
```

---

## SECTION 7: STD LIBRARY — COMPLETE REFERENCE

### 7.1 Prelude (always available, no import needed)

Types: num, int, uint, tiny, float, float32, big, word, bool, char, void
Compound: maybe<T>, result<T,E>, List<T>, Map<K,V>
Doctrines: Displayable, Comparable, Equatable, Cloneable, Hashable,
           Callable, MutCallable, OneShot, Add, Sub, Mul, Div, Neg, Eq, Ord
Functions: say, ask, panic
Constants: num::PI, num::E, num::INF, num::NAN, num::OVER9000,
           int::MAX, int::MIN

### 7.2 std::word

```
"hello".length          -- character count (not bytes)
"hello".bytes           -- byte length
"hello".slice(0, 3)     -- character-indexed slice
"hello".contains("ell")
"hello".starts_with("he") / .ends_with("lo")
"a,b,c".split(",")      -- List<word>
"  hi  ".trim() / .trim_start() / .trim_end()
"hello".to_upper() / .to_lower()
"hello".replace("l", "r")
"42".to_int()           -- maybe<int>
"3.14".to_num()         -- maybe<num>
"hello".chars()         -- List<char>
"hello".bytes_raw()     -- List<tiny>

-- WordBuilder for mutable construction
pilot b = WordBuilder::new()
b.push("Mission: ")
b.push(name)
pilot result: word = b.build()
```

### 7.3 std::num

```
42.abs() / 42.sign()
x.clamp(lo, hi)
x.pow(exp) / x.sqrt() / x.cbrt()
x.floor() / x.ceil() / x.round()
x.to_word() / x.to_word_fmt(decimals: 2)
x.is_nan() / x.is_inf() / x.is_finite()
int::checked_add(a, b)   -- maybe<int>, overflow-safe
```

### 7.4 std::collections

```
-- List<T>
List::new() / List::with_capacity(n)
list.push(val) / list.pop() / list.insert(i, val)
list.get(i) / list[i] / list.first() / list.last()
list.length / list.empty() / list.clear()
list.contains(val) / list.index_of(val)
list.sort() / list.sort_by(key, dir)
list.reverse() / list.shuffle() / list.dedup()
list.slice(from, to) / list.take(n) / list.skip(n) / list.chunk(n)
list.join(sep)   -- word, T: Displayable

-- Map<K, V>
Map::new() / Map::from(pairs)
map.get(key) / map.get_or(key, default)
map.set(key, val) / map.remove(key)
map.keys() / map.values() / map.pairs()
map.merge(other) / map.merge_with(other, resolve)

-- Set<T>
Set::new()
set.add(val) / set.remove(val) / set.contains(val)
set.union(other) / set.intersect(other) / set.difference(other)
set.subset_of(other)

-- Lineup<T> (FIFO Queue)
Lineup::new()
lineup.enqueue(val) / lineup.dequeue() / lineup.peek()
```

### 7.5 std::iter (lazy, all collections)

```
.filter(|x| => bool)
.map(|x| => U)
.flat_map(|x| => List<U>)
.fold(init, |acc, x| => acc)
.each(|x| => void)
.each_index(|i, x| => void)
.find(|x| => bool) / .position(|x| => bool)
.any(|x| => bool) / .all(|x| => bool)
.take(n) / .skip(n) / .take_while(pred) / .skip_while(pred)
.zip(other) / .enumerate()
.collect() / .collect_map() / .collect_set()
.count() / .sum() / .min() / .max()
```

### 7.6 std::io

```
use std::io::{ask, say_err, say_fmt, stdout, stdin}

say_err(msg)             -- stderr
ask(prompt)              -- read stdin line (also in prelude)
ask_secret(prompt)       -- no-echo input
stdout() / stderr()      -- raw Writer handles
stdin()                  -- raw Reader
```

### 7.7 std::fs

```
use std::fs::{read, write, exists, dir}

fs::read(path)           -- result<word, word>
fs::read_bytes(path)     -- result<List<tiny>, word>
fs::write(path, content) -- result<void, word>
fs::append(path, content)
fs::copy(from, to) / fs::move(from, to) / fs::delete(path)
fs::exists(path) / fs::is_file(path) / fs::is_dir(path)
dir::list(path) / dir::create(path) / dir::create_all(path) / dir::delete(path)
```

### 7.8 std::net

```
use std::net::{TcpSocket, UdpSocket, Address}

TcpSocket::connect(addr)  -- promise<result<TcpSocket, NetError>>
TcpSocket::listen(addr)   -- result<TcpListener, NetError>
socket.send(bytes)        -- promise<result<void, NetError>>
socket.receive(max)       -- promise<result<List<tiny>, NetError>>
```

### 7.9 std::time

```
use std::time::{now, sleep, Duration, Instant}

time::now()              -- Instant
time::unix()             -- uint (epoch seconds)
time::sleep(duration)    -- blocks current sortie
start.elapsed()          -- Duration
start.since(other)       -- Duration

-- Duration literals
500.milliseconds / 2.seconds / 1.minute / 1.hour
```

### 7.10 std::math

```
use std::math::{sin, cos, sqrt, log, exp, gcd, simd}

math::sin(x) / math::cos(x) / math::tan(x)
math::asin(x) / math::acos(x) / math::atan(x) / math::atan2(y, x)
math::log(x, base) / math::ln(x) / math::exp(x)
math::gcd(a, b) / math::lcm(a, b)
math::to_rad(degrees) / math::to_deg(radians)
math::simd::dot(a, b) / math::simd::map(arr, f)
```

### 7.11 std::random

```
use std::random::{rand, rand_range, pick, secure, seed}

random::rand()                  -- num in [0, 1)
random::rand_range(lo, hi)      -- num in [lo, hi)
random::rand_int_range(lo, hi)  -- int in [lo, hi)
random::pick(list)              -- maybe<T>
random::secure()                -- SecureRng (OS entropy)
random::seed(n)                 -- seeded Rng (reproducible)
```

### 7.12 std::process

```
use std::process::{run, spawn, pid, exit, env_var, args}

process::run(cmd, args)         -- result<Output, word>
process::spawn(cmd, args)       -- result<Process, word>
process::pid()                  -- uint
process::exit(code)             -- void, no return
process::env_var(name)          -- maybe<word>
process::set_env(name, val)
process::args()                 -- List<word>

-- Output shape: .stdout .stderr .exit_code .success
-- Process shape: .pid .wait() .kill()
```

### 7.13 std::thread

```
use std::thread::{spawn, current_id, yield_now, available_parallelism}

thread::spawn(f: OneShot)       -- ThreadHandle
thread::current_id()            -- uint
thread::yield_now()             -- hint to scheduler
thread::available_parallelism() -- uint (logical cores)

-- ThreadHandle: .join() .id() .is_finished()

-- Atomic types (lock-free)
Atomic<int>:  .load() .store(val) .fetch_add(n) .compare_swap(old, new)
Atomic<bool>: .load() .store(val) .flip()
```

### 7.14 std::bytes

```
use std::bytes::ByteBuffer

ByteBuffer::new() / ByteBuffer::from(data: List<tiny>)
buf.write_byte(b) / buf.write_int(n) / buf.write_int_be(n)
buf.write_word(s) / buf.write_bytes(data)
buf.read_byte()   -- maybe<tiny>
buf.read_int()    -- maybe<int>
buf.read_word(len) -- maybe<word>
buf.seek(pos) / buf.position() / buf.length()
buf.to_list()     -- List<tiny>
buf.to_word()     -- result<word, word>
```

### 7.15 std::anime (always available)

```
-- mood type and arithmetic (see Section 2.4)
-- power<N> type (see Section 2.1)
-- prob[lo..hi] type (see Section 2.2)
-- route type (see Section 5.3)

anime::power_check(current, required)  -- bool
anime::route_reachable(r)              -- bool
```

### 7.16 std::narrative

```
use std::narrative::{DeathFlag, ForeshadowLog}

narrative::death_flags()       -- List<DeathFlag> (empty in release builds)
narrative::foreshadow_log()    -- ForeshadowLog
log.unpaid.length              -- should be 0 at program end
```

### 7.17 std::test (dev only, stripped in release)

```
test "description" { ... }
test "name" @skip
test "name" @only
test "name" @nakige

expect X to be Y
expect X to not be Y
expect X to be greater than Y / less than Y / at least Y / at most Y
expect X to panic
expect X to match route Y

-- Output includes vibes rating:
-- vibes: MONO_NO_AWARE  (almost there. so close.)
```

---

## SECTION 8: FULL LEXER SPECIFICATION

### 8.1 All Token Types

```python
class TokenType(Enum):
    # Literals
    INT_LIT / FLOAT_LIT / STRING_LIT / BOOL_LIT

    # Core keywords
    PILOT / FIXED / TASK / GIVE_BACK / SAY / SHAPE / IMPL / DOCTRINE
    LAUNCH / USE / AS / IN / LEND / MUT / MOVE / COPY / TRUST_ME
    GIVE_BACK / BREAK / CONTINUE

    # Control flow
    IF / ELSE / WHEN / REPEAT / TIMES / UNTIL / DONE / FOR_KW / EACH

    # Error handling
    CHECK / RESULT_KW / GOT / NOBODY / SOME / OK / ERR / OR_ELSE

    # Concurrency
    XM3 / SORTIE / DEBRIEF / FORMATION / FIRST_KW / ENTER / BRIEFING
    OBSERVE / WINGMAN / ON_KW / COMMS

    # Anime keywords
    TRAINING_ARC / SESSIONS / MAX / FORESHADOW / PAYOFF / ROUTE_KW
    KNOWING / SADLY / FOR_SCIENCE / ON_MY_HONOR / ONLY_ON / BRINGING_BACK
    ISEKAI / EVENTUALLY / DEUS_EX_MACHINA / DECLARE_WAS / PROB_WHEN

    # Operators
    PLUS / MINUS / STAR / SLASH / PERCENT / STAR_STAR
    EQ_EQ / BANG_EQ / LT / GT / LT_EQ / GT_EQ
    AND / OR / NOT / PIPE / QUESTION / BANG
    ARROW / FAT_ARROW / PLUS_ULTRA / NAKAMA / FINAL_FORM / TSUNDERE
    DOUBLE_PIPE   # || in xm3 blocks

    # Delimiters
    LBRACE / RBRACE / LPAREN / RPAREN / LBRACKET / RBRACKET
    COMMA / COLON / SEMICOLON / DOT / COLON_COLON / PIPE_SINGLE / AT

    # Assignment
    EQ / PLUS_EQ / MINUS_EQ / STAR_EQ / SLASH_EQ

    # Special
    IDENT / UNDERSCORE / NEWLINE / EOF
```

### 8.2 Multi-Word Tokens (lex greedily)

```
give back / or else / trust me / for each / training arc
on my honor as / knowing this will hurt / for science
PLUS ULTRA / FINAL FORM / only on / bringing back
deus_ex_machina / declare was / prob when
```

### 8.3 Special Lexer Notes

- `--` starts a line comment, skip to end of line
- `done` closes blocks (synonym for `}`)
- `||` in xm3 blocks is branch separator (not OR)
- `@` followed by IDENT is an annotation
- `'` followed by IDENT is a lifetime annotation
- `prob[lo..hi]` lexes as: IDENT("prob") LBRACKET FLOAT DOT_DOT FLOAT RBRACKET
- Number suffixes: `42u` → uint, `3.14f` → float, `42t` → tiny, `999b` → big

---

## SECTION 9: FULL PARSER — AST NODES

All nodes from freak-lite-bible.md Section 7.1, plus:

```python
@dataclass
class PowerType:             # power<N>
    level: Expr              # can be numeric literal or 'over9000'

@dataclass
class ProbType:              # prob[lo..hi]
    lo: Expr
    hi: Expr

@dataclass
class CausalityType:         # causality<T>
    inner: TypeExpr

@dataclass
class MoodExpr:              # .chill, .hype, etc.
    variant: str

@dataclass
class MoodAdd:               # mood1 + mood2
    left: MoodExpr
    right: MoodExpr

@dataclass
class RouteDecl:             # route RouteName inside task body
    name: str

@dataclass
class RouteCheck:            # check route expr { Name -> ... }
    expr: Expr
    arms: List[Tuple[str, Block]]

@dataclass
class OnlyOnRoute:           # only on RouteName from expr { }
    route: str
    source: Expr
    body: Block

@dataclass
class XM3Block:              # xm3 { branch || branch }
    branches: List[Block]
    timeout: Optional[Expr]
    fallback: Optional[Block]

@dataclass
class Foreshadow:            # foreshadow pilot x = expr
    decl: PilotDecl

@dataclass
class Payoff:                # payoff x
    names: List[str]         # payoff { a, b, c } or payoff a

@dataclass
class DeusExMachina:         # deus_ex_machina "monologue" { }
    monologue: str           # must be >= 20 words
    body: Block

@dataclass
class TrainingArcWith:       # training arc ... with growth
    condition: Expr
    max_sessions: Expr
    body: Block
    growth_var: str          # variable that must change each session

@dataclass
class Isekai:                # isekai { } bringing back { vars }
    body: Block
    exports: List[str]

@dataclass
class Eventually:            # eventually { } / eventually if cond { }
    body: Block
    condition: Optional[Expr]

@dataclass
class ProbGate:              # prob[0.3] chance { }
    probability: Expr
    body: Block

@dataclass
class ProbWhen:              # prob_when expr { >= 0.9 -> ... }
    subject: Expr
    arms: List[Tuple[str, Expr, Block]]

@dataclass
class CausalityWrite:        # causality_val.write(expr)
    target: Expr
    value: Expr

@dataclass
class DeclareWas:            # declare x was val in timeline "name"
    variable: str
    value: Expr
    timeline: str

@dataclass
class DirectOrder:           # direct_order [arch] (bindings) { asm }
    arch: str
    inputs: List[Tuple[str, str, Expr]]    # (reg, name, expr)
    outputs: List[Tuple[str, str]]          # (reg, name)
    body: str                               # raw assembly text
```

---

## SECTION 10: TYPE CHECKER — FULL RULES

### 10.1 All Lite checks (from freak-lite-bible.md Section 8) plus:

- power<N> arithmetic: verify N at call sites, propagate through generics
- prob[lo..hi] range tracking: verify range doesn't exceed [0.0..1.0]
- causality<T> writes: verify all registered timelines are notified
- mood compound: verify both operands are mood type, compute result mood
- route coverage: all possible routes handled in check route blocks
- only on route: variable only accessible inside matching route block
- foreshadow/payoff: every foreshadow must have a reachable payoff
- deus_ex_machina monologue word count: must be >= 20
- @season_finale: exactly one per codebase
- @nakige: caller must use knowing/sadly prefix
- @experiment: caller must use for science prefix
- @classified: variable name/type redacted in all error output
- isekai export list: only listed variables escape the isekai block
- eventually: guaranteed execution tracked in control flow graph
- training arc with growth: verify condition variable mutated in body
- declare was: verify timeline name is registered causality timeline

### 10.2 Borrow Checker Pass (after type checker)

1. Build ownership graph: every value has exactly one owner
2. Track borrows: immutable borrows counted, only one mutable allowed
3. Verify lifetimes: no reference outlives its referent
4. trust-me blocks: suspended within block, re-engaged after
5. Report errors with Meiya voice

---

## SECTION 11: CODE GENERATION NOTES (Full Compiler)

The full compiler targets native code via LLVM IR or direct assembly,
not C. Key differences from FREAK Lite:

- power<N> types: completely erased at codegen, zero runtime overhead
- prob[lo..hi]: compiles to double + bounds metadata (stripped in release)
- causality<T>: compiles to value + broadcast function table
- mood type: compiles to uint8_t enum, compound arithmetic is integer ops
- xm3 {}: LLVM coroutines or OS threads, first-result-wins via atomics
- deus_ex_machina: pragma optimize("O3") + disable sanitizers for block
- isekai {}: fresh stack frame, only exports pass through
- eventually {}: RAII destructor pattern or longjmp cleanup chain
- training arc with growth: loop + static analysis at compile time
- @classified: debug symbols omitted, variable renamed to __classified_N

---

## SECTION 12: BUILD MODES

```
slice_of_life   -- debug mode. full symbols. no optimization. death flags warn only.
mecha           -- release mode. O2. strip debug.
shonen_jump     -- progressive JIT. narrative PGO. frequency-based optimization.
final_form      -- maximum optimization. drama pause at compile start.
                   "...preparing final form. this may take a moment."
alternative     -- special mode. enables ALL anime features. full causality.
                   reserved for programs that are actually the final version.
```

---

## SECTION 13: COMPILER CLI — FULL COMMANDS

```
freak run file.fk             -- compile and run
freak build file.fk           -- compile to binary
freak check file.fk           -- type check + borrow check only
freak test                    -- run all test blocks
freak vibe file.fk            -- Opus vibe analysis

freak hangar [command]        -- package manager (see Section 6.3)

freak audit-science           -- list all 'for science' calls
freak audit-trust             -- list all trust-me blocks with honor levels
freak audit-miracles          -- list all deus_ex_machina blocks
freak foreshadow-audit        -- list all foreshadow/payoff pairs
freak timeline-diff           -- show causality divergence between timelines

--voice=[character]           -- set error voice (yuuko/meiya/sumika/mana/sagiri/kasumi)
--clearance=TOP_SECRET        -- unredact @classified variables
--keep-ir                     -- keep intermediate representation files
--build-mode=[mode]           -- override hangar.toml build mode
--emit-c                      -- emit C instead of native (Lite compatibility)
```

---

## SECTION 14: ERROR VOICE CAST

| Error Type              | Character | Personality                              |
|-------------------------|-----------|------------------------------------------|
| Borrow/lifetime         | Meiya     | Formal, disappointed, believes in you    |
| Type mismatch           | Yuuko     | Sarcastic, technically precise           |
| Power level             | Sagiri    | Blunt, no encouragement whatsoever       |
| Route handling          | Sumika    | Gentle, devastating subtext              |
| @nakige missing prefix  | Kasumi    | Quiet, clinical, saddest                 |
| Unused foreshadowing    | Takeru T3 | Tired, seen this 4 times                 |
| deus_ex overuse         | Yuuko     | Scolding ("Even I have limits")          |
| Syntax error            | Mana      | Direct, zero patience                    |
| death flag (tier 3-4)   | Hayase    | Doesn't know. That's the worst part.     |
| isekai scope violation  | Sumika    | "You can't bring that with you."         |
| causality divergence    | 00-Unit   | No emotion. Just facts. Somehow worse.   |

---

## SECTION 15: COMPLETE SYNTAX CHEATSHEET

```
-- Variables
pilot x = value
fixed pilot x = value      -- immutable
pilot x: Type = value

-- Functions
task name(p: T) -> R { body }
task name(p: T) -> R
    body
done
task name(p: T) => expr

-- Types
num int uint tiny float float32 big word bool char void
[T; N]  (A, B)  *T  *mut T
maybe<T>  result<T,E>  List<T>  Map<K,V>  Set<T>  Lineup<T>
power<N>  prob[lo..hi]  causality<T>  mood

-- Values
42  3.14  "string {interp}"  true/yes/hai  false/no/iie
some(x)  nobody  ok(x)  err(x)  [1,2,3]  {"k":v}  (a,b)

-- Control
if cond { } else { }
when x { val -> expr   _ -> expr }
for each item in list { }
repeat N times { }
repeat until cond { }
training arc until cond max N sessions { }
training arc until cond max N sessions with growth { }

-- Probability
prob[0.3] chance { }
prob_when x { >= 0.9 -> ...  _ -> ... }

-- Error handling
expr?
check val { got x -> ...  nobody -> ... }
check result val { ok(x) -> ...  err(e) -> ... }
check route val { TrueRoute -> ...  BadEnd -> ... }
val or else default

-- Closures
|x: T| => expr
|x: T| { body }
copy |x| => expr
move |x| { body }
mut |x| { body }

-- Concurrency (XM3)
xm3 { branch || branch }
xm3[timeout: 500.milliseconds] { branch || branch } fallback { }

-- Concurrency (Squadron)
sortie[callsign: "name"] { }
debrief handle
formation { name: task()  name: task() } debrief as r { }
formation first { ... } debrief as winner { }
Comms::open<T>() / Comms::buffered<T>(capacity: n)
BriefingRoom::new(val)
enter briefing x as v { }
observe briefing x as v { }
wingman Name { on msg(...) { } }

-- Operators
+  -  *  /  %  **
==  !=  <  >  <=  >=
and  or  not
|>  ?  !  ->  =>  ||
PLUS ULTRA / NAKAMA / FINAL FORM / TSUNDERE

-- Anime annotations
@protagonist  @nakige  @side_character  @experiment  @fixed_fate
@classified  @rival(other)  @season_finale  @i_know_what_im_doing("reason")

-- Anime call prefixes
knowing this will hurt, call()
sadly call()
for science, call()

-- Anime blocks
foreshadow pilot x = val
payoff x  /  payoff { x, y, z }
trust me "msg" on my honor as .level { }
direct_order [arch] (in: reg=val, out: reg=name) { asm }
deus_ex_machina "20+ word monologue" { }
isekai { } bringing back { vars }
eventually { }
eventually if cond { }

-- Causality
causality::new(val)
causality::register("timeline-name")
val.write(x)  /  val.read()  /  val.read_from(timeline)
declare val was x in timeline "name"

-- Modules
use module::{Thing}
use module::*
launch task ...
launch shape ...

-- Route system
task f() -> route { route TrueRoute }
only on TrueRoute from result { }
```

---

## END OF FREAK FULL BIBLE

This document supersedes freak-lite-bible.md for full compiler implementation.
For FREAK Lite (Python → C transpiler) use freak-lite-bible.md —
it is a strict subset of this document.

The full compiler is written in FREAK itself.
When FREAK compiles this compiler, the language is complete.
Until then: build, iterate, ship.

諦めるな。コードを書け。
Don't give up. Write the code.
