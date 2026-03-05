# freak-ui — Official UI Framework Plan
## Cross-platform immediate mode UI, built from scratch on OS APIs
### Style: Immediate Mode | Target: Windows + Mac + Linux | Status: Planning

---

## WHAT YOU ARE BUILDING

freak-ui is FREAK's official UI framework. It is split into two layers:

**std::ui** — ships with the compiler. Thin abstraction over the OS window
and input system. Just enough to open a window, get input events, and draw
pixels. No widgets. No layout. Just the floor.

**freak-ui (Hangar package)** — the full framework. Built on top of std::ui.
Widgets, layout, theming, the calculator example. This is what people actually use.

The design philosophy: **one task per frame, describe what you want, get it drawn.**
No widget trees. No callbacks. No retained state. Just call the widget functions
in order and the frame renders.

---

## ARCHITECTURE OVERVIEW

```
Your FREAK app
     │
     ▼
freak-ui (Hangar)          ← widgets, layout, theming, input handling
     │
     ▼
std::ui                    ← window, events, raw draw calls, pixel buffer
     │
     ├── Windows: Win32 API (CreateWindowEx, GDI/Direct2D)
     ├── macOS:   Cocoa / CoreGraphics (via Objective-C bridge)
     └── Linux:   X11 or Wayland (via xlib or wayland-client)
```

---

## LAYER 1: std::ui
### The OS abstraction. Ships with compiler. No widgets.

### What it does:
- Creates and manages a native OS window
- Delivers input events (mouse, keyboard, resize, close)
- Exposes a pixel buffer OR a 2D draw command list
- Handles the platform event loop

### API:

```
use std::ui::{Window, Canvas, Event, Key, MouseButton}

-- Open a window
pilot win = Window::open(WindowConfig {
    title:  "My App",
    width:  800,
    height: 600,
    resizable: true,
})

-- Main loop
win.run(|canvas, events| {
    -- events: List<Event> for this frame
    -- canvas: draw target for this frame
    -- Return false to quit

    for each event in events {
        when event {
            Event::Quit          -> give back false
            Event::Key { key, pressed } -> handle_key(key, pressed)
            Event::Mouse { x, y, button, pressed } -> handle_mouse(x, y)
            Event::Resize { w, h } -> handle_resize(w, h)
            _ -> {}
        }
    }

    -- Draw directly to canvas
    canvas.clear(Color::rgb(20, 20, 30))
    canvas.fill_rect(Rect { x: 10, y: 10, w: 100, h: 50 }, Color::RED)
    canvas.draw_text("Hello", Vec2 { x: 10, y: 70 }, font, Color::WHITE)

    give back true   -- continue running
})
```

### std::ui Types:

