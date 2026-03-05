#pragma once

/*
 * FREAK Lite Runtime — C runtime support for the FREAK→C transpiler.
 *
 * Every emitted .c file includes this header.  The implementation lives in
 * freak_runtime.c which must be compiled and linked alongside the generated
 * code.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* ------------------------------------------------------------------ */
/*  Runtime bootstrap globals                                         */
/* ------------------------------------------------------------------ */

/* Populated by generated main() before freak_main() runs. */
extern int freak_argc;
extern char** freak_argv;

/* ------------------------------------------------------------------ */
/*  word type (UTF-8 string)                                          */
/* ------------------------------------------------------------------ */

typedef struct {
    const char* data;
    size_t length;       /* byte length   */
    size_t char_count;   /* codepoint count (== length for ASCII) */
    bool   heap;         /* true if data was malloc'd and must be freed */
} freak_word;

/* Construct from a C string literal (no copy, points into rodata). */
freak_word freak_word_lit(const char* s);

/* Construct from a heap-allocated buffer (takes ownership). */
freak_word freak_word_own(char* s, size_t len);

/* Concatenate two words — allocates. */
freak_word freak_word_concat(freak_word a, freak_word b);

/* Equality test (byte-wise). */
bool freak_word_eq(freak_word a, freak_word b);

/* Get a NUL-terminated C string.  For literals this is the original
   pointer; for heap strings the data is already NUL-terminated. */
const char* freak_word_to_cstr(freak_word w);

/* Conversions to word. */
freak_word freak_word_from_int(int64_t n);
freak_word freak_word_from_double(double n);
freak_word freak_word_from_bool(bool b);

/* printf-style interpolation — returns a heap-allocated word. */
freak_word freak_interpolate(const char* fmt, ...);

/* ------------------------------------------------------------------ */
/*  I/O                                                               */
/* ------------------------------------------------------------------ */

/* Print word to stdout with trailing newline. */
void freak_say(freak_word msg);

/* Print word to stderr with trailing newline. */
void freak_say_err(freak_word msg);

/* Prompt on stdout, read a line from stdin, return as word. */
freak_word freak_ask(freak_word prompt);

/* ------------------------------------------------------------------ */
/*  Panic                                                             */
/* ------------------------------------------------------------------ */

/* Print message to stderr and exit(1). */
_Noreturn void freak_panic(freak_word msg);

/* ------------------------------------------------------------------ */
/*  std::fs — file I/O                                                */
/* ------------------------------------------------------------------ */

/* Read entire file contents as a word. Panics on failure. */
freak_word freak_fs_read(freak_word path);

/* Write word contents to a file. Panics on failure. */
void freak_fs_write(freak_word path, freak_word content);

/* ------------------------------------------------------------------ */
/*  Numeric helpers                                                   */
/* ------------------------------------------------------------------ */

int64_t freak_abs_int(int64_t x);
double  freak_abs_double(double x);
int64_t freak_clamp_int(int64_t x, int64_t lo, int64_t hi);
double  freak_clamp_double(double x, double lo, double hi);
int64_t freak_pow_int(int64_t base, int64_t exp);

/* ------------------------------------------------------------------ */
/*  Closures                                                          */
/* ------------------------------------------------------------------ */

/* A closure is a function pointer + captured environment pointer.
   The emitter generates typed wrapper structs per closure signature,
   but the generic form is used for storage/passing. */
typedef struct {
    void* fn;    /* pointer to the generated static function */
    void* env;   /* pointer to the generated capture struct  */
} freak_closure;

/* ------------------------------------------------------------------ */
/*  Maybe<T> and Result<T,E> generator macros                         */
/* ------------------------------------------------------------------ */

/* Generate a maybe type for a given C type.
   Usage: FREAK_MAYBE_DECL(int64_t, int)
   Produces: typedef struct { bool has_value; int64_t value; } freak_maybe_int; */
#define FREAK_MAYBE_DECL(CType, Suffix) \
    typedef struct { \
        bool has_value; \
        CType value; \
    } freak_maybe_##Suffix

/* Generate a result type for given ok/err C types.
   Usage: FREAK_RESULT_DECL(int64_t, freak_word, int_word)
   Produces: typedef struct { bool is_ok; union { int64_t ok_val; freak_word err_val; } data; } freak_result_int_word; */
#define FREAK_RESULT_DECL(OkType, ErrType, Suffix) \
    typedef struct { \
        bool is_ok; \
        union { OkType ok_val; ErrType err_val; } data; \
    } freak_result_##Suffix

/* Pre-generated common maybe types */
FREAK_MAYBE_DECL(int64_t,    int);
FREAK_MAYBE_DECL(double,     num);
FREAK_MAYBE_DECL(freak_word, word);
FREAK_MAYBE_DECL(bool,       bool);

/* Pre-generated common result types (error is always freak_word) */
FREAK_RESULT_DECL(int64_t,    freak_word, int_word);
FREAK_RESULT_DECL(double,     freak_word, num_word);
FREAK_RESULT_DECL(freak_word, freak_word, word_word);
FREAK_RESULT_DECL(bool,       freak_word, bool_word);

