#include "freak_runtime.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <time.h>

/* runtime bootstrap globals (set by generated main) */
int freak_argc = 0;
char** freak_argv = NULL;

/* ------------------------------------------------------------------ */
/*  word helpers                                                      */
/* ------------------------------------------------------------------ */

freak_word freak_word_lit(const char* s) {
    size_t len = strlen(s);
    freak_word w;
    w.data       = s;
    w.length     = len;
    w.char_count = len;   /* ASCII assumption for now */
    w.heap       = false;
    return w;
}

freak_word freak_word_own(char* s, size_t len) {
    freak_word w;
    w.data       = s;
    w.length     = len;
    w.char_count = len;
    w.heap       = true;
    return w;
}

freak_word freak_word_concat(freak_word a, freak_word b) {
    size_t total = a.length + b.length;
    char* buf = (char*)malloc(total + 1);
    if (!buf) { fprintf(stderr, "FREAK: out of memory\n"); exit(1); }
    memcpy(buf, a.data, a.length);
    memcpy(buf + a.length, b.data, b.length);
    buf[total] = '\0';
    return freak_word_own(buf, total);
}

bool freak_word_eq(freak_word a, freak_word b) {
    if (a.length != b.length) return false;
    return memcmp(a.data, b.data, a.length) == 0;
}

const char* freak_word_to_cstr(freak_word w) {
    /* Literals are NUL-terminated by the compiler; heap strings are
       NUL-terminated by freak_word_own / freak_interpolate. */
    return w.data;
}

/* ------------------------------------------------------------------ */
/*  Conversions to word                                               */
/* ------------------------------------------------------------------ */

freak_word freak_word_from_int(int64_t n) {
    char* buf = (char*)malloc(32);
    if (!buf) { fprintf(stderr, "FREAK: out of memory\n"); exit(1); }
    int len = snprintf(buf, 32, "%lld", (long long)n);
    if (len < 0) len = 0;
    return freak_word_own(buf, (size_t)len);
}

freak_word freak_word_from_double(double n) {
    char* buf = (char*)malloc(64);
    if (!buf) { fprintf(stderr, "FREAK: out of memory\n"); exit(1); }
    int len = snprintf(buf, 64, "%g", n);
    if (len < 0) len = 0;
    return freak_word_own(buf, (size_t)len);
}

freak_word freak_word_from_bool(bool b) {
    return freak_word_lit(b ? "true" : "false");
}

/* ------------------------------------------------------------------ */
/*  Interpolation                                                     */
/* ------------------------------------------------------------------ */

freak_word freak_interpolate(const char* fmt, ...) {
    va_list args, args_copy;
    va_start(args, fmt);
    va_copy(args_copy, args);

    /* First pass: determine required size. */
    int needed = vsnprintf(NULL, 0, fmt, args);
    va_end(args);

    if (needed < 0) {
        va_end(args_copy);
        return freak_word_lit("");
    }

    char* buf = (char*)malloc((size_t)needed + 1);
    if (!buf) { fprintf(stderr, "FREAK: out of memory\n"); exit(1); }

    vsnprintf(buf, (size_t)needed + 1, fmt, args_copy);
    va_end(args_copy);

    return freak_word_own(buf, (size_t)needed);
}

/* ------------------------------------------------------------------ */
/*  I/O                                                               */
/* ------------------------------------------------------------------ */

void freak_say(freak_word msg) {
    fwrite(msg.data, 1, msg.length, stdout);
    fputc('\n', stdout);
    fflush(stdout);
}

void freak_say_err(freak_word msg) {
    fwrite(msg.data, 1, msg.length, stderr);
    fputc('\n', stderr);
}