```
-- Window configuration
shape WindowConfig {
    title:     word
    width:     uint
    height:    uint
    resizable: bool       -- default true
    vsync:     bool       -- default true
    icon:      maybe<word> -- path to icon file
}

-- Canvas: draw target for current frame
-- All draw calls are queued and flushed at end of frame
impl Canvas {
    task clear(self, color: Color)
    task fill_rect(self, rect: Rect, color: Color)
    task stroke_rect(self, rect: Rect, color: Color, thickness: num)
    task fill_circle(self, center: Vec2, radius: num, color: Color)
    task stroke_circle(self, center: Vec2, radius: num, color: Color, thickness: num)
    task fill_path(self, points: List<Vec2>, color: Color)
    task draw_line(self, from: Vec2, to: Vec2, color: Color, thickness: num)
    task draw_text(self, text: word, pos: Vec2, font: Font, color: Color)
    task draw_image(self, image: Image, dest: Rect)
    task clip(self, rect: Rect)          -- clip drawing to rect
    task unclip(self)                    -- remove clip
    task size(self) -> Vec2              -- canvas dimensions
}

-- Primitive types
shape Vec2  { x: num, y: num }
shape Rect  { x: num, y: num, w: num, h: num }
shape Color { r: tiny, g: tiny, b: tiny, a: tiny }

impl Color {
    task rgb(r: tiny, g: tiny, b: tiny) -> Color
    task rgba(r: tiny, g: tiny, b: tiny, a: tiny) -> Color
    task hex(code: word) -> Color     -- "#FF2D78"
    task lerp(self, other: Color, t: num) -> Color

    -- Named colors
    Color::RED / Color::GREEN / Color::BLUE
    Color::WHITE / Color::BLACK / Color::TRANSPARENT
}

-- Font handle
shape Font {
    family: word
    size:   num
    bold:   bool
    italic: bool
}

impl Font {
    task load(family: word, size: num) -> result<Font, word>
    task measure(self, text: word) -> Vec2   -- text dimensions
}

-- Image handle
shape Image {
    width:  uint
    height: uint
}

impl Image {
    task load(path: word) -> result<Image, word>
    task from_bytes(data: List<tiny>, w: uint, h: uint) -> result<Image, word>
}

-- Input events
route Event {
    Quit
    Key      { key: Key, pressed: bool, repeat: bool }
    Char     { character: char }
    Mouse    { x: num, y: num, button: maybe<MouseButton>, pressed: bool }
    Scroll   { x: num, y: num, delta_x: num, delta_y: num }
    Resize   { width: uint, height: uint }
    Focus    { gained: bool }
    FileDrop { paths: List<word> }
}

-- Key enum (common keys)
route Key {
    A through Z / F1 through F12
    Up / Down / Left / Right
    Enter / Escape / Space / Tab / Backspace / Delete
    Shift / Ctrl / Alt / Super
    Num0 through Num9
    -- ... full key list
}

route MouseButton { Left / Right / Middle / X1 / X2 }
```

### Platform Implementation Notes:

```
-- Windows: Win32
-- Window creation: CreateWindowEx + WNDCLASSEX
-- Event loop: GetMessage / TranslateMessage / DispatchMessage
-- Drawing: GDI for text/simple shapes, Direct2D for hardware acceleration
-- Build: link against user32.lib, gdi32.lib, d2d1.lib

-- macOS: Cocoa via C bridge
-- Window: NSWindow + NSView subclass
-- Event loop: NSApplication run loop
-- Drawing: CoreGraphics CGContext
-- Requires: Objective-C bridge in trust-me blocks
-- Build: link against Cocoa.framework, CoreGraphics.framework

-- Linux: X11 (primary) + Wayland (optional)
-- Window: XCreateWindow
-- Event loop: XNextEvent
-- Drawing: XCB for drawing, Cairo for 2D graphics
-- Build: link against libX11, libcairo

-- Abstraction: each platform provides the same internal C interface:
--   freak_ui_create_window(config) -> handle
--   freak_ui_poll_events(handle) -> events
--   freak_ui_begin_frame(handle) -> canvas_handle
--   freak_ui_end_frame(handle)
--   freak_ui_destroy_window(handle)
-- The FREAK layer calls these. Platform code implements them.
```

---

## LAYER 2: freak-ui (Hangar Package)
### The full widget framework. Built on std::ui.

### Design Principles:

1. **Immediate mode**: call widget functions each frame, get results back
2. **No IDs**: widgets are identified by their call order (like Dear ImGui)
3. **Layout flows top to bottom by default**, with explicit horizontal groups
4. **State lives in your code**, not the framework
5. **Theming is a first-class FREAK concept** — the theme has a mood

### Core Loop Pattern:

```
use freak_ui::{UI, button, label, input, row, column, Theme}

pilot display = "0"
pilot ui = UI::new(win, Theme::default())

win.run(|canvas, events| {
    ui.begin_frame(canvas, events)

    -- widgets are just function calls
    label("Calculator", style: .heading)

    label(display, style: .display)

    row {
        if button("7") { append("7") }
        if button("8") { append("8") }
        if button("9") { append("9") }
        if button("÷", style: .operator) { set_op(Op::Div) }
    }
    row {
        if button("4") { append("4") }
        if button("5") { append("5") }
        if button("6") { append("6") }
        if button("×", style: .operator) { set_op(Op::Mul) }
    }
    row {
        if button("1") { append("1") }
        if button("2") { append("2") }
        if button("3") { append("3") }
        if button("−", style: .operator) { set_op(Op::Sub) }
    }
    row {
        if button("0", width: .fill) { append("0") }
        if button("=", style: .equals) { calculate() }
        if button("+", style: .operator) { set_op(Op::Add) }
    }

    ui.end_frame()
    give back true
})
```