/* ------------------------------------------------------------------ */
/*  String methods                                                    */
/* ------------------------------------------------------------------ */

/* Length in characters (codepoints). */
int64_t freak_word_length(freak_word w);

/* Case conversion — allocates new word. */
freak_word freak_word_to_upper(freak_word w);
freak_word freak_word_to_lower(freak_word w);

/* Substring tests. */
bool freak_word_contains(freak_word haystack, freak_word needle);
bool freak_word_starts_with(freak_word w, freak_word prefix);
bool freak_word_ends_with(freak_word w, freak_word suffix);

/* Trim whitespace from both ends — allocates. */
freak_word freak_word_trim(freak_word w);

/* Replace all occurrences of old with new — allocates. */
freak_word freak_word_replace(freak_word w, freak_word old_s, freak_word new_s);

/* Get character at index (0-based) as a single-char word. */
freak_word freak_word_char_at(freak_word w, int64_t index);

/* Conversions from word to number. */
int64_t freak_word_to_int(freak_word w);
double  freak_word_to_num(freak_word w);

/* ------------------------------------------------------------------ */
/*  std::process                                                      */
/* ------------------------------------------------------------------ */

typedef struct {
    freak_word out;
    freak_word err;
    int64_t exit_code;
    bool success;
} freak_process_output;

typedef struct {
    uint64_t pid;
} freak_process_handle;

/* run/spawn/process metadata */
freak_process_output freak_process_run(freak_word cmd, void* args /* TODO: list<word> */);
freak_process_handle freak_process_spawn(freak_word cmd, void* args /* TODO: list<word> */);
uint64_t freak_process_pid(void);
void freak_process_exit(int64_t code);
freak_maybe_word freak_process_env_var(freak_word name);
void freak_process_set_env(freak_word name, freak_word val);
void* freak_process_args(void); /* TODO: list<word> */

/* process handle methods */
int64_t freak_process_wait(freak_process_handle p);
bool freak_process_kill(freak_process_handle p);

/* ------------------------------------------------------------------ */
/*  std::thread                                                       */
/* ------------------------------------------------------------------ */

typedef struct {
    uint64_t id;
    bool finished;
} freak_thread_handle;

/* raw thread primitives */
freak_thread_handle freak_thread_spawn(freak_closure f);
uint64_t freak_thread_current_id(void);
void freak_thread_yield_now(void);
uint64_t freak_thread_available_parallelism(void);

/* thread handle methods */
bool freak_thread_join(freak_thread_handle h);
uint64_t freak_thread_id(freak_thread_handle h);
bool freak_thread_is_finished(freak_thread_handle h);

/* simple atomics */
typedef struct { volatile int64_t value; } freak_atomic_int;
typedef struct { volatile bool value; } freak_atomic_bool;

int64_t freak_atomic_int_load(freak_atomic_int* a);
void freak_atomic_int_store(freak_atomic_int* a, int64_t v);
int64_t freak_atomic_int_fetch_add(freak_atomic_int* a, int64_t n);
bool freak_atomic_int_compare_swap(freak_atomic_int* a, int64_t old_v, int64_t new_v);

bool freak_atomic_bool_load(freak_atomic_bool* a);
void freak_atomic_bool_store(freak_atomic_bool* a, bool v);
bool freak_atomic_bool_flip(freak_atomic_bool* a);

/* ------------------------------------------------------------------ */
/*  std::bytes                                                        */
/* ------------------------------------------------------------------ */

typedef struct {
    uint8_t* data;
    size_t length;
    size_t capacity;
    size_t cursor;
} freak_byte_buffer;

freak_byte_buffer freak_bytes_new(void);
freak_byte_buffer freak_bytes_from(void* data /* TODO: list<tiny> */);

void freak_bytes_write_byte(freak_byte_buffer* b, uint8_t v);
void freak_bytes_write_int(freak_byte_buffer* b, int64_t v);
void freak_bytes_write_int_be(freak_byte_buffer* b, int64_t v);
void freak_bytes_write_word(freak_byte_buffer* b, freak_word s);
void freak_bytes_write_bytes(freak_byte_buffer* b, const uint8_t* data, size_t n);

freak_maybe_int freak_bytes_read_byte(freak_byte_buffer* b);
freak_maybe_int freak_bytes_read_int(freak_byte_buffer* b);
freak_maybe_word freak_bytes_read_word(freak_byte_buffer* b, uint64_t len);

void freak_bytes_seek(freak_byte_buffer* b, uint64_t pos);
uint64_t freak_bytes_position(const freak_byte_buffer* b);
uint64_t freak_bytes_length(const freak_byte_buffer* b);

void* freak_bytes_to_list(const freak_byte_buffer* b); /* TODO: list<tiny> */
freak_result_word_word freak_bytes_to_word(const freak_byte_buffer* b);