freak_word freak_ask(freak_word prompt) {
    /* Print the prompt (no newline). */
    fwrite(prompt.data, 1, prompt.length, stdout);
    fflush(stdout);

    char* line = NULL;
    size_t cap  = 0;
    size_t len  = 0;
    int    ch;
    while ((ch = fgetc(stdin)) != EOF && ch != '\n') {
        if (len + 1 >= cap) {
            cap = cap ? cap * 2 : 128;
            line = (char*)realloc(line, cap);
            if (!line) { fprintf(stderr, "FREAK: out of memory\n"); exit(1); }
        }
        line[len++] = (char)ch;
    }
    if (!line) {
        line = (char*)malloc(1);
        if (!line) { fprintf(stderr, "FREAK: out of memory\n"); exit(1); }
    }
    line[len] = '\0';
    return freak_word_own(line, len);
}

/* ------------------------------------------------------------------ */
/*  Panic                                                             */
/* ------------------------------------------------------------------ */

_Noreturn void freak_panic(freak_word msg) {
    fprintf(stderr, "PANIC: ");
    fwrite(msg.data, 1, msg.length, stderr);
    fputc('\n', stderr);
    exit(1);
}

/* ------------------------------------------------------------------ */
/*  std::fs — file I/O                                                */
/* ------------------------------------------------------------------ */

freak_word freak_fs_read(freak_word path) {
    const char* p = freak_word_to_cstr(path);
    FILE* f = fopen(p, "rb");
    if (!f) {
        fprintf(stderr, "FREAK: cannot open file '%s': %s\n", p, strerror(errno));
        exit(1);
    }
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* buf = (char*)malloc((size_t)size + 1);
    if (!buf) { fprintf(stderr, "FREAK: out of memory\n"); fclose(f); exit(1); }
    size_t read = fread(buf, 1, (size_t)size, f);
    fclose(f);
    buf[read] = '\0';
    return freak_word_own(buf, read);
}

void freak_fs_write(freak_word path, freak_word content) {
    const char* p = freak_word_to_cstr(path);
    FILE* f = fopen(p, "wb");
    if (!f) {
        fprintf(stderr, "FREAK: cannot write file '%s': %s\n", p, strerror(errno));
        exit(1);
    }
    fwrite(content.data, 1, content.length, f);
    fclose(f);
}

/* ------------------------------------------------------------------ */
/*  Numeric helpers                                                   */
/* ------------------------------------------------------------------ */

int64_t freak_abs_int(int64_t x) {
    return x < 0 ? -x : x;
}

double freak_abs_double(double x) {
    return x < 0.0 ? -x : x;
}