### Widget Reference:

```
-- label: display text, no interaction
label(text: word)
label(text: word, style: LabelStyle)
-- LabelStyle: .normal .heading .subheading .display .mono .muted

-- button: clickable, returns true on click
button(text: word) -> bool
button(text: word, style: ButtonStyle) -> bool
button(text: word, width: SizeHint, style: ButtonStyle) -> bool
-- ButtonStyle: .normal .primary .danger .operator .equals .ghost

-- input: text field, returns current value
input(lend mut value: word) -> bool   -- true if value changed
input(lend mut value: word, placeholder: word) -> bool
input(lend mut value: word, InputConfig { placeholder, password, max_len })

-- checkbox
checkbox(label: word, lend mut checked: bool) -> bool   -- true if toggled

-- slider
slider(lend mut value: num, lo: num, hi: num) -> bool

-- dropdown / select
dropdown(lend mut selected: uint, options: List<word>) -> bool

-- image display
image_view(img: Image, size: Vec2)
image_view(img: Image, size: Vec2, fit: ImageFit)
-- ImageFit: .contain .cover .stretch .none

-- spacer
spacer(size: num)       -- fixed space
spacer(.fill)           -- fills remaining space

-- separator
separator()
separator(color: Color)
```

### Layout System:

```
-- Default: vertical flow (column)
label("one")   -- renders at y=0
label("two")   -- renders at y=one.height + padding
label("three") -- renders at y=two.bottom + padding

-- row: horizontal group
row {
    button("A")
    button("B")
    button("C")
}

-- row with config
row(gap: 8.0, align: .center) {
    button("Left")
    spacer(.fill)
    button("Right")
}

-- column: explicit vertical group (for nesting)
column {
    label("Name")
    input(lend mut name)
}

-- column with config
column(gap: 4.0, padding: 12.0) {
    label("Section")
    label("Content here")
}

-- stack: absolute positioning within a fixed area
stack(size: Vec2 { x: 400, y: 300 }) {
    at(Vec2 { x: 10, y: 10 }) { label("top left") }
    at(Vec2 { x: 200, y: 150 }) { label("center") }
}

-- scroll area: scrollable region
scroll(height: 200.0) {
    for each item in long_list {
        label(item)
    }
}

-- SizeHint: how widgets size themselves
-- .auto       — fit content
-- .fill       — fill available space
-- .fixed(n)   — exact pixel size
-- .fraction(f) — fraction of available space (0.0..1.0)
```

### Theme System:

```
-- Themes have a mood (naturally)
shape Theme {
    mood:       mood
    bg:         Color
    bg2:        Color
    surface:    Color
    border:     Color
    text:       Color
    text_muted: Color
    accent:     Color
    danger:     Color
    success:    Color
    font:       Font
    font_mono:  Font
    radius:     num      -- corner radius
    padding:    num      -- default widget padding
    gap:        num      -- default layout gap
    shadow:     bool
}

impl Theme {
    -- Built-in themes
    task default() -> Theme        -- clean dark, mood .focused
    task light() -> Theme          -- clean light, mood .chill
    task terminal() -> Theme       -- green on black, mood .hype
    task alternative() -> Theme    -- deep navy + pink, mood .muv_luv
    task muvluv() -> Theme         -- blood red + black, mood .mono_no_aware

    -- Build custom
    task from_mood(m: mood) -> Theme   -- generates a theme from a mood
    task accent(self, color: Color) -> Theme
}

-- Apply theme to the whole UI
pilot ui = UI::new(win, Theme::alternative())

-- Override theme for a section
with_theme(Theme::terminal()) {
    label("CLASSIFIED OUTPUT")
    label(classified_data)
}
```

### State Management Pattern:

```
-- In immediate mode, YOU hold all state
-- Common pattern: define state shapes outside the loop

shape CalcState {
    display:    word
    operand:    maybe<num>
    operation:  maybe<Op>
    just_result: bool
}

pilot state = CalcState {
    display: "0",
    operand: nobody,
    operation: nobody,
    just_result: false,
}

win.run(|canvas, events| {
    ui.begin_frame(canvas, events)
    draw_calculator(lend mut state, lend mut ui)
    ui.end_frame()
    give back true
})

task draw_calculator(lend mut state: CalcState, lend mut ui: UI) {
    -- all widget calls here, mutate state directly
}
```

### Animation:

```
-- freak-ui has a simple animation system
-- Animations are driven by the frame clock

-- Animated value: smoothly interpolates to target
pilot opacity = ui.animate(target: 1.0, speed: 0.15)
pilot scale   = ui.animate(target: 1.0, speed: 0.2)

-- Use in draw calls
with_opacity(opacity) {
    label("Fading in...")
}

-- Easing functions
ui.animate(target: 1.0, speed: 0.2, easing: .ease_out)
ui.animate(target: 1.0, speed: 0.2, easing: .spring(stiffness: 200, damping: 20))

-- One-shot animation trigger
if button("Click me") {
    ui.trigger("button_pop")
}
pilot pop = ui.tween("button_pop", from: 1.2, to: 1.0, duration: 0.3)
```

---

## THE CALCULATOR APP (Reference Implementation)

This is the target. Build freak-ui until this works.

```
use std::ui::Window
use freak_ui::{UI, Theme, button, label, row, column}

route Op { Add, Sub, Mul, Div }

shape State {
    display:     word
    pending:     maybe<num>
    op:          maybe<Op>
    fresh:       bool
}

task main() {
    pilot win   = Window::open(WindowConfig {
        title: "FREAK Calculator",
        width: 320, height: 480,
        resizable: false,
    })

    pilot state = State { display: "0", pending: nobody, op: nobody, fresh: false }
    pilot ui    = UI::new(win, Theme::alternative())

    win.run(|canvas, events| {
        for each e in events {
            when e { Event::Quit -> give back false   _ -> {} }
        }

        ui.begin_frame(canvas, events)

        column(padding: 16.0, gap: 8.0) {

            label(state.display, style: .display)

            row(gap: 8.0) {
                for each btn in ["C", "±", "%", "÷"] {
                    if button(btn, style: .operator) { handle_op(lend mut state, btn) }
                }
            }
            row(gap: 8.0) {
                for each btn in ["7", "8", "9", "×"] {
                    pilot s = if btn == "×" { .operator } else { .normal }
                    if button(btn, style: s) { handle_input(lend mut state, btn) }
                }
            }
            row(gap: 8.0) {
                for each btn in ["4", "5", "6", "−"] {
                    pilot s = if btn == "−" { .operator } else { .normal }
                    if button(btn, style: s) { handle_input(lend mut state, btn) }
                }
            }
            row(gap: 8.0) {
                for each btn in ["1", "2", "3", "+"] {
                    pilot s = if btn == "+" { .operator } else { .normal }
                    if button(btn, style: s) { handle_input(lend mut state, btn) }
                }
            }
            row(gap: 8.0) {
                if button("0", width: .fraction(0.5), style: .normal) {
                    handle_input(lend mut state, "0")
                }
                if button(".", style: .normal) { handle_input(lend mut state, ".") }
                if button("=", style: .equals) { handle_equals(lend mut state) }
            }
        }

        ui.end_frame()
        give back true
    })
}

task handle_input(lend mut s: State, digit: word) {
    if s.fresh or s.display == "0" {
        s.display = digit
        s.fresh = false
    } else {
        s.display = s.display + digit
    }
}

task handle_op(lend mut s: State, op: word) {
    when op {
        "C"  -> { s.display = "0"; s.pending = nobody; s.op = nobody }
        "±"  -> s.display = (s.display.to_num() or else 0.0 * -1.0).to_word()
        "%"  -> s.display = (s.display.to_num() or else 0.0 / 100.0).to_word()
        "÷"  -> { s.pending = s.display.to_num(); s.op = some(Op::Div); s.fresh = true }
        "×"  -> { s.pending = s.display.to_num(); s.op = some(Op::Mul); s.fresh = true }
        "−"  -> { s.pending = s.display.to_num(); s.op = some(Op::Sub); s.fresh = true }
        "+"  -> { s.pending = s.display.to_num(); s.op = some(Op::Add); s.fresh = true }
        _    -> {}
    }
}

task handle_equals(lend mut s: State) {
    check s.pending {
        nobody -> {}
        got p  -> {
            pilot current = s.display.to_num() or else 0.0
            pilot result = check s.op {
                got Op::Add -> ok(p + current)
                got Op::Sub -> ok(p - current)
                got Op::Mul -> ok(p * current)
                got Op::Div -> if current == 0.0 { err("÷0") } else { ok(p / current) }
                nobody      -> ok(current)
            }
            when result {
                ok(n)  -> s.display = n.to_word_fmt(decimals: 8).trim_end_zeros()
                err(e) -> s.display = e
            }
            s.pending = nobody
            s.op = nobody
            s.fresh = true
        }
    }
}
```