int64_t freak_clamp_int(int64_t x, int64_t lo, int64_t hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

double freak_clamp_double(double x, double lo, double hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

int64_t freak_pow_int(int64_t base, int64_t exp) {
    int64_t result = 1;
    if (exp < 0) return 0;  /* integer pow with neg exp → 0 */
    while (exp > 0) {
        if (exp & 1) result *= base;
        base *= base;
        exp >>= 1;
    }
    return result;
}

/* ------------------------------------------------------------------ */
/*  String methods                                                    */
/* ------------------------------------------------------------------ */

#include <ctype.h>

int64_t freak_word_length(freak_word w) {
    return (int64_t)w.char_count;
}

freak_word freak_word_to_upper(freak_word w) {
    char* buf = (char*)malloc(w.length + 1);
    if (!buf) { fprintf(stderr, "FREAK: out of memory\n"); exit(1); }
    for (size_t i = 0; i < w.length; i++) {
        buf[i] = (char)toupper((unsigned char)w.data[i]);
    }
    buf[w.length] = '\0';
    return freak_word_own(buf, w.length);
}

freak_word freak_word_to_lower(freak_word w) {
    char* buf = (char*)malloc(w.length + 1);
    if (!buf) { fprintf(stderr, "FREAK: out of memory\n"); exit(1); }
    for (size_t i = 0; i < w.length; i++) {
        buf[i] = (char)tolower((unsigned char)w.data[i]);
    }
    buf[w.length] = '\0';
    return freak_word_own(buf, w.length);
}

bool freak_word_contains(freak_word haystack, freak_word needle) {
    if (needle.length == 0) return true;
    if (needle.length > haystack.length) return false;
    for (size_t i = 0; i <= haystack.length - needle.length; i++) {
        if (memcmp(haystack.data + i, needle.data, needle.length) == 0) {
            return true;
        }
    }
    return false;
}

bool freak_word_starts_with(freak_word w, freak_word prefix) {
    if (prefix.length > w.length) return false;
    return memcmp(w.data, prefix.data, prefix.length) == 0;
}

bool freak_word_ends_with(freak_word w, freak_word suffix) {
    if (suffix.length > w.length) return false;
    return memcmp(w.data + w.length - suffix.length, suffix.data, suffix.length) == 0;
}

freak_word freak_word_trim(freak_word w) {
    size_t start = 0;
    while (start < w.length && isspace((unsigned char)w.data[start])) start++;
    size_t end = w.length;
    while (end > start && isspace((unsigned char)w.data[end - 1])) end--;
    size_t new_len = end - start;
    char* buf = (char*)malloc(new_len + 1);
    if (!buf) { fprintf(stderr, "FREAK: out of memory\n"); exit(1); }
    memcpy(buf, w.data + start, new_len);
    buf[new_len] = '\0';
    return freak_word_own(buf, new_len);
}

freak_word freak_word_replace(freak_word w, freak_word old_s, freak_word new_s) {
    if (old_s.length == 0) return w;
    /* Count occurrences */
    size_t count = 0;
    for (size_t i = 0; i <= w.length - old_s.length; i++) {
        if (memcmp(w.data + i, old_s.data, old_s.length) == 0) {
            count++;
            i += old_s.length - 1;
        }
    }
    if (count == 0) {
        char* buf = (char*)malloc(w.length + 1);
        if (!buf) { fprintf(stderr, "FREAK: out of memory\n"); exit(1); }
        memcpy(buf, w.data, w.length);
        buf[w.length] = '\0';
        return freak_word_own(buf, w.length);
    }
    size_t new_len = w.length + count * (new_s.length - old_s.length);
    char* buf = (char*)malloc(new_len + 1);
    if (!buf) { fprintf(stderr, "FREAK: out of memory\n"); exit(1); }
    size_t j = 0;
    for (size_t i = 0; i < w.length; ) {
        if (i + old_s.length <= w.length &&
            memcmp(w.data + i, old_s.data, old_s.length) == 0) {
            memcpy(buf + j, new_s.data, new_s.length);
            j += new_s.length;
            i += old_s.length;
        } else {
            buf[j++] = w.data[i++];
        }
    }
    buf[new_len] = '\0';
    return freak_word_own(buf, new_len);
}

freak_word freak_word_char_at(freak_word w, int64_t index) {
    if (index < 0 || (size_t)index >= w.length) {
        return freak_word_lit("");
    }
    char* buf = (char*)malloc(2);
    if (!buf) { fprintf(stderr, "FREAK: out of memory\n"); exit(1); }
    buf[0] = w.data[index];
    buf[1] = '\0';
    return freak_word_own(buf, 1);
}

int64_t freak_word_to_int(freak_word w) {
    return strtoll(w.data, NULL, 10);
}

double freak_word_to_num(freak_word w) {
    return strtod(w.data, NULL);
}

/* ------------------------------------------------------------------ */
/*  std::process                                                      */
/* ------------------------------------------------------------------ */

freak_process_output freak_process_run(freak_word cmd, void* args) {
    (void)args;
    freak_process_output out;
    out.out = freak_word_lit("");
    out.err = freak_word_lit("process::run not implemented yet");
    out.exit_code = -1;
    out.success = false;
    (void)cmd;
    return out;
}

freak_process_handle freak_process_spawn(freak_word cmd, void* args) {
    (void)cmd;
    (void)args;
    freak_process_handle h;
    h.pid = 0;
    return h;
}

uint64_t freak_process_pid(void) {
#if defined(_WIN32)
    return 0;
#else
    return (uint64_t)0;
#endif
}

void freak_process_exit(int64_t code) {
    exit((int)code);
}

freak_maybe_word freak_process_env_var(freak_word name) {
    freak_maybe_word r;
    const char* key = freak_word_to_cstr(name);
    const char* val = key ? getenv(key) : NULL;
    if (val) {
        r.has_value = true;
        r.value = freak_word_lit(val);
    } else {
        r.has_value = false;
        r.value = freak_word_lit("");
    }
    return r;
}

void freak_process_set_env(freak_word name, freak_word val) {
    (void)name;
    (void)val;
    /* Minimal cross-platform stub: no-op for now. */
}

void* freak_process_args(void) {
    return (void*)freak_argv;
}

int64_t freak_process_wait(freak_process_handle p) {
    (void)p;
    return -1;
}

bool freak_process_kill(freak_process_handle p) {
    (void)p;
    return false;
}

/* ------------------------------------------------------------------ */
/*  std::thread                                                       */
/* ------------------------------------------------------------------ */

freak_thread_handle freak_thread_spawn(freak_closure f) {
    (void)f;
    freak_thread_handle h;
    h.id = 0;
    h.finished = true;
    return h;
}

uint64_t freak_thread_current_id(void) {
    return 0;
}

void freak_thread_yield_now(void) {
    /* Minimal stub: no scheduler hint available without platform APIs. */
}

uint64_t freak_thread_available_parallelism(void) {
    return 1;
}

bool freak_thread_join(freak_thread_handle h) {
    (void)h;
    return true;
}

uint64_t freak_thread_id(freak_thread_handle h) {
    return h.id;
}

bool freak_thread_is_finished(freak_thread_handle h) {
    return h.finished;
}

int64_t freak_atomic_int_load(freak_atomic_int* a) {
    return a ? a->value : 0;
}

void freak_atomic_int_store(freak_atomic_int* a, int64_t v) {
    if (a) a->value = v;
}

int64_t freak_atomic_int_fetch_add(freak_atomic_int* a, int64_t n) {
    if (!a) return 0;
    int64_t old = a->value;
    a->value += n;
    return old;
}

bool freak_atomic_int_compare_swap(freak_atomic_int* a, int64_t old_v, int64_t new_v) {
    if (!a) return false;
    if (a->value == old_v) {
        a->value = new_v;
        return true;
    }
    return false;
}

bool freak_atomic_bool_load(freak_atomic_bool* a) {
    return a ? a->value : false;
}

void freak_atomic_bool_store(freak_atomic_bool* a, bool v) {
    if (a) a->value = v;
}

bool freak_atomic_bool_flip(freak_atomic_bool* a) {
    if (!a) return false;
    a->value = !a->value;
    return a->value;
}

/* ------------------------------------------------------------------ */
/*  std::bytes                                                        */
/* ------------------------------------------------------------------ */

static void freak_bytes_ensure_capacity(freak_byte_buffer* b, size_t needed) {
    if (!b) return;
    if (b->capacity >= needed) return;
    size_t new_cap = b->capacity ? b->capacity : 16;
    while (new_cap < needed) new_cap *= 2;
    uint8_t* n = (uint8_t*)realloc(b->data, new_cap);
    if (!n) {
        fprintf(stderr, "FREAK: out of memory\n");
        exit(1);
    }
    b->data = n;
    b->capacity = new_cap;
}

freak_byte_buffer freak_bytes_new(void) {
    freak_byte_buffer b;
    b.data = NULL;
    b.length = 0;
    b.capacity = 0;
    b.cursor = 0;
    return b;
}

freak_byte_buffer freak_bytes_from(void* data) {
    (void)data;
    return freak_bytes_new();
}

void freak_bytes_write_byte(freak_byte_buffer* b, uint8_t v) {
    if (!b) return;
    freak_bytes_ensure_capacity(b, b->length + 1);
    b->data[b->length++] = v;
}

void freak_bytes_write_int(freak_byte_buffer* b, int64_t v) {
    if (!b) return;
    for (int i = 0; i < 8; i++) {
        freak_bytes_write_byte(b, (uint8_t)((uint64_t)v >> (i * 8)));
    }
}

void freak_bytes_write_int_be(freak_byte_buffer* b, int64_t v) {
    if (!b) return;
    for (int i = 7; i >= 0; i--) {
        freak_bytes_write_byte(b, (uint8_t)((uint64_t)v >> (i * 8)));
    }
}

void freak_bytes_write_word(freak_byte_buffer* b, freak_word s) {
    if (!b) return;
    freak_bytes_write_bytes(b, (const uint8_t*)s.data, s.length);
}

void freak_bytes_write_bytes(freak_byte_buffer* b, const uint8_t* data, size_t n) {
    if (!b || !data || n == 0) return;
    freak_bytes_ensure_capacity(b, b->length + n);
    memcpy(b->data + b->length, data, n);
    b->length += n;
}

freak_maybe_int freak_bytes_read_byte(freak_byte_buffer* b) {
    freak_maybe_int r;
    if (!b || b->cursor >= b->length) {
        r.has_value = false;
        r.value = 0;
        return r;
    }
    r.has_value = true;
    r.value = (int64_t)b->data[b->cursor++];
    return r;
}

freak_maybe_int freak_bytes_read_int(freak_byte_buffer* b) {
    freak_maybe_int r;
    if (!b || b->cursor + 8 > b->length) {
        r.has_value = false;
        r.value = 0;
        return r;
    }
    uint64_t acc = 0;
    for (int i = 0; i < 8; i++) {
        acc |= ((uint64_t)b->data[b->cursor++]) << (i * 8);
    }
    r.has_value = true;
    r.value = (int64_t)acc;
    return r;
}

freak_maybe_word freak_bytes_read_word(freak_byte_buffer* b, uint64_t len) {
    freak_maybe_word r;
    if (!b || b->cursor + (size_t)len > b->length) {
        r.has_value = false;
        r.value = freak_word_lit("");
        return r;
    }
    char* s = (char*)malloc((size_t)len + 1);
    if (!s) {
        fprintf(stderr, "FREAK: out of memory\n");
        exit(1);
    }
    memcpy(s, b->data + b->cursor, (size_t)len);
    s[len] = '\0';
    b->cursor += (size_t)len;
    r.has_value = true;
    r.value = freak_word_own(s, (size_t)len);
    return r;
}

void freak_bytes_seek(freak_byte_buffer* b, uint64_t pos) {
    if (!b) return;
    if (pos > b->length) pos = b->length;
    b->cursor = (size_t)pos;
}

uint64_t freak_bytes_position(const freak_byte_buffer* b) {
    return b ? (uint64_t)b->cursor : 0;
}

uint64_t freak_bytes_length(const freak_byte_buffer* b) {
    return b ? (uint64_t)b->length : 0;
}

void* freak_bytes_to_list(const freak_byte_buffer* b) {
    (void)b;
    return NULL;
}

freak_result_word_word freak_bytes_to_word(const freak_byte_buffer* b) {
    freak_result_word_word r;
    if (!b) {
        r.is_ok = false;
        r.data.err_val = freak_word_lit("null byte buffer");
        return r;
    }
    char* s = (char*)malloc(b->length + 1);
    if (!s) {
        fprintf(stderr, "FREAK: out of memory\n");
        exit(1);
    }
    memcpy(s, b->data, b->length);
    s[b->length] = '\0';
    r.is_ok = true;
    r.data.ok_val = freak_word_own(s, b->length);
    return r;
}