---

## BUILD PLAN — PHASES

### Phase A — std::ui (the floor)
*Goal: open a window on all three platforms and draw a colored rectangle*

- [ ] Define std::ui API types: Window, Canvas, Event, Vec2, Rect, Color, Font, Image
- [ ] Implement C backend interface (freak_ui_platform.h):
  ```c
  freak_ui_handle freak_ui_create(freak_ui_config*);
  freak_ui_events freak_ui_poll(freak_ui_handle);
  freak_ui_canvas freak_ui_begin(freak_ui_handle);
  void            freak_ui_end(freak_ui_handle);
  void            freak_ui_destroy(freak_ui_handle);
  ```
- [ ] Windows implementation (win32_backend.c):
  - [ ] CreateWindowEx + message loop
  - [ ] GDI drawing: FillRect, TextOut, Ellipse, LineTo
  - [ ] Keyboard and mouse event translation
  - [ ] Direct2D path for antialiased drawing (optional upgrade)
- [ ] macOS implementation (cocoa_backend.m):
  - [ ] NSWindow + NSView subclass
  - [ ] CoreGraphics drawing context
  - [ ] NSEvent keyboard/mouse translation
  - [ ] Objective-C bridge via trust-me blocks in FREAK
- [ ] Linux implementation (x11_backend.c):
  - [ ] XCreateWindow + XNextEvent loop
  - [ ] Cairo for 2D drawing
  - [ ] XLib key/button event translation
- [ ] Font loading: platform font APIs (GDI fonts / CTFont / Pango)
- [ ] Image loading: embed stb_image.h (single-header, public domain, easiest)
- [ ] **★ MILESTONE A: window opens, rectangle draws, events fire on all 3 platforms ★**

### Phase B — freak-ui Core (immediate mode engine)
*Goal: the UI state machine that makes immediate mode work*

- [ ] `UI` shape: holds frame state, input state, layout cursor, draw list
- [ ] `begin_frame(canvas, events)` — reset layout, process input
- [ ] `end_frame()` — flush draw list to canvas
- [ ] Layout cursor: tracks current x/y position, available width/height
- [ ] `row { }` — push horizontal layout context, pop on close
- [ ] `column { }` — push vertical layout context, pop on close
- [ ] `SizeHint` resolution: .auto .fill .fixed(n) .fraction(f)
- [ ] Input state tracking: mouse position, buttons down, keys down, last click
- [ ] Hot/active widget tracking (by call order index, not ID)
- [ ] **★ MILESTONE B: layout system works, widgets know their bounds ★**

### Phase C — Core Widgets
*Goal: enough widgets to build the calculator*

- [ ] `label(text, style)` — text rendering with style variants
- [ ] `button(text, style, width)` → bool — click detection, hover state
- [ ] `input(value, config)` → bool — text cursor, keyboard input, selection
- [ ] `spacer(hint)` — empty space
- [ ] `separator()` — horizontal line
- [ ] `scroll(height) { }` — scrollable region with scrollbar
- [ ] **★ MILESTONE C: calculator app runs ★**

### Phase D — Theme System
*Goal: the five built-in themes all work, custom themes work*

- [ ] `Theme` shape with all fields
- [ ] `Theme::default()` — dark, mood .focused
- [ ] `Theme::light()` — light, mood .chill
- [ ] `Theme::terminal()` — green on black, mood .hype
- [ ] `Theme::alternative()` — navy + pink, mood .muv_luv
- [ ] `Theme::muvluv()` — red + black, mood .mono_no_aware
- [ ] `Theme::from_mood(m)` — auto-generate from mood
- [ ] `with_theme(theme) { }` — scoped theme override
- [ ] **★ MILESTONE D: calculator looks good in all 5 themes ★**

### Phase E — Extended Widgets
*Goal: enough to build real apps*

- [ ] `checkbox(label, checked)` → bool
- [ ] `slider(value, lo, hi)` → bool
- [ ] `dropdown(selected, options)` → bool
- [ ] `image_view(image, size, fit)`
- [ ] `stack(size) { at(pos) { } }` — absolute layout
- [ ] `tooltip(text) { }` — hover tooltip wrapper
- [ ] `modal(open) { }` — overlay dialog
- [ ] `tabs(selected, names) { }` — tabbed container
- [ ] `menu_bar { menu("File") { item("Open") ... } }` — top menu bar

### Phase F — Animation
*Goal: smooth, springy UI*

- [ ] Frame clock: `ui.delta_time() -> num` (seconds since last frame)
- [ ] `ui.animate(target, speed, easing)` — smooth value interpolation
- [ ] `ui.trigger(name)` / `ui.tween(name, from, to, duration)` — one-shot animations
- [ ] Easing functions: .linear .ease_in .ease_out .ease_in_out .spring
- [ ] Built-in hover animations on all interactive widgets

### Phase G — Accessibility + Polish
*Goal: usable by real people*

- [ ] Keyboard navigation (Tab to next widget, Enter to activate)
- [ ] Screen reader support (Windows: MSAA / macOS: NSAccessibility / Linux: AT-SPI)
- [ ] High-DPI / retina display support (scale factor from OS)
- [ ] System font fallback (use system default if custom font fails to load)
- [ ] Clipboard support (Ctrl+C/V in input widgets)
- [ ] Drag and drop (connect to std::ui FileDrop event)

---

## MILESTONES SUMMARY

```
[ ] MA — std::ui: window + drawing on all 3 platforms
[ ] MB — freak-ui: layout engine working
[ ] MC — freak-ui: calculator app compiles and runs     ← first real app
[ ] MD — freak-ui: all 5 themes working
[ ] ME — freak-ui: extended widget set done
[ ] MF — freak-ui: animation system
[ ] MG — freak-ui: accessibility + polish
```

---

## WHAT TO BUILD FIRST

The critical path to the calculator app is:

  Phase A (std::ui Windows only) →
  Phase B (layout engine) →
  Phase C (label + button only) →
  Calculator runs on Windows

Do macOS and Linux after the calculator works on Windows.
The platform abstraction layer makes this straightforward —
you're just writing a second and third implementation of the same C interface.

Start with Windows because:
- You're already on Windows (the hello.exe proves it)
- Win32 is well-documented and has no extra dependencies
- GDI is built into every Windows install
- Direct2D is optional and can be added later

---

## DEPENDENCY SUMMARY

std::ui dependencies:
- Windows: user32, gdi32 (built in) + optional d2d1
- macOS: Cocoa.framework, CoreGraphics.framework (built in)
- Linux: libX11, libcairo (common, apt install libx11-dev libcairo2-dev)
- All platforms: stb_image.h (single header, embed in repo, no install)

freak-ui dependencies:
- std::ui (above)
- Nothing else. Zero external dependencies.

---

## PACKAGE NAME AND HANGAR ENTRY

```toml
[unit]
name    = "freak-ui"
version = "0.1.0"
author  = "FREAK Core Team"
edition = "alternative-4"

[build]
links   = ["user32", "gdi32"]   -- Windows
         ["Cocoa", "CoreGraphics"]  -- macOS
         ["X11", "cairo"]           -- Linux
```

---

## END OF freak-ui PLAN

Target: calculator app in FREAK with freak-ui.
First milestone: window opens on Windows.
Final milestone: same app runs on Windows, Mac, and Linux with one codebase.
